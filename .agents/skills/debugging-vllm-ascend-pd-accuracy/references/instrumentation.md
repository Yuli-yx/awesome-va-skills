# KV 与 Decode 插桩策略

## 目标

判断偏差第一次出现于：P 计算、KV 发送、KV 接收/block mapping、attention、Decode graph、logits 还是 sampler。

## 分层升级

1. **元数据**：request ID、DP/TP rank、layer、token range、block ID、slot mapping、shape、dtype、layout、完成事件。
2. **轻量 fingerprint**：首/中/尾位置抽样，计算有限性、sum、absmax 和固定采样哈希；默认不把完整 NPU KV 拷贝到 CPU。
3. **局部扩大**：只有元数据或轻量 fingerprint 不一致时，扩大到对应 layer/rank/request。
4. **Decode 跟踪**：比较 D 的首个 input token、position、block table、top-k logits 和 sampler token。

## 实现要求

- 插桩必须通过容器内 `/tmp/vllm_pd_accuracy_debug/<run_id>/overlay` 或运行时 hook 注入，不直接改 editable 源码。
- 插桩日志使用 JSONL，字段固定且包含 run id、request id、rank 和 layer。
- 同一请求的 P 发送记录和 D 接收记录必须可关联；不能只按时间戳匹配。
- 避免在热路径逐元素 `.item()`；调试同步必须聚合并记录额外开销。
- 插桩失败时回退到原始服务，不把诊断代码留在生产进程。

## 判读

| 观察 | 下一步 |
|---|---|
| P 发送前 fingerprint 已不一致 | 查 P attention、量化或模型 runner |
| P 正常、D 收到后不一致 | 查 Mooncake 传输、dtype/layout、block/slot 映射、完成事件 |
| KV 内容一致、block table 不同 | 查 scheduler、block allocator、request mapping |
| KV 与 metadata 一致、logits 首步偏差 | 查 D graph、attention backend、position/rope、量化 |
| logits 一致、采样 token 不同 | 查 sampler、随机种子、logprobs 和请求参数 |
| 只有全量模型异常 | 优先查后部层、显存压力、异步竞态和层数映射 |
| 只有特定 DP/TP rank 异常 | 查 rank、设备列表、网络/NIC 和并行组映射 |
