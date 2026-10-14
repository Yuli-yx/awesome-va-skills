---
name: aisbench-accuracy
description: Run AISBench dataset accuracy evaluation against a running vLLM service, aligning sampling, prompts and answer postprocessing with the baseline. Use for GSM8K or other full-dataset accuracy runs and regression comparisons, not throughput benchmarks.
---

# AISBench Accuracy

Evaluate the intended service through AISBench and produce a reproducible score with complete sample accounting. For PD, send requests through the PD proxy, not directly to a decode worker. Preserve running services unless the user authorizes a change. Use remote-dev tools or the managed remote job/artifact wrappers for remote work; keep runtime records under `.vaws-local/` and credentials out of tracked files.

## Align the evaluation contract first

Use the user's reference configuration or an existing baseline as the source of truth. Read the installed AISBench version's model adapter, dataset config and postprocessors before adapting a configuration: field names and API behavior vary by revision. Record the AISBench revision and resolved configuration, not only a config alias.

**Sampling parameters and postprocessing must both match.** Temperature, top-k, top-p and output length control generation; they are not answer postprocessing. Do not assume omitted values mean greedy sampling, disabled top-k or unlimited output. For each setting record the configured value, actual outgoing request field and effective server default if omitted:

| Area | Values to align with baseline |
|---|---|
| Sampling | temperature, top_k, top_p, min_p when used, seed, repetition/frequency/presence penalties, number of completions |
| Length and stopping | max_out_len → actual API token limit, context limit, input truncation, stop strings/token IDs, ignore_eos; whether reasoning consumes the output budget |
| Prompt | dataset split/revision/sample order, zero/few-shot examples, system prompt, chat template, thinking mode and template kwargs |
| Response extraction | content versus reasoning_content, stream assembly, reasoning delimiters, model-level postprocessor |
| Scoring | dataset prediction postprocessor, reference postprocessor, evaluator, normalization and exact-match rules |
| Runtime | model/weight/tokenizer identity, quantization, code revisions, model runner, PD topology, MTP, prefix cache, graph/eager, concurrency and retry policy |

Verify that the adapter actually forwards the requested sampling fields. For example top_k may be a vLLM extension whose placement depends on whether the adapter uses an SDK or raw HTTP; inspect the implementation and captured request rather than blindly adding an `extra_body` field. Verify server generation_config defaults and any overrides. A field present in the Python config but absent from the request is not alignment. Keep secrets redacted in request evidence.

If no baseline exists, state the selected evaluation contract and report an absolute score only. Do not claim “no regression” against an unmeasured or differently configured baseline. Choose an output budget appropriate to the model's reasoning behavior; the historical 1024-token GSM8K cap is not a recommended default. If the user explicitly requests that cap, preserve it and report its effect.

## Prepare and precheck

Use an existing compatible AISBench installation or an isolated evaluator venv so installing evaluator dependencies does not alter the live serving runtime. Verify dataset availability, split size and checksum locally on the target. Keep the dataset and model configuration files with the experiment artifacts.

Run a small explicit sample subset before the full run. Confirm the actual request sampling fields, a successful response, raw content/reasoning representation, extracted answer and score against a known reference. Inspect the execution order of model postprocessing and dataset postprocessing: removing reasoning incorrectly can produce an empty answer or cause the evaluator to score a number from unfinished reasoning. Retain raw responses before destructive postprocessing where the adapter supports it.

Check the installed CLI's `--help`. Do not assume `--dry-run` prevents requests: the version used in the validated example executed its configured single sample. Use a separate subset config and output directory for prechecks; remove subset restrictions for the full run and verify the expected sample count.

## Run and monitor

Submit a durable remote job with a unique ID and output directory. A previously validated CLI form is shown in [the GSM8K reference](references/gsm8k.md); adapt it to the installed CLI, not by installing an arbitrary version to match the example. Freeze parameters for the run. Do not silently change output length, concurrency or postprocessing midway through a scored experiment.

Monitor completed/failed requests, job exit status and P/D logs at a reasonable cadence. A failed request may be retried: distinguish logical samples, HTTP attempts, recovered errors and final failures. Inspect stalled progress or service exceptions rather than repeatedly restarting. Preserve services when the user asked to retain them.

## Validate the result

- Require successful job completion and reconcile expected samples, unique sample IDs, predictions and evaluator details. Report correct, incorrect, empty, missing and failed counts. Do not drop failed samples to improve the denominator.
- Preserve the resolved configs, raw predictions, scored details, summary, build/runtime identities, evaluator logs and relevant service errors. Pull artifacts with checksums.
- Count finish_reason=length and output token usage when available. If the adapter discarded them, retokenizing saved text is only an estimate: decoded/re-encoded lengths and filtered reasoning can differ from generated token counts. Label cap hits as suspected unless supported by response metadata.
- Cross-tabulate correct/incorrect with cap hits, empty final answers and extraction failures. Accuracy after excluding truncated samples is diagnostic only, not a replacement dataset score; that subset is biased.
- If the output cap materially affects results, disclose it. For a no-regression comparison, rerun both baseline and candidate under the same adequate budget. A targeted rerun of cap-hit samples can diagnose truncation, but must be labeled separately; do not silently merge it into the original score.
- A successful full dataset run supports the tested model/configuration. It does not prove memory safety or cover untested prefix caching, concurrency, graph modes or other models.

Return the exact score and denominator, request failures, duration, aligned sampling and postprocessing settings, truncation evidence, comparison limits, artifact paths and service retention status. Keep inference throughput benchmarking in `vllm-ascend-benchmark` and service changes in `vllm-ascend-serving`.
