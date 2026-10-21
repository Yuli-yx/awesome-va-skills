# Company-format collection review: 2026-10-21

The catalogue covers the license-resolved subset of the complete archive.
Entry names, frontmatter, task descriptions, dependency/layout references and
source/license metadata were inspected for catalogue mapping; no unchanged
package is newly claimed to have passed its full runtime workflow.

Source snapshots use this collection's immutable commit, not an assumption that
exported local adaptations match their original application repository. Retain
the detailed original-source attribution in ATTRIBUTION.md and package notices.
The existing AISBench origin and user-authored PD licenses are carried forward
from the previously reviewed `8d9f7ee` contribution.

## Pending archive entries

`compile-mooncake`, `hccl-auto-test`, `pd-dfx-workbench` and `vllm-ascend-debug`
remain in the archive inventory with unresolved licenses/provenance and are not
registered in the curated catalogue. The HCCL skill remains credited to its
GitCode author WZN-JJB; possession of that package does not confer a new license.

Local untracked Leaf-Spine/vendor drafts are not added to this branch. Their
original files and the original checkout's working changes are preserved.

## Validation boundary

Run catalogue schema/link/hash checks, bilingual renderer checks, syntax and
offline regression suites. Invalid duplicate keys, unknown categories and stale
README output must be rejected on disposable inputs. The pooling monitor's
local HTTP fixtures are not remote Ascend or SSD tests. Runtime validation for
all catalogue entries remains `not-recorded`.
