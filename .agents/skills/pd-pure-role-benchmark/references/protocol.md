# Protocol details

## Workload identity and cache semantics

The guide's pure-P tables may list the full end-to-end output length while the actual pure-P probe uses output 1. State both explicitly. Pure-D and end-to-end output lengths must match.

Construct token-counted data, then retain actual API input/output counts and dataset hashes. Compare identical prompt distribution and sampling when possible. Where uncached P and warmed P for pure-D supply use different data, retain the content-distribution difference and actual draft acceptance; do not imply identical MTP behavior from matching lengths alone. Prefer matching content with cache flags adjusted when that preserves the requested protocol.

For an explicitly requested cached-P capacity case, seed public prefixes across actual DP routes and prewarm under representative load. Do not warm all formal unique tails: this can silently turn a partial-hit case into 100% on subsequent rounds. Use distinct tails per round while preserving length-class proportions and public prefixes. Frozen datasets and tool configuration must exist before warmup finishes. High P cache hits used only to supply a pure-D test do not imply a separate cached-P acceptance case.

Use `total_hit_tokens / queried_input_tokens` for combined HBM plus pooled hits, and show each tier separately. Do not add hit ratios that use different denominators. A dataset `repeat_rate` is a construction parameter, not a measured hit rate. DSV4's compression/group alignment can require mixtures of adjacent aligned prefix lengths to achieve an aggregate target.

If the user retains a small fixed multi-prefix set without a pool stress requirement, do not increase prefixes, force eviction or create SSD pressure. Exclude cache-tier-specific acceptance rows that the user declines; keeping DRAM pooling available does not restore an excluded three-tier cached-P case. A mostly-HBM steady phase is a valid cache result but does not establish pooled-only performance.

## BS and bottleneck validity

Read startup cache capacity, free/allocated blocks and group layouts. Estimate simultaneous input+output reservation per DP, include speculative lookahead, and compare against actual no-reuse admission/preemption behavior. Ordinary `KV tokens / (input + output)` is only a rough first bound for homogeneous caches; compressed/SWA/circular/state/shared groups require their actual managers and allocation units.

Disable D prefix/HBM and pooled reuse and prove the setting effective. Repeated identical prefixes on D with reuse enabled can make a BS limit appear much larger than distinct contexts support. The D consumer must still receive remote KV from P.

Keep a client/scheduler/connector timing view. Pure-P needs enough D service and transfer capacity at the selected P rate; pure-D needs enough P supply at the selected D rate. Inspect rolling queue trends and achieved load, not just total elapsed time or NPU utilization. HTTP success and output count prove completion, not target-role isolation.

Record which duration contains remote-KV waiting. Some deployed schedulers only emit `SCHEDULED` after async KV receive completes; their queue interval includes transfer waiting. Connector timers may include address generation, synchronous transfer and internal waits, and exclude peer queueing or completion notification. Treat timers as nested until their actual boundaries prove otherwise.

## RR/concurrency search

Pure-P baseline uses RR=0. A positive rate starts no higher than measured baseline QPS, then decreases/increases by bracketed search towards the TTFT target. Avoid integer rounding that maps sub-1 QPS to zero, because zero changes the load mode. When a guide says round down but illustrates 2.413→2.4, state a fractional rounding policy.

Pure-D uses RR=0 and searches concurrency under capacity. Select the largest stable point satisfying the TPOT ceiling. Tight and loose ceilings are separate operating points. Before formal measurement, pin D per-DP sequence limits and graph settings so the matched end-to-end case preserves those settings.

Report client configured concurrency and achieved average in-flight separately. Positive RR may be the binding limiter, and achieved concurrency can be far below the maximum.

## Steady measurement

Warmup and three formal rounds have separate directories, commands, return codes and metrics snapshots. Keep all original outputs, including first/slow/failed rounds. A suggested request budget is `max(15*C, estimated_QPS * planned_duration, minimum_case_count)`, rounded up; inspect the effective steady window afterwards and extend if insufficient.

Use the installed AISBench stable-stage summarizer and preserve raw results plus summarizer command/version and window boundaries. The guide gives:

```bash
ais_bench --models <actual-model-config> --datasets <actual-dataset-config> \
  --debug --summarizer stable_stage --mode perf --reuse <run-timestamp>
```

This is a template, not proof that every wrapper/package version supports identical flags. Verify that reuse re-summarizes the intended saved results and does not unexpectedly resubmit the workload before invoking it. Never reuse the guide's GSM8K name for a generated fixed-length prefix workload without the actual matching configuration.

Use identical extraction policy across pure P, pure D and end-to-end. A throughput window and the latency/MTP sample population must refer to the same selected stable stage. Preserve total-stage results as auxiliary data, not a replacement for stable QPS.

## MTP and acceptance

Capture delta counters for draft invocations, proposed draft tokens and accepted draft tokens over the selected interval. Distinguish acceptance rate (`accepted / proposed`) from average accepted length. Where the engine convention includes the ordinary/bonus token, average accepted length is `1 + accepted / draft_invocations`; verify the deployed DSpark metric convention before using this expression.

Unadjusted target:

```text
Q_theory = min(Q_P, Q_D)
error = abs(Q_E2E - Q_theory) / Q_theory
```

The guide permits:

```text
Q_D_adjusted = Q_D * L_E2E / L_D
Q_theory_adjusted = min(Q_P, Q_D_adjusted)
```

Use that adjustment only when concurrency, output length and per-verification-step execution time remain comparable. L is the same accepted-length definition on both sides. Preserve raw and adjusted QPS plus the comparability evidence. If step timing changes, the simple proportional correction is insufficient; report the comparison limit and investigate rather than normalizing it away. ITL between emitted tokens is not automatically per-verification-step timing.

The final error threshold comes from the approved guide/plan; the example's arithmetic is not a measured baseline. Always recompute from original numeric values. Label role-invalid or unmatched-MTP results before deciding whether an end-to-end difference indicates PD overhead.
