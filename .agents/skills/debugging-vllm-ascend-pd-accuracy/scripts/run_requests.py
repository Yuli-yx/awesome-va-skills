#!/usr/bin/env python3
"""等待 endpoint 就绪并执行确定性 OpenAI-compatible 请求。"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("缺少 PyYAML，请使用项目 uv 环境安装") from exc


def load_case(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("case 顶层必须是 mapping")
    request, endpoints = data.get("request"), data.get("endpoints")
    if not isinstance(request, dict) or not isinstance(endpoints, list) or not endpoints:
        raise ValueError("case 必须包含 request mapping 和非空 endpoints")
    if request.get("method", "POST").upper() != "POST":
        raise ValueError("当前只支持 POST 推理请求")
    if not isinstance(request.get("json"), dict):
        raise ValueError("request.json 必须是 mapping")
    if "temperature" not in request["json"]:
        raise ValueError("确定性诊断必须显式设置 temperature，建议为 0")
    for endpoint in endpoints:
        if not isinstance(endpoint, dict) or not endpoint.get("name") or not endpoint.get("url"):
            raise ValueError("每个 endpoint 必须包含 name 和 url")
    return data


def no_proxy_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def request_once(opener, method: str, url: str, headers: dict[str, str], body: bytes | None, timeout: float):
    started = time.monotonic()
    request = urllib.request.Request(url=url, method=method, headers=headers, data=body)
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read(), None, time.monotonic() - started
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read(), None, time.monotonic() - started
    except Exception as exc:
        return None, {}, b"", f"{type(exc).__name__}: {exc}", time.monotonic() - started


def endpoint_ready(opener, base_url: str, paths: list[str], timeout: float) -> tuple[bool, str]:
    messages = []
    for path in paths:
        status, _, body, error, _ = request_once(opener, "GET", join_url(base_url, path), {}, None, timeout)
        message = f"{path}: status={status} error={error} body={body[:120]!r}"
        messages.append(message)
        if status is not None and 200 <= status < 300:
            return True, message
    return False, "; ".join(messages)


def wait_all_ready(case: dict[str, Any], opener) -> None:
    experiments = case.get("experiments") or {}
    timeout = float(experiments.get("readiness_timeout_seconds", 900))
    interval = float(experiments.get("readiness_interval_seconds", 5))
    paths = list(experiments.get("readiness_paths") or ["/health", "/v1/models"])
    deadline = time.monotonic() + timeout
    stable = {str(endpoint["name"]): 0 for endpoint in case["endpoints"]}
    last = {}
    while time.monotonic() < deadline:
        all_stable = True
        for endpoint in case["endpoints"]:
            name = str(endpoint["name"])
            ready, message = endpoint_ready(
                opener, str(endpoint["url"]), list(endpoint.get("readiness_paths") or paths), min(interval, 10)
            )
            last[name] = message
            stable[name] = stable[name] + 1 if ready else 0
            if stable[name] < 2:
                all_stable = False
        if all_stable:
            return
        time.sleep(interval)
    raise TimeoutError(f"endpoint 未在 {timeout}s 内连续两次就绪：{last}")


def decode_body(payload: bytes) -> tuple[Any | None, str]:
    text = payload.decode("utf-8", errors="replace")
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def run(case: dict[str, Any], output: Path, ready_only: bool) -> None:
    opener = no_proxy_opener()
    wait_all_ready(case, opener)
    if ready_only:
        print("所有 endpoint 已连续两次就绪；未发送推理请求。")
        return

    request = case["request"]
    method = str(request.get("method", "POST")).upper()
    path = str(request.get("path", "/v1/completions"))
    headers = {str(key): str(value) for key, value in (request.get("headers") or {}).items()}
    headers.setdefault("Content-Type", "application/json")
    token_env = request.get("auth_token_env")
    if token_env:
        token = os.environ.get(str(token_env))
        if token is None:
            raise ValueError(f"认证环境变量 {token_env} 未设置")
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(request["json"], ensure_ascii=False).encode("utf-8")
    repeats = int(request.get("repeats", 3))
    timeout = float(request.get("timeout_seconds", 300))
    if repeats < 1:
        raise ValueError("request.repeats 必须大于 0")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for endpoint in case["endpoints"]:
            url = join_url(str(endpoint["url"]), path)
            for iteration in range(1, repeats + 1):
                status, response_headers, payload, error, elapsed = request_once(
                    opener, method, url, headers, body, timeout
                )
                parsed, raw_text = decode_body(payload)
                record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "case": case.get("name"),
                    "endpoint": endpoint["name"],
                    "url": url,
                    "iteration": iteration,
                    "http_status": status,
                    "elapsed_seconds": round(elapsed, 6),
                    "content_type": response_headers.get("Content-Type"),
                    "error": error,
                    "response": parsed,
                    "raw_response": None if parsed is not None else raw_text,
                }
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                stream.flush()
                print(f"{endpoint['name']} iteration={iteration} status={status} elapsed={elapsed:.3f}s error={error}")
                if error or status is None or not 200 <= status < 300:
                    raise RuntimeError("推理请求失败，已停止后续请求")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ready-only", action="store_true", help="只等待就绪，不发送推理请求")
    args = parser.parse_args()
    run(load_case(args.case), args.output, args.ready_only)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, TimeoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
