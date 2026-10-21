# awesome-va-skills

[中文](README.md) | English

Skills for vLLM-Ascend and Ascend inference engineering, aligned with the company
`awesome-mindie-skills` catalogue: category metadata, pinned source revisions,
bilingual discovery and scoped review evidence. The new self-contained pooling
package lives in `skills/ascend-memcache-pooling/`; legacy skills and shared tools
retain their complete workspace-relative layout.

The archive contains 30 complete packages. Only license-resolved packages enter
the curated catalogue; four historical imports remain pending. Existing local
untracked Leaf-Spine/vendor drafts are preserved and excluded from this public
contribution. See [layout and installation](docs/collection-layout.md).

```bash
git clone https://github.com/Yuli-yx/awesome-va-skills.git
cd awesome-va-skills
python -m pip install -r requirements.txt
python scripts/validate_catalog.py
python scripts/render_catalog.py --check
```

Definition reviews and offline tests do not certify NPU deployment, SSD readback
or performance. See [attribution](ATTRIBUTION.md) and the [complete package
inventory](skills-manifest.json) for source and license boundaries.

<!-- CATALOG:START -->

26 skills · 8 categories

Definitions reviewed: 26 · Entries with execution reproductions: 0. See each entry's metadata for scope.

| Upstream Source | Listed | Maintainer | License |
|---|---|---|---|
| [va-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 16 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | MIT |
| [va-hixl-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 5 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | CANN-2.0 |
| [va-apache-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 4 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | Apache-2.0 |
| [va-pooling-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 1 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | CC0-1.0 AND MIT |

- [Environment and dependencies](#environment)
- [Model integration and conversion](#model-integration)
- [Serving and scaling](#serving)
- [Correctness and accuracy](#correctness)
- [Benchmarking and regressions](#benchmarking)
- [Profiling and bottleneck analysis](#profiling)
- [Debugging](#debugging)
- [Delivery and operations](#delivery)

<a id="environment"></a>

### Environment and dependencies

Check drivers, CANN, framework compatibility, containers, and devices.

- [machine-management](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/machine-management/SKILL.md) — Add, verify, repair, or remove a managed remote NPU host for this workspace.
  `Ascend` `vLLM Ascend` `Hardware depends on checks` `Workflow` · [Metadata](catalog/skills/machine-management.yaml)
- [remote-code-parity](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/remote-code-parity/SKILL.md) — Ensure a ready remote runtime runs the exact current local workspace state before any remote smoke, service launch, or benchmark.
  `Ascend` `vLLM Ascend` `Host tools` `Workflow` · [Metadata](catalog/skills/remote-code-parity.yaml)
- [remote-toolbox](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/remote-toolbox/SKILL.md) — Resolve, probe, execute, observe jobs, sync, manage service lifecycle, transfer artifacts, and clean VAWS remote Ascend session containers through structured agent-facing CLI entrypoints..
  `Ascend` `vLLM Ascend` `Host tools` `Workflow` · [Metadata](catalog/skills/remote-toolbox.yaml)
- [repo-init](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/repo-init/SKILL.md) — Initialize this workspace after clone.
  `Ascend` `vLLM Ascend` `Host tools` `Workflow` · [Metadata](catalog/skills/repo-init.yaml)
- [session-management](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/session-management/SKILL.md) — Create, list, inspect, remove, and garbage-collect isolated VAWS agent sessions.
  `Ascend` `vLLM Ascend` `Host tools` `Workflow` · [Metadata](catalog/skills/session-management.yaml)
- [vllm-ascend-build](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-build/SKILL.md) — Compile and verify vLLM-Ascend from a pinned workspace or PR revision inside a ready Ascend container.
  `Ascend` `vLLM Ascend` `Host tools` `Workflow` · [Metadata](catalog/skills/vllm-ascend-build.yaml)

<a id="model-integration"></a>

### Model integration and conversion

Integrate models, convert weights, and verify configuration and input/output contracts.

- [main2main](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/main2main/SKILL.md) — Adapt vLLM-Ascend to upstream vLLM main changes.
  `Ascend` `vLLM Ascend` `Offline analysis` `Workflow` · [Metadata](catalog/skills/main2main.yaml)
- [modelscope](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/modelscope/SKILL.md) — Download, resume, status-check, and SHA256-verify ModelScope model weights.
  `Ascend` `vLLM Ascend` `Host tools` `Workflow` · [Metadata](catalog/skills/modelscope.yaml)
- [vllm-ascend-model-adapter](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-model-adapter/SKILL.md) — Adapt and debug existing or new models for vLLM on Ascend NPU.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/vllm-ascend-model-adapter.yaml)

<a id="serving"></a>

### Serving and scaling

Deploy colocated or disaggregated services and verify topology, endpoints, and requests.

- [ascend-memcache-pooling](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/skills/ascend-memcache-pooling/SKILL.md) — Deploy and inspect Ascend A3/A5 MemCache KV pools over SDMA, UB, UBoE or supported Host RoCE; plan DRAM/SSD owners, preserve P/D transfer, and monitor multi-DP HBM, external reuse and SSD readback evidence..
  `Ascend` `vLLM Ascend` `MemCache` `SSD` `NPU execution` `Workflow` · [Metadata](catalog/skills/ascend-memcache-pooling.yaml)
- [vllm-ascend-serving](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-serving/SKILL.md) — Start, check, or stop a single-node vLLM Ascend online service on a workspace-managed ready remote container.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/vllm-ascend-serving.yaml)

<a id="correctness"></a>

### Correctness and accuracy

Fix references and case matrices to compare outputs, numerical error, and task quality.

- [aisbench-accuracy](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/aisbench-accuracy/SKILL.md) — Run AISBench dataset accuracy evaluation against a running vLLM service, aligning sampling, prompts and answer postprocessing with the baseline.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/aisbench-accuracy.yaml)

<a id="benchmarking"></a>

### Benchmarking and regressions

Evaluate throughput and latency using warmup, repeated measurements, and controlled comparisons.

- [aisbench-pd-benchmark](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/aisbench-pd-benchmark/SKILL.md) — Prepare and run AISBench performance cases for vLLM Ascend services and two-node PD proxy deployments, including tokenizer-based normal or repeated-prefix dataset construction, warmup and formal runs, exact concurrency/request-count semantics, and result capture.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/aisbench-pd-benchmark.yaml)
- [pd-pure-role-benchmark](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/pd-pure-role-benchmark/SKILL.md) — Prepare and run AISBench pure Prefill, pure Decode, and end-to-end capacity acceptance for a 1P1D deployment, with TTFT-constrained request rates, TPOT-constrained concurrency, steady-stage results, and MTP-aware QPS comparisons.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/pd-pure-role-benchmark.yaml)
- [vllm-ascend-benchmark](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-benchmark/SKILL.md) — Run vLLM online-serving benchmarks on a workspace-managed remote container.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/vllm-ascend-benchmark.yaml)

<a id="profiling"></a>

### Profiling and bottleneck analysis

Collect or analyze traces, per-rank behavior, and HBM use with traceable evidence.

- [ascend-memory-profiling](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/ascend-memory-profiling/SKILL.md) — Profile and attribute HBM memory usage on Ascend NPU for vLLM serving scenarios.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/ascend-memory-profiling.yaml)
- [ascend-profiling-analysis](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/ascend-profiling-analysis/SKILL.md) — Analyze Ascend NPU torch profiler output (kernel_details.csv / trace_view.json / op_summary / communication.json) for one or many profiling roots and produce a traceable report (rank/step/layer/operator summary, cross-rank alignment, diagnosis findings, report.md / report.xlsx / report.html with single-step inspectors, bubble tracing axes, and zoomable Chrome-tracing-style timelines).
  `Ascend` `vLLM Ascend` `Offline analysis` `Workflow` · [Metadata](catalog/skills/ascend-profiling-analysis.yaml)
- [ascend-profiling-collection](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/ascend-profiling-collection/SKILL.md) — Collect one Ascend torch-profiler case end-to-end on a workspace-managed remote NPU container.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/ascend-profiling-collection.yaml)

<a id="debugging"></a>

### Debugging

Reduce startup, communication, graph, and operator failures and verify fixes.

- [debugging-vllm-ascend-pd-accuracy](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/debugging-vllm-ascend-pd-accuracy/SKILL.md) — Use when vLLM Ascend 的 Prefill/Decode 分离出现复读、乱码、截断、首 token 偏差、PD 与非 PD 输出不一致，或全量模型异常而减层模型正常；适用于 KV transfer、Mooncake、外部 DP、多机 TP/DP、ACL Graph、Decode logits 和 NPU 精度问题的全自动远程诊断。.
  `Ascend` `vLLM Ascend` `NPU execution` `Workflow` · [Metadata](catalog/skills/debugging-vllm-ascend-pd-accuracy.yaml)
- [driver-peermem-check](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/driver-peermem-check/SKILL.md) — 分析 Ascend 驱动 .run 包中是否包含 npu_peermem.ko 及相关源码。适用于：
- 判断某个驱动版本是否支持 d2d/d2rd RDMA 传输
- 对比不同平台的驱动包内容差异
- 检查 npu_peermem 模块的构建依赖是否就绪
- 用户提到驱动包、npu_peermem、d2d RDMA 失败、peer memory 等问题时
.
  `Ascend` `HIXL` `Offline analysis` `Workflow` · [Metadata](catalog/skills/driver-peermem-check.yaml)
- [hixl-troubleshoot](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-troubleshoot/SKILL.md) — 在 Ascend 上定位 HIXL/ADXL/HIXL_CS 建链、传输问题。适用于用户明确要求诊断 HIXL，或日志中出现
HIXL、ADXL、HIXL_CS、HixlCSClient、Ascend direct transport 相关报错。
.
  `Ascend` `HIXL` `NPU execution` `Workflow` · [Metadata](catalog/skills/hixl-troubleshoot.yaml)

<a id="delivery"></a>

### Delivery and operations

Map changes to build, correctness, and performance checks and record coverage.

- [hixl-pr-review](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-pr-review/SKILL.md) — HIXL 代码检视技能。用于检视 GitCode 上的 HIXL 项目 PR，当用户要求检视PR，审查PR时调用此skill。
自动分析代码变更，检查内存泄漏、安全漏洞和可读性，生成结构化报告并发布评论。
.
  `Ascend` `HIXL` `Offline analysis` `Workflow` · [Metadata](catalog/skills/hixl-pr-review.yaml)
- [hixl-srs-doc-generator](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-srs-doc-generator/SKILL.md) — 当用户要求为 HIXL 或 ADXL 功能生成、扩展或评审 SRS/需求设计文档时使用，特别涉及 src/hixl 或 src/llm_datadist/adxl 目录下的变更。
触发关键词包括 SRS、设计文档、需求描述、功能要点、技术方案、相关文档、测试方案，或将简短需求转化为完整设计文档的请求。
.
  `Ascend` `HIXL` `Offline analysis` `Workflow` · [Metadata](catalog/skills/hixl-srs-doc-generator.yaml)
- [hixl-ut-generator](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-ut-generator/SKILL.md) — 为 HIXL 仓库中的 C++ 改动生成单元测试（UT）方案与代码草稿。
支持三种输入源：
1.
  `Ascend` `HIXL` `Offline analysis` `Workflow` · [Metadata](catalog/skills/hixl-ut-generator.yaml)
- [vllm-ascend-release-note-writer](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-release-note-writer/SKILL.md) — You are a release note writer for vLLM Ascend project (vllm-project/vllm-ascend).
  `Ascend` `vLLM Ascend` `Offline analysis` `Workflow` · [Metadata](catalog/skills/vllm-ascend-release-note-writer.yaml)
- [vllm-ascend-release](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-release/SKILL.md) — End-to-end release management skill for vLLM Ascend.
  `Ascend` `vLLM Ascend` `Offline analysis` `Workflow` · [Metadata](catalog/skills/vllm-ascend-release.yaml)

<!-- CATALOG:END -->
