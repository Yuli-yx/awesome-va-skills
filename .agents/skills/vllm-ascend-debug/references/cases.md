# 案例索引：用于提出假设

以下为历史调测资料的去现场化摘要，整理于 2026-09-14。不是当前部署结论，也不是可直接运行的复现包。只查相关条目；需要定案时取得该现场版本和原始证据，不能用案例替代验证。

| 条目 | 检索线索 | 主要用途 |
|---|---|---|
| C01 | v0.23、提前拒绝、empty receive、delay free | 区分接收任务创建前后的清理 |
| C02 | Qwen3.5、空 metadata、Mamba OOB、P assert | 区分机制链与具体请求时序 |
| C03 | v0.26、DSpark、IndexCheck、discard | 回溯非法索引的生产者 |
| C04 | malformed chunk footer、GPQA、乱码 | 区分协议损坏与生成/评分问题 |
| C05 | 固定并发、高缓存命中、短输出 | 区分交接成本与峰值容量 |
| C06 | A5、某 P 卡失败、健康 P→同一 D 成功 | 设计有区分力的卡对矩阵 |
| C07 | 容器映射、物理 ID、endpoint | 核对真实设备与配置 |

## C01：准入前未建立接收任务

历史 v0.23 分支曾存在 D 在 `update_state_after_alloc` 前拒绝/取消后，没有 receive task 进入 worker `finally` 的清理缺口。相关修复通过 empty receive 接入完成通知路径，公开线索为 [PR #15239](https://github.com/vllm-project/vllm-ascend/pull/15239)。

可迁移判断：查任务是否创建、通知是否发送/处理/汇聚及 scheduler 是否释放。补齐路径不是通知可靠必达保证。验证同类问题时控制准入前后的事件顺序；这里没有附带已运行的最小复现。

## C02：空 metadata 与迟到终结

Qwen3.5 历史分析中，Mamba 远端 block 列表为空/过短导致 D 侧索引越界；P 异步输出、抢占和请求删除与迟到完成之间存在生命周期竞态线索。

关键反例：某份日志里 P assert 早于被怀疑的 D OOB，不能把后者当作前者的直接原因。代码能说明异常后仍可能发 DONE，但还缺 assert 所属 request ID。源头竞态补丁当时只有静态检查，不能称 NPU 闭环。

可迁移判断：追 metadata 生产、有效长度和 step 所有权；分别核对首错与后续节点失败；不要为避免 P assert 全局去掉 D 的清理通知。

## C03：校验报错不是输入生产根因

历史 v0.26 DSpark 分析逐值重建了 async discard 后有效采样为零、负位置索引及随后展开的非法 draft positions。IndexCheck 是暴露点；后续同步失败与断连属于级联。公开修复线索为 [PR #16153](https://github.com/vllm-project/vllm-ascend/pull/16153)，需按目标版本核对 diff。

故障 step 的 connector metadata 没有活跃传输，结合本地输入生成证据支持 DSpark/async 路径定界；单独“无活跃传输”不证明所有历史 KV 输入无影响。该例为历史静态证据闭环，不声称随包提供真实复现。

## C04：协议字节改变与精度下降分开

历史 DSV4 直连实验在双端同一 TCP 流、对应 sequence 上发现不同 payload，且客户端错误与损坏 chunk footer 对应。结论限定为两个观察点之间发生字节改变，具体 driver/offload/硬件未闭环。

另一次混部评测的失败表现为答案选择错误与超长输出没有最终答案，没有对应协议错误；不能合并归因。可迁移方法是同流双端对照、逐样本失败模式和分离的单变量实验，而不是直接关闭某个网卡选项作为通用修复。

## C05：PD 交接占用请求槽位

历史固定并发、高 prefix 命中、极短输出对照中，PD 的端到端耗时更长、吞吐更低；两组样本数也不同。

可迁移判断：交接成本可能在这种负载下突出，测试启动/排空也影响均值；端到端时差不是纯 KV 时间，固定并发差异不能外推充分流水下的峰值容量。按 [性能定界](performance.md) 重建可比基线。

## C06：卡对矩阵定位服务态建链

历史 A5 实验中某 P 卡对多个 D 失败，健康 P 对同一 D 成功；控制面与裸通信检查未暴露对应故障，进一步证据收敛到该 P 卡服务态建链路径。

可迁移方法：用有区分力的卡对矩阵配合双端通信证据；不能仅凭矩阵认定物理卡损坏，也不能把裸 RDMA 通过当作服务态正常。

## C07：可见序号不是宿主物理 ID

历史容器映射分析区分了绑定设备与查询宿主物理 ID；读取按物理 ID 命名的 endpoint 文件时，仅按 `local_rank` 或可见设备列表推断可能选错。

可迁移方法：取得目标版本提供的实际 user/visible→physical 映射并核对 endpoint；平台代码中可搜索 `visible_device_id_to_physical_device_id` 和 `aclrtGetPhyDevIdByUserDevId` 作为候选入口，不假设每个部署都提供或已使用它们。
