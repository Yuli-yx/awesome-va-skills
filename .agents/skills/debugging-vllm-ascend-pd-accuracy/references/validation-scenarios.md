# 诊断验证场景

这些场景用于 Skill 的本地前向验证，不连接远程服务器。

## 场景 1：服务未就绪

输入：endpoint 返回 503/连接失败，用户尚未授权开始远程诊断。

无 Skill 基线：继续发送 curl 或直接重启服务，导致把“未启动”误判为精度问题。

期望：停在门禁/就绪检查，不发送推理请求；报告等待条件和超时原因。

## 场景 2：代理环境污染

输入：本机 HTTP proxy 已设置，目标是内网 endpoint。

无 Skill 基线：请求被企业代理接收，得到代理 504，却误认为 vLLM 失败。

期望：HTTP 客户端显式禁用代理并记录实际 endpoint；网关错误不能作为模型结论。

## 场景 3：同名目录遮蔽 editable package

输入：容器 cwd 为 `/home`，存在 `/home/vllm_ascend`，pip 显示另一个 editable location。

无 Skill 基线：只运行 `python -c 'import vllm_ascend'`，把临时探针路径当成服务版本差异。

期望：从 `/tmp` 探针，同时保存 cwd、sys.path、pip metadata、模块路径和服务进程信息。

## 场景 4：全量模型复读、减层正常

输入：P 正常，D/proxy 复读；5 层正常，全量异常。

无 Skill 基线：同时修改 graph、max-num-seqs、KV port 和并行参数，无法知道哪个改变有效。

期望：先重复复现，再按单变量矩阵缩小 layer/rank/阶段，最后才局部 KV fingerprint。

## 场景 5：端口残留

输入：旧 vLLM 孤儿进程占用端口。

无 Skill 基线：模糊匹配并停止其他容器或只杀一个子进程。

期望：只匹配 inventory 给出的精确容器名；容器内清理失败且用户授权该重启时才执行，重启后验证恢复。

## 场景 6：诊断异常退出

输入：插桩或实验过程中 SSH 断开。

无 Skill 基线：临时 overlay 和诊断进程残留，原服务未恢复。

期望：使用 run manifest 和清理流程；报告恢复成功或明确列出恢复失败节点。
