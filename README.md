# awesome-va-skills

面向 **vLLM-Ascend / Huawei Ascend NPU** 的 Agent Skills 合集。覆盖开发、部署、远端管理、性能与精度评测、profiling、P/D 调测、Mooncake/HIXL/HCCL 通信和版本维护。

本仓库收集了 **28 个 skill 包**，保留 `SKILL.md`、脚本、参考资料、模板和 Agent 元数据。收集日期：2026-10-14。

## 技能目录

| 方向 | Skill | 用途 |
| --- | --- | --- |
| 环境 | [repo-init](.agents/skills/repo-init/SKILL.md) | 工作区初始化、GitHub 与子模块拓扑 |
| 环境 | [machine-management](.agents/skills/machine-management/SKILL.md) | 接入、验证、修复和移除远端 NPU 主机 |
| 环境 | [session-management](.agents/skills/session-management/SKILL.md) | 隔离工作区、容器和资源租约 |
| 环境 | [remote-toolbox](.agents/skills/remote-toolbox/SKILL.md) | 远端任务、同步、服务和产物工具 |
| 环境 | [remote-code-parity](.agents/skills/remote-code-parity/SKILL.md) | 本地与容器代码一致性 |
| 模型 | [modelscope](.agents/skills/modelscope/SKILL.md) | ModelScope 权重下载、续传与校验 |
| 开发 | [vllm-ascend-build](.agents/skills/vllm-ascend-build/SKILL.md) | 固定版本构建、原生依赖与运行路径校验 |
| 开发 | [vllm-ascend-model-adapter](.agents/skills/vllm-ascend-model-adapter/SKILL.md) | 模型适配与调试 |
| 开发 | [main2main](.agents/skills/main2main/SKILL.md) | 适配 vLLM 主线变化和定位兼容性 CI 失败 |
| 服务 | [vllm-ascend-serving](.agents/skills/vllm-ascend-serving/SKILL.md) | 启停、检查服务与进程归属标识 |
| 评测 | [vllm-ascend-benchmark](.agents/skills/vllm-ascend-benchmark/SKILL.md) | 在线服务性能测试 |
| 评测 | [aisbench-pd-benchmark](.agents/skills/aisbench-pd-benchmark/SKILL.md) | AISBench 与两端 P/D 性能测试 |
| 评测 | [aisbench-accuracy](.agents/skills/aisbench-accuracy/SKILL.md) | 数据集精度与回归对照 |
| Profiling | [ascend-profiling-collection](.agents/skills/ascend-profiling-collection/SKILL.md) | 采集 Ascend torch profiler 数据 |
| Profiling | [ascend-profiling-analysis](.agents/skills/ascend-profiling-analysis/SKILL.md) | 算子、step、layer 和跨 rank 分析及报告 |
| Profiling | [ascend-memory-profiling](.agents/skills/ascend-memory-profiling/SKILL.md) | HBM 占用采集与归因 |
| 调测 | [vllm-ascend-debug](.agents/skills/vllm-ascend-debug/SKILL.md) | P/D 功能、精度、性能与资源生命周期定界 |
| 调测 | [debugging-vllm-ascend-pd-accuracy](.agents/skills/debugging-vllm-ascend-pd-accuracy/SKILL.md) | P/D 精度异常的远端诊断与对照实验 |
| DFX | [pd-dfx-workbench](.agents/skills/pd-dfx-workbench/SKILL.md) | P/D DFX 台账、诊断缺口与覆盖映射 |
| 通信 | [compile-mooncake](.agents/skills/compile-mooncake/SKILL.md) | Ascend Direct Mooncake 构建与安装 |
| 通信 | [hccl-auto-test](.agents/skills/hccl-auto-test/SKILL.md) | HCCL 单机、多机打流与环境验收 |
| 通信 | [hixl-troubleshoot](.agents/skills/hixl-troubleshoot/SKILL.md) | HIXL/ADXL 建链和传输问题诊断 |
| 通信 | [driver-peermem-check](.agents/skills/driver-peermem-check/SKILL.md) | 驱动包与 npu_peermem RDMA 支持检查 |
| HIXL 开发 | [hixl-ut-generator](.agents/skills/hixl-ut-generator/SKILL.md) | HIXL 单元测试生成 |
| HIXL 开发 | [hixl-pr-review](.agents/skills/hixl-pr-review/SKILL.md) | HIXL PR 代码检视 |
| HIXL 开发 | [hixl-srs-doc-generator](.agents/skills/hixl-srs-doc-generator/SKILL.md) | HIXL 需求规格文档 |
| 发布 | [vllm-ascend-release](.agents/skills/vllm-ascend-release/SKILL.md) | 发布检查、版本引用、发布说明和公告 |
| 发布 | [vllm-ascend-release-note-writer](.agents/skills/vllm-ascend-release-note-writer/SKILL.md) | 历史版本发布说明写作流程 |

## 使用方式

每次先阅读目标包的 `SKILL.md`，按需加载其参考资料。任务涉及实际模型推理、构建或 NPU 测试时，需要远端 Ascend 容器和兼容的 CANN、torch、torch_npu 环境。收集与静态验证不代表 NPU 运行验证。

### 集成到开发工作区

```bash
git clone https://github.com/Yuli-yx/awesome-va-skills.git
```

将需要的 skill 包放入目标工作区 `.agents/skills/`。部署、远端管理等包使用工作区相对路径，并依赖 `.agents/lib/`、`.agents/scripts/` 和 `.remote-dev/`：这些目录应作为完整布局集成。集成到已有工作区时先检查差异，避免覆盖已有工具。目标工作区仍需准备 `vllm/` 和 `vllm-ascend/` 源码，本合集不携带源码子模块、容器或模型。

独立资料型 skills 可单独复制到 Agent 的用户技能目录。带共享脚本依赖的 skills 应保持上述工作区布局，不宜仅复制 `SKILL.md` 或孤立安装到用户技能目录。

根据运行的脚本安装本地工具依赖，例如 Python 3.10+、PyYAML、SSH、Git、GitHub CLI；profiling 分析和精度诊断的部分脚本还需 pandas、numpy、openpyxl、requests 或 paramiko。具体以各包的入口和依赖说明为准。

### 远端连接与本地状态

优先通过 `.remote-dev/tools/` 的结构化入口使用显式 `host`、`port`、`user` 参数。可将 `.remote-dev/endpoints.example.json` 复制为本地 `.remote-dev/endpoints.json` 后填入个人端点；该文件已忽略。不要提交密码、token、机器清单或进程所有者配置。

本地状态写入 `.vaws-local/`、`.remote-dev/state/`；实验和运行产物放入 `experiments/` 或 `artifacts/`。以上路径均已忽略。

身份标识见 [process-ownership.md](.agents/skills/vllm-ascend-serving/references/process-ownership.md)：设置 `VLLM_PROCESS_NAME_PREFIX=<owner-id>`，在宿主机核实进程名称和归属。DFX skill 需要用户提供自己的工作簿；本仓库不含台账数据。

## 收集规则与来源

- 同名 skill 按包去重，工作区维护的规范包优先；工具适配器和旧 worktree 副本不重复收录。
- HIXL 开发包作为 Ascend 通信配套能力收录；普通办公、前端、通用 Agent 和 CUDA/Triton 专用包不在范围内。
- 原包完整保留，导出副本中个人台账路径和现场地址示例已通用化。源目录没有修改。
- 导出时修正了 3 处 frontmatter 格式：过长 description、description 中的箭头字符和非规范 skill 名称；补齐了 main2main 引用的版本策略文档，修正了历史发布包的资源路径。
- 包来源、许可证信息和导出调整见 [skills-manifest.json](skills-manifest.json)。来源工作区为 [vllm-ascend-workspace](https://github.com/Yuli-yx/vllm-ascend-workspace)，模型适配和发布相关包来自本机 vLLM-Ascend checkout；HIXL 配套包来自本机 HIXL 源码包，其他包来自本机已安装 skills。
- 原有包中的平台、版本、工具或路径约定需结合目标环境核对；特别是模型适配和历史发布包保留了原工作流约定。

## 许可证

这是多来源合集，各包保留原有版权和许可证。`LICENSES/` 包含来源工作区的 MIT、vLLM-Ascend 的 Apache-2.0 和 HIXL 的 CANN 2.0 文本。未明确声明许可证的本地包在清单中标为 `unspecified`，本合集不为这些文件追加或推定授权。

## 本次验证范围

28 个 skill 的 frontmatter 与命名检查通过；159 个 Python 文件通过语法检查；服务启动、远端命令和目标解析入口通过本地 `--help` 加载检查。真实环境连接、NPU 推理、通信、精度和性能尚未在此合集上验证。
