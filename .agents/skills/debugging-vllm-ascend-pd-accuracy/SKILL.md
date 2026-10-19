---
name: debugging-vllm-ascend-pd-accuracy
license: MIT
description: Use when vLLM Ascend 的 Prefill/Decode 分离出现复读、乱码、截断、首 token 偏差、PD 与非 PD 输出不一致，或全量模型异常而减层模型正常；适用于 KV transfer、Mooncake、外部 DP、多机 TP/DP、ACL Graph、Decode logits 和 NPU 精度问题的全自动远程诊断。
---

# vLLM Ascend PD 精度调试

本包由 Yuli-yx 维护，为用户确认的自有工作流，采用 MIT；分发时保留完整包与[许可证](LICENSE)。

这是一个**证据优先、单变量、可恢复**的远程诊断 Skill。它只在用户明确授权“开始执行”后操作远程环境；默认从项目 `.venv` 运行 Python，所有远程写操作限制在指定容器内。

## 触发与硬性规则

- 触发条件：PD 分离精度下降、Decode 复读、P/D/proxy 输出不一致、KV Cache 传输怀疑、全量模型与减层模型行为不同。
- 未收到明确启动授权时，只能设计 SOP、检查本地文件和生成配置，**不得 SSH、curl、重启服务或容器**。
- 远程操作前必须保存进程命令、环境、版本、源码/模型哈希和容器信息。
- 只允许操作 inventory 中的精确容器名；不得用模糊 `docker ps` 结果操作其他容器。
- 允许在目标容器内启停 vLLM；端口残留或孤儿进程无法清理时，才允许 `docker restart <精确容器名>`。
- 不修改宿主机配置、镜像、模型原文件或其他容器；插桩使用容器内 `/tmp` overlay，并保证异常时回滚。
- 不把 SSH 密码写入 Skill、配置、日志、Git 或报告；使用运行时环境变量、SSH key 或内存传递。

## 标准流程

1. **门禁与发现**：验证用户授权、SSH、精确容器、NPU、服务进程和网络；从实际命令自动识别 P/D、DP/TP/rank、KV role、端口和模型。
2. **快照**：记录版本、editable location、真实模块路径、cwd/sys.path、关键环境变量、模型配置、权重索引、Mooncake 配置、日志和显存状态。
3. **复现**：等待所有 rank 健康后，使用 `temperature=0` 的固定请求；P、D、proxy 和每个 DP rank 至少重复 3 次，保存原始响应和 token/logprob 信息。
4. **对照矩阵**：一次只改变一个变量，依次检查 DP rank、D eager/graph、KV block 复用、PD/非 PD、减层/全量和并发条件。
5. **边界定位**：先比较 token/metadata，再按需对 KV 发送前后做逐层抽样 fingerprint；若 KV 一致，继续跟踪 Decode input、logits、sampler 和首次偏差 token。
6. **根因确认**：每个假设必须有证据、最小改动、预期和实际结果；连续 3 个假设未证实时停止猜测，回到取证阶段。
7. **恢复与报告**：停止诊断进程，清理 overlay；必要时精确重启目标容器；恢复原服务并验证健康；输出实验账本、首次偏差位置、证据和未决假设。

详细步骤见 `references/sop.md`；inventory/case 格式见 `references/config-schema.md`；KV 指纹策略见 `references/instrumentation.md`。远程并发探针和容器安全操作使用 `scripts/remote_orchestrator.py`，确定性 HTTP 复现使用 `scripts/run_requests.py`，输出比较使用 `scripts/analyze_responses.py`。

## 运行时输入

机器、精确容器名、模型、请求和授权范围由本次 inventory/case 提供，不从历史案例推断。服务未完全拉起时停在“就绪检查”，不发送推理请求。

优先使用已配置的 MindIE remote-dev companion 工具。包内 inventory 脚本是独立部署的兼容入口，不要求将项目改回旧脚手架。连接与重启须在用户已授权的目标和范围内执行。
