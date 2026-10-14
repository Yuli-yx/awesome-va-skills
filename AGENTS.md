# Agent instructions

This repository collects vLLM-Ascend and Ascend communication skills.

- Read `.agents/skills/<name>/SKILL.md` before using a skill.
- Preserve complete skill packages and the workspace-relative layout of `.agents/lib/`, `.agents/scripts/`, and `.remote-dev/`.
- Use `.remote-dev` tools for remote endpoints; shared managed workflows use `.agents/scripts/`.
- NPU inference and torch/torch_npu-dependent checks run in a prepared remote Ascend environment. Local checks cover packaging, syntax and command interfaces only.
- Do not commit credentials, populated endpoint inventories, owner identities, logs, experimental outputs or machine state. Keep those in ignored local paths.
- Preserve source copyright notices and per-package license information.
