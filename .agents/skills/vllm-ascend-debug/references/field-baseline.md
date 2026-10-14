# 现场基线

用于脚本、环境或版本不明确的现场。只补足影响当前判断的信息，已有首错时不要等待完整清单齐备。

## 把期望配置与实际状态对应起来

| 信息 | 有用的证据 |
|---|---|
| 实际代码 | vLLM/vllm-ascend commit 或 wheel 版本、backport、未提交改动、模块路径、扩展库加载位置 |
| 运行依赖 | 镜像、CANN、torch/torch_npu、Mooncake/HIXL；版本取现场，不猜测兼容矩阵 |
| 模型与输入 | 权重/量化、tokenizer、chat template、输入/输出长度、生成参数及故障样本 |
| 拓扑 | proxy/P/D 实例、DP/TP/PP/PCP/DCP、rank→容器设备→宿主物理设备→通信 endpoint |
| 实际启动 | 启动脚本、进程 argv、有效关键环境变量、启动日志和 connector 类/角色 |
| 特性叠加 | async scheduling、Graph 模式、spec decode、prefix cache、KV pool、多 connector、错误策略 |
| 现场窗口 | 故障时间、进程/rank 覆盖、日志级别、是否重启/重试、数据是否被截断或轮转 |

优先做只读比对，例如在正确的 checkout 使用 `git rev-parse HEAD`、`git status --short`，结合远端包和模块加载信息。不要在本地 PC 导入 NPU 模块以推断远端状态；不要把全部环境变量、令牌或带密钥的 argv 原样归档。

## PD 场景的易漏点

- 脚本指定一个 checkout，不代表实际 Python、wheel 或 `.so` 来自那里。源码覆盖需核对自定义算子等随 wheel 发布的依赖，不能以纯 Python import 成功证明完整运行一致。
- API 地址、握手/metadata 地址与实际数据传输 endpoint 分别检查。HTTP 健康或控制面握手成功只证明对应路径。
- `local_rank`、进程可见设备序号与宿主物理卡 ID 不必相等。若 endpoint 文件按物理 ID 命名，用目标环境可用的运行时映射核对；不要仅按可见设备字符串索引推断。
- 对比实际展开后的 P/D 启动配置，尤其是 block size、KV dtype/group/layout、并行与切片策略、错误回退配置。
- 内存紧张、残留进程或背景流量可改变复现概率；记录资源使用和归属，不为做基线擅自停止其他任务。

## 留下可继续使用的基线

简要列出已确认信息、互相冲突的信息、尚缺信息及来源。版本映射不完整时仍可提出条件性结论，但不要用当前 main 覆盖旧版本语义。只向用户询问无法自行读取且会影响下一步的信息。

交付实验时将启动、请求和结果关联到同一个 run 标识。复现需要重新启动时保存实际配置与变更原因，避免后续比较混用不同现场。
