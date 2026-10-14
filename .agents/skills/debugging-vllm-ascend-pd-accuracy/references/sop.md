# 标准操作流程（SOP）

## 0. 双重门禁

- “确认 SOP/创建 Skill”只允许本地写文件和静态验证。
- 只有用户明确说“开始执行远程诊断”才允许连接服务器。
- 远程服务未就绪时只轮询健康状态；超时后生成报告，不盲目重启。

## 1. 操作边界

每个远程动作都必须满足：

1. SSH 主机来自 inventory；
2. `docker ps --format '{{.Names}}'` 中存在且**精确等于**目标容器名；
3. 进入容器的写入路径仅为 `/tmp/vllm_pd_accuracy_debug/<run_id>`；
4. 不执行宿主机文件写入、系统配置修改、镜像修改、模型删除或其他容器操作。

允许的容器重启命令只有：

```bash
docker restart --time 30 pd_kimi_zyx
```

执行前必须再次确认精确名称和容器 ID；执行后重新检查容器 ID、挂载、NPU 数量、进程命令和服务健康。不能使用 `docker restart $(...)`、模糊 name filter 或按前缀匹配。

## 2. 发现与快照

并发读取每个容器：

- 容器 image ID、hostname、挂载和设备；
- vLLM 主进程完整 argv、cwd、selected environment；
- `kv_role`、KV connector、Mooncake port；
- DP/TP/EP size、rank、RPC 地址；
- vLLM/vLLM Ascend/torch/torch-npu/CANN 版本；
- editable project location、模块 `__file__`、Git commit；
- model config、权重 index 和 tokenizer 文件哈希；
- `/dev/davinci*` 数量、NPU 内存、关键日志；
- `/home` 同名目录和 `PYTHONPATH`，防止错误 import 结论。

Python 探针从 `/tmp` 执行，并同时记录 `pip show` 与实际模块路径。探针结果不能单独证明服务进程已加载某个源码版本。

## 3. 就绪与复现

使用条件轮询，不使用固定 sleep：

1. 所有预期 rank 出现；
2. DP/RPC 和 KV connector 日志完成注册；
3. 内部 endpoint 和用户提供的 proxy endpoint 可连接；
4. `/health`、`/v1/models` 或等价检查成功；
5. 连续两次检查稳定。

复现请求必须包含固定模型、prompt、`temperature=0`、有界 `max_tokens`。每个路径至少运行 3 次，记录原始 HTTP、响应体、耗时、token/logprob、finish reason 和服务端 rank。

## 4. 实验顺序

一次只改变一个变量，并在每项实验前保存命令和配置：

1. 按 DP rank 分组比较；
2. D 侧 graph 与 eager 对照；
3. 首请求与后续请求对照，检查 block reuse/残留状态；
4. 单请求与受控并发对照；
5. PD 与非 PD 基线；
6. 已知减层模型与全量模型；支持时对层数做二分；
7. 仅对可疑 layer/rank 做 KV fingerprint 和 Decode logits 追踪。

每次实验结束后先比较结果，再决定下一项，不允许同时改 max-num-seqs、graph、dtype、并行度和 KV 配置。

## 5. 停止与恢复

以下情况立即停止当前实验并保留证据：容器身份不匹配、NPU 数量变化、模型路径变化、rank 缺失、服务健康检查失败、日志出现新的致命错误、3 个假设均未证实。

清理顺序：停止本次启动的 vLLM 进程 → 删除 `/tmp` overlay → 恢复原命令/环境 → 必要时精确重启目标容器 → 等待健康 → 再验证一次原始请求。无论异常类型如何，报告都必须注明恢复成功或失败。

## 6. 输出

本地报告至少包含：

- run id、时间、inventory 脱敏副本；
- 拓扑和版本一致性表；
- 原始请求和响应摘要；
- 每项实验的单变量 ledger；
- 首次偏差的阶段/layer/rank/token；
- KV fingerprint 对比；
- 根因证据、修复验证和恢复状态；
- 未决假设与下一步建议。

密码、token、完整 secret environment 和私钥路径不得进入报告。
