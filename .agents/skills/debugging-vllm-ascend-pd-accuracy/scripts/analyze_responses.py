#!/usr/bin/env python3
"""分析 run_requests.py 生成的 JSONL，定位复读和首次输出偏差。"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

TOKEN_PATTERN = re.compile(r"[\u3400-\u9fff]|[A-Za-z0-9_]+|[^\s]")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text)


def extract_choice(record: dict[str, Any]) -> tuple[str, list[str] | None, str | None]:
    response = record.get("response")
    if not isinstance(response, dict):
        return "", None, None
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return "", None, None
    choice = choices[0]
    text = choice.get("text")
    if text is None and isinstance(choice.get("message"), dict):
        text = choice["message"].get("content")
    logprobs = choice.get("logprobs")
    tokens = logprobs.get("tokens") if isinstance(logprobs, dict) else None
    return str(text or ""), tokens if isinstance(tokens, list) else None, choice.get("finish_reason")


def repetition_info(tokens: list[str], min_repeats: int = 3, max_period: int = 32) -> dict[str, Any] | None:
    best = None
    count = len(tokens)
    for start in range(count):
        max_candidate = min(max_period, (count - start) // min_repeats)
        for period in range(1, max_candidate + 1):
            pattern = tokens[start : start + period]
            repeats, cursor = 1, start + period
            while cursor + period <= count and tokens[cursor : cursor + period] == pattern:
                repeats += 1
                cursor += period
            if repeats < min_repeats:
                continue
            candidate = {
                "start_token": start,
                "period": period,
                "repeats": repeats,
                "pattern": pattern,
                "covered_tokens": period * repeats,
            }
            if best is None or (candidate["start_token"], -candidate["covered_tokens"]) < (
                best["start_token"],
                -best["covered_tokens"],
            ):
                best = candidate
    return best


def first_divergence(left: list[str], right: list[str]) -> int | None:
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return None if len(left) == len(right) else min(len(left), len(right))


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"第 {line_number} 行不是 JSON object")
        records.append(value)
    if not records:
        raise ValueError("输入 JSONL 为空")
    return records


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    runs = []
    for record in records:
        endpoint = str(record.get("endpoint", "unknown"))
        text, api_tokens, finish_reason = extract_choice(record)
        tokens = [str(token) for token in api_tokens] if api_tokens else tokenize(text)
        item = {
            "endpoint": endpoint,
            "iteration": record.get("iteration"),
            "http_status": record.get("http_status"),
            "elapsed_seconds": record.get("elapsed_seconds"),
            "text": text,
            "tokens": tokens,
            "token_source": "api_logprobs" if api_tokens else "text_lexical",
            "finish_reason": finish_reason,
            "repetition": repetition_info(tokens),
        }
        runs.append(item)
        groups[endpoint].append(item)

    summary = {}
    for endpoint, items in sorted(groups.items()):
        texts = [item["text"] for item in items]
        elapsed = [float(item["elapsed_seconds"]) for item in items if item.get("elapsed_seconds") is not None]
        summary[endpoint] = {
            "runs": len(items),
            "unique_outputs": len(set(texts)),
            "all_equal": len(set(texts)) == 1,
            "repetition_runs": sum(item["repetition"] is not None for item in items),
            "mean_elapsed_seconds": round(statistics.mean(elapsed), 6) if elapsed else None,
        }

    pairwise = []
    endpoints = sorted(groups)
    for left_index, left_name in enumerate(endpoints):
        for right_name in endpoints[left_index + 1 :]:
            left, right = groups[left_name][0], groups[right_name][0]
            divergence = first_divergence(left["tokens"], right["tokens"])
            pairwise.append(
                {
                    "left": left_name,
                    "right": right_name,
                    "exact_text_match": left["text"] == right["text"],
                    "first_divergence_token": divergence,
                    "left_token": left["tokens"][divergence]
                    if divergence is not None and divergence < len(left["tokens"])
                    else None,
                    "right_token": right["tokens"][divergence]
                    if divergence is not None and divergence < len(right["tokens"])
                    else None,
                }
            )
    return {"endpoint_summary": summary, "pairwise_first_run": pairwise, "runs": runs}


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# PD 精度响应分析",
        "",
        "## Endpoint 汇总",
        "",
        "| Endpoint | Runs | Unique | Equal | Repetition | Mean seconds |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for name, item in result["endpoint_summary"].items():
        lines.append(
            "| {name} | {runs} | {unique} | {equal} | {repetition} | {mean} |".format(
                name=name,
                runs=item["runs"],
                unique=item["unique_outputs"],
                equal=item["all_equal"],
                repetition=item["repetition_runs"],
                mean=item["mean_elapsed_seconds"],
            )
        )
    lines.extend(
        [
            "",
            "## Endpoint 首次运行对比",
            "",
            "| Left | Right | Exact | First divergence token | Left token | Right token |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for item in result["pairwise_first_run"]:
        lines.append(
            "| {left} | {right} | {exact} | {divergence} | {left_token} | {right_token} |".format(
                left=item["left"],
                right=item["right"],
                exact=item["exact_text_match"],
                divergence=item["first_divergence_token"],
                left_token=item["left_token"],
                right_token=item["right_token"],
            )
        )
    lines.extend(["", "## 复读检测", ""])
    found = False
    for item in result["runs"]:
        repetition = item["repetition"]
        if repetition:
            found = True
            pattern = "".join(repetition["pattern"])
            lines.append(
                "- {endpoint} ? {iteration} ??? token {start} ????? {period}??? {repeats} ???? {pattern!r}?".format(
                    endpoint=item["endpoint"],
                    iteration=item["iteration"],
                    start=repetition["start_token"],
                    period=repetition["period"],
                    repeats=repetition["repeats"],
                    pattern=pattern,
                )
            )
    if not found:
        lines.append("- 未检测到连续三次以上的词法重复模式。")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    result = analyze(load_records(args.input))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = markdown_report(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
