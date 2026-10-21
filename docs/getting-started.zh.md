# 查找和使用技能

中文 | [English](getting-started.md)

从[目录](../README.md)选择任务，按条目的 `source.path` 阅读固定版本的完整
SKILL.md、依赖及引用资料。来源版本和许可证见
[catalog/sources.yaml](../catalog/sources.yaml)，审阅范围见条目的 evidence。
来源不明的历史归档包暂不进入推荐目录。

克隆本仓库，并检出所选条目记录的 source commit。来源快照可以早于目录提交，
避免提交哈希自引用。新的独立包位于 `skills/`，依赖工作区的旧包保留在
`.agents/skills/`，并保留 `.agents/lib/`、`.agents/scripts/` 和 `.remote-dev/`
等实际依赖。安装前读[布局说明](collection-layout.md)，不要覆盖已有运行状态。

MemCache 监控入口见 `skills/ascend-memcache-pooling/references/monitoring.md`。
从实际配置确认 Meta 指标地址与所有 API 指标端口；脚本只发 HTTP GET，使用标准库，
不需要 NPU。实际部署需要匹配的 Ascend 软件与资源。

目录 requirements.txt 只安装目录工具依赖；各技能依赖另按入口准备。
离线检查不代表远端部署、SSD 回读或性能通过。执行后保留版本、配置和数据哈希、
命令及原始证据，按[验证规则](validation-policy.md)和[贡献说明](../CONTRIBUTING.md)
记录实际验证范围。
