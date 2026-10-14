# PD 请求与 KV 生命周期

用于判断请求阶段、等待对象与资源归属。以下以 Mooncake V1 普通 pull 为例；缓存命中、layerwise、hybrid、不同代理与版本会改变路径。

## 两条关联的进度链

执行：proxy 路由 → P 准入/排队 → 所需 prefill 完成并交接 metadata → D 准入/分配 → 接收任务 → metadata/建链/pull/必要转换 → 接收结果回报 → D 调度、计算与输出。

资源：P 生成交接信息时保留相关块（delay free）→ D 接收任务终结并尝试通知 → P 处理通知并汇聚计数 → worker 回报 → P scheduler 解除请求对块的持有。异常或全缓存命中可不传数据而仍走清理路径。

两条链不要强行拼成一条严格全序；D 继续计算与 P 的后续释放可分别推进。Pull 中 `finished_sending` 是 producer 侧终结回报，不表示 P 执行过主动 push；有些实现也把超时终结合并进该集合。

## 逐阶段查什么

| 问题 | 证据与源码搜索入口 |
|---|---|
| P 是否做完？ | 同请求的 token/调度进度、终态、交接 metadata；`request_finished` / `request_finished_all_groups` |
| D 是否接受并建任务？ | API 准入、`do_remote_prefill`、本地块分配、`update_state_after_alloc`、待接收集合 |
| 任务是否到 worker？ | `build_connector_meta`、`start_load_kv`、接收队列、实际消费的 request ID |
| 等在何处？ | `WAITING_FOR_REMOTE_KVS` 之外继续区分 metadata、建链、pull、布局转换、task 汇聚、结果回报 |
| D 是否可继续？ | `finished_recving`、`invalid_block_ids` / load errors、错误策略、scheduler 后续 step |
| P 为什么未释放？ | delay-free 起点、预期/已完成端口和 rank 数、DONE 发送/收到/ACK、`finished_sending`、`_free_blocks` |

相关实现通常位于 `vllm_ascend/distributed/kv_transfer/kv_p2p/`、`vllm/v1/core/sched/scheduler.py` 及实际 proxy。用符号定位，不依赖旧行号；还需追当前运行时加载的 patch 或 scheduler 子类。

## 不同证据的含义

- HTTP 2xx 或收到响应头不是端到端完成，后续可能中断或返回空内容。
- `Delaying free` 通常是正常保留；检查停留时长、持有原因与结束条件后再判断泄漏。
- DONE 可来自成功、失败或 empty receive。代码存在 `finally` 不能覆盖尚未入任务、进程退出或卡死。
- 发送尝试、P 处理、ACK、所有端口汇聚、scheduler 释放分别取证；单条 ACK 不证明全部完成。
- 超时 tracker 的“force freed”日志可能早于 scheduler 实际处理。释放请求持有也不等于进程 HBM 占用下降。
- 示例 proxy 的 `release_prefill_kv` 可能只释放负载计分，必须读函数确认含义。
- 接收完成还要核对 load error 与 KV 消费；不能据此证明数值正确。

## 根据现场展开异常分支

| 触发 | 检查的边界 |
|---|---|
| D 准入前拒绝/取消 | 是否创建清理任务；该版本有无 empty receive；P 是否仍等待 |
| 接收过程中失败/取消 | 失败块与完成回报、剩余异步任务、远端资源清理是否分别推进 |
| 全 prefix 命中或空 blocks | 无需传数据的合法路径与异常缺失 metadata 区分 |
| P 抢占、异步输出返回 | block table 所有权、输出所属 step、旧输出是否命中新的请求状态 |
| 多端口/多 rank | 期望计数、部分成功、重复或迟到通知是否可识别 |
| proxy retry/recompute | attempt 与 P/D request 映射；逻辑请求的新旧资源是否分开 |
| load failure | 按现场 `kv_load_failure_policy`、scheduler 和 Graph 约束追踪；不默认 D 完整重算可行 |
| 节点退出/超时 | 首个失去推进能力的节点、未终结任务、正常清理与超时兜底 |

输出时可以用“已证实到 X；Y 未知；目前等待 Z 的证据是……”。缺少身份映射时不要把相邻日志连成同一请求因果。
