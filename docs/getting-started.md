# Find and use a skill

[中文](getting-started.zh.md) | English

Select the task in the [catalogue](../README.en.md), then read its pinned
`source.path` and complete SKILL.md. The metadata records the package snapshot,
license, execution requirements and review scope. Historical archive packages
with unresolved provenance are not recommended through the curated catalogue.

Clone this collection and check out the source commit recorded for the selected
entry in [catalog/sources.yaml](../catalog/sources.yaml). The source snapshot
can differ from the catalogue commit: that avoids a self-referential hash.

New standalone packages live in `skills/`; retained workspace-dependent packages
live in `.agents/skills/`. Preserve whole packages and any `.agents/lib/`,
`.agents/scripts/` and `.remote-dev/` dependencies required by their entrypoints.
See [installation and layout](collection-layout.md) before copying into an
existing workspace. Do not replace configured runtime state.

For the MemCache monitor, open
`skills/ascend-memcache-pooling/references/monitoring.md`. Discover the actual
Meta metrics address and API metrics ports from the running configuration.
It sends only HTTP GETs and needs no NPU or third-party Python library. Running
the deployment workflow itself needs the selected Ascend runtime and resources.

Execution labels distinguish host/offline tools from NPU work and conditional
device checks. Install each selected package's own dependencies; catalogue
`requirements.txt` only installs catalogue tooling dependencies. Offline
validation does not establish remote deployment or performance success.

Retain source, config/data hashes, command lines, runtime versions and evidence
for actual executions. See the [validation policy](validation-policy.md) and
[contribution guide](../CONTRIBUTING.md) before publishing reproduction claims.
