# 低扰动异步采证

用于同步打印掩盖故障，或观察异步 KV、slot、position 和 buffer 复用。这里提供设计约束与选择方法，没有可直接运行的通用 NPU dump helper。

## 选择需要观察的量

先用 CPU 上已有的 request/step、shape、dtype、有效范围和 metadata 缩小范围，再按假设采少量设备值或统计量。设备值打印、`.item()`、搬到 CPU、字符串格式化等应核查实际执行路径；把 logger 放进线程不自动消除采集时的同步。

先确定观察对象属于哪个请求、step、rank、layer/group/component、逻辑 token/slot，以及期望采样边界。仅传 tensor 引用给后台任务不等于得到该时刻的快照。

## 可采用的异步路径

```text
确定采样边界和身份
  → 在明确所有权下取得独立样本或摘要
  → 异步搬到独立主机 buffer
  → 完成事件就绪后解释与输出
  → 异步使用结束后回收资源
```

可以在独立统计 stream 上计算、在 copy stream 上搬运，用完成 event 查询后延迟打印；具体 stream、pinned memory 和 API 按目标 PTA/CANN 与 Graph 模式验证。`non_blocking=True` 不证明全路径无同步。

不要为了取得日志在推理热路径新增全设备同步。需要局部依赖以保证样本正确时明确记录，并测量它是否改变复现条件；无法同时保真和低扰动时说明取舍。

## 采样一致性比异步输出更重要

统计 stream 等待生产 stream 只覆盖先前提交的生产任务，不阻止后续 step 或其他 stream/通信引擎原地改写 KV。持有对象引用也不阻止内容更新。

需要精确快照时，在生产结束和下一次改写之间复制必要的小样本到独立缓冲区；依赖要覆盖真实写入者，保证样本在统计和搬运期间不被复用。CPU metadata 同样固化必要字段。跨 stream 的 allocator 生命周期与写入排序是两个问题，都要核对。

若只能尽力采样，标注可能与写入重叠，不能称为目标 step 的完整快照。Graph replay 下更要核对实际可插桩边界，不默认 Python 代码每个 replay 都执行。

CPU 读取必须在对应搬运完成后。丢弃日志不代表异步操作停止；直到在途使用结束才允许释放或复用 buffer。异步日志输出时间不等于采样时间。

## 解释采样结果

- 保存 request/attempt、step/rank、逻辑位置、布局与有效范围；物理 slot 观察还需所有者/复用代次。
- 同一 slot 下一步变化可能是合法复用、释放或滑窗更新，不能直接认定被覆盖。
- 均值/方差用于筛查，不能证明内容相同；需要时对齐逻辑数据并比较有限值或更强校验。
- 显式处理无效 slot、NaN/Inf 和 padding，不能把它们混入“正常统计”。
- 按实际 KV spec 适配维度和 component，普通 K/V 假设不通用于 Mamba、压缩或量化布局。不支持则说明未采集。

## 控制开销并保留缺失信息

分别约束实际统计元素数、采样层数/频率、在途 buffer 数和总字节数；输出很短也可能执行大量设备计算。预分配缓冲池可以减少热路径分配，但必须管理占用与完成状态。

积压时采用明确的丢弃/降采样策略并计数，不静默截断，也不让日志队列长期阻塞推理。记录已采集、已输出、丢弃和未完成数量；最后一份记录、服务退出或设备错误时采用有界 drain 或报告不完整，不无限等待日志。

## 参考实现与适用边界

参考 [freyfwt 提交 9481cf7](https://github.com/freyfwt/vllm-ascend/commit/9481cf743460a9f6b22795a18d757af4aee9a562)，文件 `vllm_ascend/worker/model_runner_v1.py`。它使用统计/copy stream、event 查询、pending 延迟打印、请求/slot 关联及前一步 slot 观察，可搜索 `AsyncNPUModelRunnerOutput`、`try_log_kv_cache_stats`、`_make_debug_kv_cache_snapshot`。

该提交没有独立后台日志线程；对后续源写入的保护不能只由单向 wait_stream 推出。其 token 样本数上限不等于整体统计元素上限，pending 截断和布局假设也需重新设计。只借鉴机制，不直接移植大段 runner 代码。

## 验证

结合 [最小复现](reproduction.md)，对比不开采证、CPU 元数据采证和设备异步采证的失败频率、负载、延迟与内存；同步打印可作为已知扰动对照。故障消失不证明修复或零开销。

验证逐 step 已知值变化、buffer 重用、慢搬运、队列满、最后一份记录和退出路径，检查身份与数据是否对应、是否过早读/复用。真实 Ascend 运行前只称设计或待验证插桩，不宣称采证无扰动。
