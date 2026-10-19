#!/usr/bin/env python3
"""安全地探测或精确重启 inventory 中指定的 PD 容器。"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import dataclasses
import json
import os
import re
import shlex
import sys
import time
from pathlib import Path
from typing import Any

try:
    import paramiko
except ImportError as exc:
    raise SystemExit("缺少 paramiko，请使用项目 uv 环境安装") from exc
try:
    import yaml
except ImportError as exc:
    raise SystemExit("缺少 PyYAML，请使用项目 uv 环境安装") from exc

CONTAINER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


@dataclasses.dataclass(frozen=True)
class HostSpec:
    name: str
    host: str
    user: str
    port: int = 22
    password_env: str | None = None
    key_file: str | None = None
    role: str | None = None
    endpoint: str | None = None


def load_inventory(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("inventory 顶层必须是 mapping")
    container = data.get("container")
    if not isinstance(container, str) or not CONTAINER_RE.fullmatch(container):
        raise ValueError("container 必须是无通配符的精确容器名")
    hosts = data.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        raise ValueError("inventory.hosts 必须是非空列表")
    names: set[str] = set()
    for item in hosts:
        if not isinstance(item, dict):
            raise ValueError("hosts 中每项必须是 mapping")
        for key in ("name", "host", "user"):
            if not item.get(key):
                raise ValueError(f"host 缺少字段：{key}")
        if item["name"] in names:
            raise ValueError(f"host name 重复：{item['name']}")
        if "password" in item:
            raise ValueError("禁止保存明文 password，请使用 password_env")
        if not item.get("password_env") and not item.get("key_file"):
            raise ValueError(f"{item['name']} 必须配置 password_env 或 key_file")
        names.add(str(item["name"]))
    return data


def make_specs(inventory: dict[str, Any], selected: set[str] | None) -> list[HostSpec]:
    specs = []
    for item in inventory["hosts"]:
        if selected and item["name"] not in selected:
            continue
        specs.append(
            HostSpec(
                name=str(item["name"]),
                host=str(item["host"]),
                user=str(item["user"]),
                port=int(item.get("port", 22)),
                password_env=item.get("password_env"),
                key_file=item.get("key_file"),
                role=item.get("role"),
                endpoint=item.get("endpoint"),
            )
        )
    if selected and {spec.name for spec in specs} != selected:
        raise ValueError(f"inventory 中不存在：{sorted(selected - {s.name for s in specs})}")
    return specs


def connect(spec: HostSpec, config: dict[str, Any]) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    policy = config.get("known_hosts_policy", "reject")
    if policy == "auto_add":
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    elif policy == "reject":
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    else:
        raise ValueError("known_hosts_policy 只支持 reject/auto_add")
    timeout = float(config.get("connect_timeout", 10))
    kwargs: dict[str, Any] = dict(
        hostname=spec.host,
        port=spec.port,
        username=spec.user,
        timeout=timeout,
        auth_timeout=timeout,
        banner_timeout=timeout,
        allow_agent=False,
        look_for_keys=False,
    )
    if spec.key_file:
        kwargs["key_filename"] = os.path.expanduser(spec.key_file)
    else:
        password = os.environ.get(spec.password_env or "")
        if password is None:
            raise RuntimeError(f"环境变量 {spec.password_env} 未设置")
        kwargs["password"] = password
    client.connect(**kwargs)
    return client


def run_ssh(client: paramiko.SSHClient, command: str, timeout: float) -> tuple[int, str, str]:
    _, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return stdout.channel.recv_exit_status(), out, err


def guard(container: str) -> str:
    quoted = shlex.quote(container)
    return (
        "names=$(docker ps -a --format '{{.Names}}'); "
        f"printf '%s\\n' \"$names\" | grep -Fxq -- {quoted} || "
        f"{{ echo '目标容器不存在或名称不精确: {container}' >&2; exit 42; }}; "
    )


def inspect_command(container: str) -> str:
    fmt = (
        '{"id":"{{.Id}}","image_id":"{{.Image}}",'
        '"image_name":"{{.Config.Image}}","status":"{{.State.Status}}",'
        '"started_at":"{{.State.StartedAt}}"}'
    )
    return f"docker inspect --format {shlex.quote(fmt)} -- {shlex.quote(container)}"


PROBE = r"""
import glob, hashlib, importlib.metadata, json, os, re, subprocess

SECRET_KEY = re.compile(
    r"api[-_]?key|password|passwd|secret|credential|authorization|"
    r"(?:access|auth|bearer|hf)[-_]?token|^token$", re.I
)

def redact(value):
    if isinstance(value, dict):
        return {key: "<redacted>" if SECRET_KEY.search(str(key)) else redact(child)
                for key, child in value.items()}
    if isinstance(value, list):
        return [redact(child) for child in value]
    return value

def redact_argv(args):
    result, hide_next = [], False
    for arg in args:
        if hide_next:
            result.append("<redacted>")
            hide_next = False
        elif arg.startswith("--") and SECRET_KEY.search(arg[2:].split("=", 1)[0]):
            if "=" in arg:
                result.append(arg.split("=", 1)[0] + "=<redacted>")
            else:
                result.append(arg)
                hide_next = True
        else:
            try:
                parsed = json.loads(arg)
                result.append(json.dumps(redact(parsed)) if isinstance(parsed, (dict, list)) else arg)
            except (ValueError, TypeError):
                result.append(arg)
    return result

SAFE_PREFIXES = (
    "HCCL_", "GLOO_", "TP_SOCKET_", "ASCEND_", "VLLM_", "MOONCAKE_",
    "MMC_", "PYTORCH_NPU_", "TASK_QUEUE_",
)

def version(name):
    try: return importlib.metadata.version(name)
    except Exception: return None

def module_info(name):
    old = os.getcwd()
    try:
        os.chdir("/tmp")
        module = __import__(name)
        file = os.path.realpath(module.__file__)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    finally:
        os.chdir(old)
    result = {"file": file}
    if os.path.isfile(file):
        result["sha256"] = hashlib.sha256(open(file, "rb").read()).hexdigest()
    try:
        root = subprocess.check_output(
            ["git", "-C", os.path.dirname(file), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        ).strip()
        result["git_root"] = root
        result["git_head"] = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        ).strip()
        result["git_dirty"] = bool(subprocess.check_output(
            ["git", "-C", root, "status", "--porcelain"],
            stderr=subprocess.DEVNULL, text=True, timeout=5,
        ).strip())
    except Exception: pass
    return result

def find_process():
    for path in sorted(glob.glob("/proc/[0-9]*/cmdline"), key=lambda p: int(p.split("/")[2])):
        try: args = [x.decode("utf-8", "replace") for x in open(path, "rb").read().split(b"\0") if x]
        except Exception: continue
        if "serve" in args and any("vllm" in x for x in args): return int(path.split("/")[2]), args
    return None, []

def parse_args(args):
    result = {}
    if "serve" in args and args.index("serve") + 1 < len(args): result["model"] = args[args.index("serve") + 1]
    wanted = {
        "--host", "--port", "--data-parallel-size", "--data-parallel-rank",
        "--data-parallel-size-local", "--data-parallel-start-rank",
        "--data-parallel-address", "--data-parallel-rpc-port",
        "--tensor-parallel-size", "--max-model-len",
        "--max-num-batched-tokens", "--max-num-seqs", "--quantization",
        "--compilation-config", "--additional-config", "--kv-transfer-config",
    }
    for index, arg in enumerate(args):
        if arg in wanted and index + 1 < len(args):
            value = args[index + 1]
            if arg in {"--compilation-config", "--additional-config", "--kv-transfer-config"}:
                try: value = json.loads(value)
                except Exception: pass
            result[arg] = value
    for flag in ("--enable-expert-parallel", "--enforce-eager", "--headless"): result[flag] = flag in args
    return result

def layer_fields(value, prefix=""):
    found = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in {"num_hidden_layers", "num_layers", "n_layer"}: found[path] = child
            found.update(layer_fields(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value): found.update(layer_fields(child, f"{prefix}[{index}]"))
    return found

pid, argv = find_process()
serve = parse_args(argv)
result = {
    "container_hostname": os.uname().nodename,
    "visible_npu_devices": len(glob.glob("/dev/davinci[0-9]*")),
    "versions": {
        name: version(package)
        for name, package in (
            ("vllm", "vllm"), ("vllm_ascend", "vllm-ascend"),
            ("torch", "torch"), ("torch_npu", "torch-npu"),
        )
    },
    "vllm_ascend_module": module_info("vllm_ascend"),
    "vllm_pid": pid, "vllm_argv": redact_argv(argv), "serve": redact(serve),
}
if pid:
    try: result["vllm_cwd"] = os.path.realpath(f"/proc/{pid}/cwd")
    except Exception: pass
    try:
        env = {}
        for entry in open(f"/proc/{pid}/environ", "rb").read().split(b"\0"):
            if b"=" not in entry: continue
            key, value = entry.decode("utf-8", "replace").split("=", 1)
            if key.startswith(SAFE_PREFIXES) and not SECRET_KEY.search(key): env[key] = value
        result["selected_env"] = env
    except Exception: pass
model = serve.get("model")
if model:
    result["model_realpath"] = os.path.realpath(model)
    config_path = os.path.join(model, "config.json")
    if os.path.isfile(config_path):
        config = json.load(open(config_path, encoding="utf-8"))
        result["model_config_sha256"] = hashlib.sha256(open(config_path, "rb").read()).hexdigest()
        result["model_layer_fields"] = layer_fields(config)
        result["model_type"] = config.get("model_type")
        result["architectures"] = config.get("architectures")
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
"""


def probe_host(spec: HostSpec, inventory: dict[str, Any]) -> dict[str, Any]:
    container = inventory["container"]
    timeout = float(inventory.get("ssh", {}).get("command_timeout", 60))
    client = connect(spec, inventory.get("ssh", {}))
    try:
        code, out, err = run_ssh(client, guard(container) + inspect_command(container), timeout)
        if code:
            raise RuntimeError(err.strip() or out.strip())
        container_info = json.loads(out.strip())
        encoded = base64.b64encode(PROBE.encode()).decode()
        command = (
            guard(container)
            + f"docker exec --workdir /tmp -- {shlex.quote(container)} python -c "
            + shlex.quote(f"import base64;exec(base64.b64decode('{encoded}'))")
        )
        code, out, err = run_ssh(client, command, timeout)
        if code:
            raise RuntimeError(err.strip() or out.strip())
        return {
            "name": spec.name,
            "host": spec.host,
            "declared_role": spec.role,
            "endpoint": spec.endpoint,
            "container": container_info,
            "runtime": json.loads(out.strip().splitlines()[-1]),
            "ok": True,
        }
    finally:
        client.close()


def restart_host(spec: HostSpec, inventory: dict[str, Any], wait_seconds: int) -> dict[str, Any]:
    container = inventory["container"]
    timeout = max(float(inventory.get("ssh", {}).get("command_timeout", 60)), wait_seconds + 40)
    client = connect(spec, inventory.get("ssh", {}))
    try:
        code, out, err = run_ssh(client, guard(container) + inspect_command(container), timeout)
        if code:
            raise RuntimeError(err.strip() or out.strip())
        before = json.loads(out.strip())
        command = guard(container) + f"docker restart --time 30 -- {shlex.quote(container)}"
        code, out, err = run_ssh(client, command, timeout)
        if code or out.strip() != container:
            raise RuntimeError(err.strip() or f"重启返回异常：{out!r}")
        deadline, after = time.monotonic() + wait_seconds, None
        while time.monotonic() < deadline:
            code, out, _ = run_ssh(client, guard(container) + inspect_command(container), timeout)
            if code == 0:
                candidate = json.loads(out.strip())
                if candidate.get("status") == "running":
                    after = candidate
                    break
            time.sleep(2)
        if after is None:
            raise RuntimeError(f"容器在 {wait_seconds}s 内未恢复 running")
        if before["id"] != after["id"] or before["image_id"] != after["image_id"]:
            raise RuntimeError("重启后容器或镜像 ID 改变")
        return {"name": spec.name, "host": spec.host, "before": before, "after": after, "ok": True}
    finally:
        client.close()


def parallel(specs: list[HostSpec], worker, max_workers: int) -> list[dict[str, Any]]:
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(worker, spec): spec for spec in specs}
        for future in concurrent.futures.as_completed(futures):
            spec = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                results.append(
                    {"name": spec.name, "host": spec.host, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
                )
    return sorted(results, key=lambda item: item["name"])


def emit(value: Any, output: Path | None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--host-name", action="append", default=[])
    parser.add_argument("--max-workers", type=int, default=8)
    parser.add_argument("--output", type=Path)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("validate")
    sub.add_parser("probe")
    restart = sub.add_parser("restart")
    restart.add_argument("--yes-restart-exact-container", action="store_true")
    restart.add_argument("--wait-seconds", type=int, default=180)
    args = parser.parse_args()

    inventory = load_inventory(args.inventory)
    specs = make_specs(inventory, set(args.host_name) or None)
    if args.action == "validate":
        emit(
            {
                "ok": True,
                "container": inventory["container"],
                "hosts": [dataclasses.asdict(s) | {"password_env": bool(s.password_env)} for s in specs],
            },
            args.output,
        )
        return 0
    if args.action == "probe":
        results = parallel(specs, lambda spec: probe_host(spec, inventory), min(args.max_workers, len(specs)))
    else:
        if not args.yes_restart_exact_container:
            raise SystemExit("拒绝重启：缺少 --yes-restart-exact-container")
        results = parallel(
            specs, lambda spec: restart_host(spec, inventory, args.wait_seconds), min(args.max_workers, len(specs))
        )
    emit(results, args.output)
    return 0 if all(item.get("ok") for item in results) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
