# Repository guidance

- Maintain Chinese README.md and English README.en.md with reciprocal links. New shared documentation is English; preserved upstream skill content keeps its source language.
- Use the company's catalogue schema: metadata in catalog/skills/, taxonomy in catalog/categories.yaml, pinned sources in catalog/sources.yaml, review evidence in evidence/.
- Generate README catalogue blocks with `python scripts/render_catalog.py`; run `python scripts/validate_catalog.py` and `python scripts/render_catalog.py --check` after edits.
- New standalone packages live in skills/. The retained .agents/skills/ packages and .agents/lib/, .agents/scripts/, .remote-dev/ form a compatibility bundle. Do not move them independently: legacy wrappers resolve these paths relative to the workspace root.
- Read the complete selected SKILL.md and preserve scripts, references, templates, agents and license notices. A standalone package can be installed separately; workspace-dependent packages require their complete support layout.
- Run NPU inference and torch/torch_npu-dependent checks in the authorized remote Ascend environment. Local tests cover catalogue integrity, packaging and CPU-only tools, not deployment success.
- Preserve user working changes and attribution. Do not promote credentials, populated endpoint inventories, private addresses, kernel binaries, logs or runtime state into the public catalogue.
- Keep unresolved third-party imports out of the curated catalogue until provenance/license is resolved. A source inspection is not hardware validation.
