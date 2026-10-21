# Collection layout and company integration

The collection now uses the same catalogue schema, taxonomy, bilingual README
generation and review/evidence distinction as `mindie-agent/awesome-mindie-skills`
at `64c2457`. The imported catalogue maintenance code/documentation is CC0-1.0.
The collection's package copyrights and licenses remain separate.

| Path | Purpose |
| --- | --- |
| `catalog/skills/`, `catalog/sources.yaml` | Curated metadata and immutable package-source snapshots |
| `docs/`, `evidence/` | Maintenance/installation guidance and scoped source reviews |
| `skills/ascend-memcache-pooling/` | New self-contained pooling package with monitoring and tests |
| `.agents/skills/` | Complete retained workspace-layout skill packages |
| `.agents/lib/`, `.agents/scripts/`, `.remote-dev/` | Runtime support required by legacy wrappers |
| `skills-manifest.json`, `ATTRIBUTION.md`, `LICENSES/` | Complete archive inventory, file hashes and provenance |

The company catalogue accepts source paths such as `.agents/skills/.../SKILL.md`.
Keeping those packages in place avoids breaking Python `parents[4]` imports,
cross-skill commands and installed workspace integrations. This migration changes
discovery/metadata structure, not the legacy execution substrate. It does not
claim compatibility with a new coordinator runtime.

## Install complete packages

Clone the collection. Install `skills/ascend-memcache-pooling/` as a complete
folder into an agent's skill directory; it has no workspace helper dependency.
Its monitor uses Python 3.10+ and the standard library. See its SKILL.md for
deployment requirements and read-only monitoring commands.

For a legacy workspace-dependent package, review differences before copying
`.agents/skills/<name>/`, `.agents/lib/`, `.agents/scripts/` and `.remote-dev/`
into the target workspace. Do not overwrite existing endpoint/state files.
The target still needs its own model source trees, runtime and remote inventory.
Read-only document packages can be installed independently when their entrypoint
does not call workspace-relative helpers.

Local state belongs in ignored `.vaws-local/`, `.remote-dev/state/`, `experiments/`
or `artifacts/`. The collection contains no model weights or containers.

## Contribution scope

The integrated pooling package combines zouyida2052's CC0 workflow with Yuli-yx's
MIT Host RoCE/P-D and monitoring additions. It is submitted on a separate branch
based on the company upstream, so catalogue alignment does not add unrelated
archived packages to the pooling pull requests.

The original `a5-memcache-pooling` draft and `leaf-spine-roce-1825` local additions
are not copied wholesale: vendor attachments and unresolved licenses need their
own review. Existing local originals remain untouched. Archived unresolved
imports are listed in the review evidence rather than recommended upstream.
