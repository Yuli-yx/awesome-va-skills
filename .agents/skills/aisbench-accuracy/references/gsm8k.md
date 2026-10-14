# GSM8K reference and observed pitfalls

The PR 14872 experiment on 2026-09-07 ran AISBench from an existing source
checkout through a separate venv with system site packages. This avoided
changing the live vLLM installation. Source import via PYTHONPATH was used
after encountering a legacy installer dependency issue; this is an option
for an already prepared checkout, not a universal installation prescription.

The installed adapter was `VLLMCustomAPIChat`. The configured model-level
postprocessor was `extract_non_reasoning_content`; the dataset used
`Gsm8kEvaluator`, `gsm8k_postprocess`, and `gsm8k_dataset_postprocess`.
Inspect these functions in the chosen AISBench revision and verify their
combined behavior with actual server output. Naming a postprocessor does
not prove the adapter applied it or handled reasoning delimiters correctly.

The prompt was zero-shot CoT chat:

```text
Answer the following question. The last line of the response should follow this format: "answer:$ANSWER" (without quotes), where ANSWER is a number. Let's think step by step.

Question: {question}
```

The dataset config used `ZeroRetriever`, `GenInferencer` and
`stopping_criteria=["Question"]`. This stop condition must also match any
baseline. The dataset was the complete 1319-item test split.

After creating model and dataset config files under an experiment config
directory, the installed CLI accepted this form (paths are illustrative):

```bash
PYTHONPATH=/path/to/aisbench-source /path/to/evaluator-venv/bin/python \
  -m ais_bench.benchmark.cli.main \
  --models experiment_model --datasets experiment_gsm8k \
  --config-dir /path/to/experiment-config --mode all \
  --num-warmups 0 --dump-eval-details --debug \
  --work-dir /path/to/unique-results
```

Model settings included temperature 0, seed 1024, ignore_eos false,
max_out_len 1024, batch_size 8, retry 2 and non-streaming requests to the
PD proxy. **Top-k/top-p were not explicitly pinned in that historical
configuration.** It is therefore not a fully aligned baseline template;
new runs must resolve and record their effective values.

All 1319 logical samples succeeded. AISBench scored 1188 correct and 131
incorrect: 90.06823351023503%, with 4992.15 seconds of inference time.
Saved prediction text retokenized to exactly 1024 tokens for 142 samples,
113 of which were incorrect. The remaining 1177 samples had 1159 correct.
Because finish reasons were not retained in those prediction files, the
142 count is evidence of suspected cap hits, not an authoritative count
from API finish_reason metadata. The subset score is not a full-dataset
accuracy result and does not prove those errors would all recover with a
larger budget.

Artifacts included `predictions/<model>/gsm8k.jsonl`,
`results/<model>/gsm8k.json` with per-item details, resolved Python configs
and summary CSV/Markdown. Match predictions by sample ID rather than file
order: concurrent inference wrote completion order while evaluator details
used dataset order. Preserve this distinction in post-run analysis.
