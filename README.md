# awesome-va-skills

中文 | [English](README.en.md)

面向 vLLM-Ascend / Ascend 推理工程的技能合集，目录结构与公司
`awesome-mindie-skills` 统一：分类元数据、固定来源版本、中英目录及审阅证据。
新的独立池化包在 `skills/ascend-memcache-pooling/`；旧技能和共享工具保持完整工作区布局。

归档共 30 个完整包；目录只收录许可已明确的包，4 个历史导入暂留归档待核实。
原工作区未提交的 Leaf-Spine 和 vendor 草稿保持原样，不进入本次公共贡献。
安装、目录对应与兼容边界见 [布局说明](docs/collection-layout.md)。

```bash
git clone https://github.com/Yuli-yx/awesome-va-skills.git
cd awesome-va-skills
python -m pip install -r requirements.txt
python scripts/validate_catalog.py
python scripts/render_catalog.py --check
```

定义审阅和离线工具测试不代表 NPU 部署、SSD 回读或性能验收通过。
来源及版权见 [ATTRIBUTION](ATTRIBUTION.md) 和 [完整包清单](skills-manifest.json)。

<!-- CATALOG:START -->

26 个技能 · 8 个分类

定义已审阅：26 · 已有运行复现记录：0。具体范围见各条目记录。

| 来源项目 | 已收录 | 维护者 | 许可证 |
|---|---|---|---|
| [va-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 16 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | MIT |
| [va-hixl-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 5 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | CANN-2.0 |
| [va-apache-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 4 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | Apache-2.0 |
| [va-pooling-workflows](https://github.com/Yuli-yx/awesome-va-skills) | 1 | Yuli-yx collection; original authors credited in ATTRIBUTION.md | CC0-1.0 AND MIT |

- [环境与依赖](#environment)
- [模型接入与转换](#model-integration)
- [服务部署与扩展](#serving)
- [正确性与精度](#correctness)
- [性能评测与回归](#benchmarking)
- [Profiling 与瓶颈分析](#profiling)
- [故障诊断](#debugging)
- [工程交付与运行维护](#delivery)

<a id="environment"></a>

### 环境与依赖

检查驱动、CANN、框架配套、容器和设备环境。

- [machine-management](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/machine-management/SKILL.md) — 接入、验证和修复远端 NPU 主机
  `Ascend` `vLLM Ascend` `设备取决于检查项` `流程编排` · [条目](catalog/skills/machine-management.yaml)
- [remote-code-parity](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/remote-code-parity/SKILL.md) — 核对本地与远端执行源码一致性
  `Ascend` `vLLM Ascend` `主机工具` `流程编排` · [条目](catalog/skills/remote-code-parity.yaml)
- [remote-toolbox](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/remote-toolbox/SKILL.md) — 执行远端任务、同步、服务与产物操作
  `Ascend` `vLLM Ascend` `主机工具` `流程编排` · [条目](catalog/skills/remote-toolbox.yaml)
- [repo-init](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/repo-init/SKILL.md) — 初始化工作区、GitHub 与源码子模块
  `Ascend` `vLLM Ascend` `主机工具` `流程编排` · [条目](catalog/skills/repo-init.yaml)
- [session-management](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/session-management/SKILL.md) — 创建与管理隔离开发会话和资源租约
  `Ascend` `vLLM Ascend` `主机工具` `流程编排` · [条目](catalog/skills/session-management.yaml)
- [vllm-ascend-build](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-build/SKILL.md) — 构建固定版本并核对远端运行路径
  `Ascend` `vLLM Ascend` `主机工具` `流程编排` · [条目](catalog/skills/vllm-ascend-build.yaml)

<a id="model-integration"></a>

### 模型接入与转换

接入模型、转换权重，并核对配置与输入输出。

- [main2main](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/main2main/SKILL.md) — 分析并适配 vLLM 主线兼容性变化
  `Ascend` `vLLM Ascend` `离线分析` `流程编排` · [条目](catalog/skills/main2main.yaml)
- [modelscope](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/modelscope/SKILL.md) — 下载、续传和校验 ModelScope 权重
  `Ascend` `vLLM Ascend` `主机工具` `流程编排` · [条目](catalog/skills/modelscope.yaml)
- [vllm-ascend-model-adapter](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-model-adapter/SKILL.md) — 适配与调试 Ascend 上的 vLLM 模型
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/vllm-ascend-model-adapter.yaml)

<a id="serving"></a>

### 服务部署与扩展

部署共置或 PD 分离服务，验证拓扑、端点与请求。

- [ascend-memcache-pooling](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/skills/ascend-memcache-pooling/SKILL.md) — 部署 A3/A5 DRAM/SSD 池化，核对 P/D 与 Host RoCE，并监控多 DP 前缀复用
  `Ascend` `vLLM Ascend` `MemCache` `SSD` `执行需 NPU` `流程编排` · [条目](catalog/skills/ascend-memcache-pooling.yaml)
- [vllm-ascend-serving](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-serving/SKILL.md) — 启动、检查与清理归属明确的推理服务
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/vllm-ascend-serving.yaml)

<a id="correctness"></a>

### 正确性与精度

固定参考与用例矩阵，比较输出、误差和任务质量。

- [aisbench-accuracy](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/aisbench-accuracy/SKILL.md) — 执行数据集精度评估与采样配置对齐
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/aisbench-accuracy.yaml)

<a id="benchmarking"></a>

### 性能评测与回归

通过预热、重复测量和受控对比评估吞吐与延迟。

- [aisbench-pd-benchmark](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/aisbench-pd-benchmark/SKILL.md) — 准备并执行 AISBench 重复前缀与 P/D 性能评测
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/aisbench-pd-benchmark.yaml)
- [pd-pure-role-benchmark](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/pd-pure-role-benchmark/SKILL.md) — 验收纯 P、纯 D 容量和端到端稳态 QPS
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/pd-pure-role-benchmark.yaml)
- [vllm-ascend-benchmark](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-benchmark/SKILL.md) — 测量在线推理性能并保留原生结果
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/vllm-ascend-benchmark.yaml)

<a id="profiling"></a>

### Profiling 与瓶颈分析

采集或分析 trace、逐 rank 行为与 HBM 占用，保留证据。

- [ascend-memory-profiling](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/ascend-memory-profiling/SKILL.md) — 采集和归因推理服务的 HBM 占用
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/ascend-memory-profiling.yaml)
- [ascend-profiling-analysis](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/ascend-profiling-analysis/SKILL.md) — 分析算子、step、layer 和跨 rank profiling
  `Ascend` `vLLM Ascend` `离线分析` `流程编排` · [条目](catalog/skills/ascend-profiling-analysis.yaml)
- [ascend-profiling-collection](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/ascend-profiling-collection/SKILL.md) — 采集单次 Ascend torch profiler 工作负载
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/ascend-profiling-collection.yaml)

<a id="debugging"></a>

### 故障诊断

缩小启动、通信、图执行和算子异常的复现范围并验证修复。

- [debugging-vllm-ascend-pd-accuracy](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/debugging-vllm-ascend-pd-accuracy/SKILL.md) — 定界 P/D 输出精度差异并执行对照
  `Ascend` `vLLM Ascend` `执行需 NPU` `流程编排` · [条目](catalog/skills/debugging-vllm-ascend-pd-accuracy.yaml)
- [driver-peermem-check](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/driver-peermem-check/SKILL.md) — 检查驱动包的 peer-memory 支持
  `Ascend` `HIXL` `离线分析` `流程编排` · [条目](catalog/skills/driver-peermem-check.yaml)
- [hixl-troubleshoot](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-troubleshoot/SKILL.md) — 定界 HIXL/ADXL 建链与传输失败
  `Ascend` `HIXL` `执行需 NPU` `流程编排` · [条目](catalog/skills/hixl-troubleshoot.yaml)

<a id="delivery"></a>

### 工程交付与运行维护

将变更映射到构建、正确性和性能验证，记录覆盖范围。

- [hixl-pr-review](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-pr-review/SKILL.md) — 按 HIXL 规则检视代码变更
  `Ascend` `HIXL` `离线分析` `流程编排` · [条目](catalog/skills/hixl-pr-review.yaml)
- [hixl-srs-doc-generator](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-srs-doc-generator/SKILL.md) — 编写和评审 HIXL 需求规格设计
  `Ascend` `HIXL` `离线分析` `流程编排` · [条目](catalog/skills/hixl-srs-doc-generator.yaml)
- [hixl-ut-generator](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/hixl-ut-generator/SKILL.md) — 生成与现有风格一致的 HIXL 单元测试方案
  `Ascend` `HIXL` `离线分析` `流程编排` · [条目](catalog/skills/hixl-ut-generator.yaml)
- [vllm-ascend-release-note-writer](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-release-note-writer/SKILL.md) — 整理版本说明与发布记录
  `Ascend` `vLLM Ascend` `离线分析` `流程编排` · [条目](catalog/skills/vllm-ascend-release-note-writer.yaml)
- [vllm-ascend-release](https://github.com/Yuli-yx/awesome-va-skills/blob/7d3aa5f3b55049a2f917b4ca682c1e9963033c18/.agents/skills/vllm-ascend-release/SKILL.md) — 组织 vLLM Ascend 发布检查和交付
  `Ascend` `vLLM Ascend` `离线分析` `流程编排` · [条目](catalog/skills/vllm-ascend-release.yaml)

<!-- CATALOG:END -->
