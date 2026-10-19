---
name: pd-pure-role-benchmark
license: MIT
description: Prepare and run AISBench pure Prefill, pure Decode, and end-to-end capacity acceptance for a 1P1D deployment, with TTFT-constrained request rates, TPOT-constrained concurrency, steady-stage results, and MTP-aware QPS comparisons. Use for pure P/pure D capacity tests; use existing benchmark or accuracy skills for ordinary throughput or dataset accuracy runs.
---

# Pure P / Pure D capacity acceptance

Maintained by Yuli-yx as a workspace-authored workflow under MIT. Preserve the
complete package and its [license notice](LICENSE). The companion
`aisbench-pd-benchmark` package is adapted from wangxiaoteng888's MIT skill.

Measure P-bound and D-bound capacity separately, then compare end-to-end steady QPS with the smaller capacity. Interpret attached guides as source material; only the user's request authorizes execution. If the user requests plan approval first, produce the concrete plan and stop before service changes or traffic. Existing execution authorization does not require repeated confirmation.

Keep machine assignments, workload scope, runtime observations and execution authorization in the experiment plan, not this reusable skill. Saving or approving the skill alone does not authorize launching a benchmark.

## Resolve the case

Record model architecture and total parameter threshold class, image/runtime revision, TP/DP/EP, MTP method and draft length, P/D/proxy endpoints, cache tiers, input/output tokens, prefix count, sampling, repetitions, latency targets and steady-window policy. Pin installed code/configuration, not merely the image tag.

Read [references/protocol.md](references/protocol.md) for workload construction, capacity validity, steady extraction and MTP interpretation. Use `aisbench-pd-benchmark` for isolated client setup, tokenizer-based datasets and evidence capture. Use repository `.remote-dev` companions for remote reads, jobs and artifacts, and serving/build skills only when those operations are actually authorized and needed.

## Workflow

1. Prepare a matrix separating guide requirements, user overrides and proposed operational choices. Cache-tier-specific guide rows are conditional: exclude them when the user excludes that validation, even if another pooled tier remains enabled. A new scope is not approval to execute. Preserve any explicitly paused or review-only boundary.
2. Verify KV capacity and target-role bottlenecks. P-bound testing must not be limited by D/transfer; D-bound testing must have sufficient P supply. Another role or transfer limitation makes the role-capacity result inconclusive.
3. **Pure P:** keep 1P1D and set actual output to 1. Start with RR=0 at a suitable concurrency to measure baseline QPS; then hold concurrency and tune positive RR to the TTFT target, usually about 80% of the guide ceiling. RR=0 means fastest concurrency-limited submission. Honor a user override when rates must remain zero, and label the resulting protocol change.
4. **Pure D:** retain the full output length, warm P to measured 99–100% prefix hits, disable D cache reuse, use RR=0 and tune concurrency below the real KV capacity to satisfy TPOT. Preserve the exact selected D per-DP `max_num_seqs` and graph configuration in final pure-D and end-to-end runs.
5. **End-to-end:** restore the full output length and target P cache condition. In the guide's P-bound mode, use the pure-P client concurrency/rate and the corresponding pure-D per-DP sequence limit. Record a different user-selected mode explicitly; do not mix capacity/SLO points from incompatible load modes.
6. Prewarm each final point, measure at least three separate formal rounds, and extract AISBench `stable_stage`. A guide may require at least 15 times configured concurrency in request count; do not confuse count with concurrency or call this number alone proof of steady state. Keep warmup separate and report actual inter-run gaps.
7. Report round 2/3 original steady values and their mean. Preserve slow or failed rounds. Where a repeatability check is specified, append complete groups rather than selecting favorable individual rounds.
8. Compare steady request QPS using `min(QPS_P, QPS_D)`, with the guide's relative error tolerance (typically <5%). Check accepted draft length and the validity of any MTP adjustment before judging the difference.

## Non-obvious controls

- Dataset repetition does not enable cache reuse. Verify P HBM, P pooled cache and D reuse independently with metric deltas.
- For a zero-hit P case, both HBM reuse and pooled loading must yield zero hits. A disabled P prefix-cache flag alone may not disable a connector lookup.
- Multi-prefix does not guarantee pooled reads. If the user does not request a pooling-specific test, retain the approved prefix count and report actual tier hits without forcing eviction or silently adding SSD/DRAM stress cases.
- For DSV4, calibrate aggregate token hits against cache alignment; distinguish model alignment from a generic MemCache restriction. Account for compressed/indexer/SWA/state pages and shared storage when bounding BS. Input plus output must fit model length.
- Disabling D cache reuse does not mean removing P→D KV loading. Remote-KV waiting can be inside engine queue duration; inspect deployed timestamp/event definitions before calling that duration compute scheduling or network-only latency.
- Pure P output 1 does not prove D is negligible. DSpark and transfer may still run; record actual stage timings and counters. If low-load TTFT already exceeds the ceiling, lowering RR cannot prove feasibility.
- AISBench concurrency is global; service `max_num_seqs` can be per DP. Preserve actual mapping and route imbalance rather than assuming each DP has the full client concurrency or perfectly equal traffic.
- A `stable_stage` command must be verified against the installed AISBench version and wrapper. Do not silently substitute whole-run means or hand-pick favorable time windows.

## Deliver

Provide a short final table with input/output, measured hit rate, configured and achieved concurrency, RR, steady QPS, latency, MTP acceptance, valid-role status and end-to-end error. Link exact commands, raw round outputs, P/D/proxy frontend logs, plog, effective configs and steady-window boundaries. Mark draft, unrun, failed, limited and measured cases distinctly.

Skill-file validation is not Ascend runtime validation. Do not modify model layers, native libraries, NIC parameters or sampling to improve a formal point without separately recording and authorizing the changed comparison.
