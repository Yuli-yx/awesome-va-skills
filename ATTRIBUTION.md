# Source attribution

This is a collection of imported and locally maintained packages, not a claim
that every skill was authored by this repository's maintainer. Preserve the
original copyright and license when copying a complete package. The package
inventory and export adjustments are recorded in `skills-manifest.json`.

## Workspace-derived packages

Original workspace: [maoxx241/vllm-ascend-workspace](https://github.com/maoxx241/vllm-ascend-workspace),
whose product has moved to [mindie-agent/mindie-agent](https://github.com/mindie-agent/mindie-agent).
The retained source with local changes is
[Yuli-yx/vllm-ascend-workspace at c7f899d](https://github.com/Yuli-yx/vllm-ascend-workspace/tree/c7f899d74a36d0d031f488a3d81bad49de2be724/.agents/skills).
The bundled workspace MIT notice credits **Qi Mao**; local additions and
adaptations are maintained by Yuli-yx and retain that notice where applicable.

Packages: `aisbench-accuracy`, `ascend-memory-profiling`,
`ascend-profiling-analysis`, `ascend-profiling-collection`,
`machine-management`, `modelscope`, `remote-code-parity`, `remote-toolbox`,
`repo-init`, `session-management`, `vllm-ascend-benchmark`,
`vllm-ascend-build`, `vllm-ascend-serving`, `pd-pure-role-benchmark`.
See [the preserved MIT license](LICENSES/workspace-MIT.txt).
This source base includes local additions; it does not attribute every added
workflow to the original workspace author.

## vLLM Ascend packages

Original project and maintainers:
[vllm-project/vllm-ascend](https://github.com/vllm-project/vllm-ascend).
Packages: `vllm-ascend-model-adapter`, `vllm-ascend-release`, `main2main`,
`vllm-ascend-release-note-writer`.
The collection was exported from local installations/checkouts, with the base
revision `a2acc452fb4d6bd181dd0bfe3b4bb5aff075292a` recorded in the manifest.
This records project provenance, not a claim that all exported bytes or all
four package paths exist in that clean upstream revision.
See [the preserved Apache-2.0 license](LICENSES/vllm-ascend-Apache-2.0.txt).

## HIXL packages

Original project and maintainers: [CANN HIXL](https://gitcode.com/cann/hixl).
Packages: `driver-peermem-check`, `hixl-ut-generator`,
`hixl-srs-doc-generator`, `hixl-pr-review`, `hixl-troubleshoot`.
These were imported from a local HIXL source package or installed package and
include local adaptations. An exact original HIXL archive revision is not
recorded; use this collection's pinned revision to reproduce the exported
files, rather than assuming they match current HIXL main.
Their frontmatter declares CANN Open Software License Agreement Version 2.0;
see [the preserved license](LICENSES/HIXL-CANN-2.0.txt).

## GitCode A5 HCCL traffic-test skill

`hccl-auto-test` comes from
[qq_46749096/MindIE-PyMotor, personal_skills branch](https://gitcode.com/qq_46749096/MindIE-PyMotor/tree/personal_skills/personal_skills/hccl-auto-test).
The inspected source file is
[SKILL.md at 9f0f99c319090eec50a182eec390a1307254e2ae](https://gitcode.com/qq_46749096/MindIE-PyMotor/blob/9f0f99c319090eec50a182eec390a1307254e2ae/personal_skills/hccl-auto-test/SKILL.md).
The introducing commit `555507cf550a27e3f6421c2ede1716582bb312ac` and the
inspected revision are authored by **WZN-JJB**. Credit belongs to that author
and contributors; Yuli-yx maintains only this collected copy and its documented
export adjustments.

The personal branch has no explicit license in the inspected file/root;
`unspecified` remains the manifest value. The repository's separate master
revision `499b3b9ae2248cedb9784ffddd0df1c092a27cb6` contains a
[Mulan PSL v2 license](https://gitcode.com/qq_46749096/MindIE-PyMotor/blob/499b3b9ae2248cedb9784ffddd0df1c092a27cb6/LICENSE.md),
but its application to the standalone personal skill has not been confirmed.
Attribution does not add a license.
Do not submit it as an original Yuli-yx skill or register it in a catalogue
requiring an explicit source license until that information is supplied.

## AISBench PD benchmark

`aisbench-pd-benchmark` originates from
[wangxiaoteng888/vllm-ascend-workspace](https://github.com/wangxiaoteng888/vllm-ascend-workspace/tree/5fba343c1c2b3d896f1273e0ecb9b0581f8128d4/.agents/skills/aisbench-pd-benchmark),
at revision `5fba343c1c2b3d896f1273e0ecb9b0581f8128d4`, authored in Git by
`wangxiaoteng`. The repository's
[MIT license](https://github.com/wangxiaoteng888/vllm-ascend-workspace/blob/5fba343c1c2b3d896f1273e0ecb9b0581f8128d4/LICENSE)
preserves Qi Mao's copyright notice; a copy is bundled with this skill.
Yuli-yx's adapted copy adds warmup load/timing controls and fixes warmup-rate
formatting. The external benchmark application
[rayn-zzz/aisbench_auto_tools_prefix](https://github.com/rayn-zzz/aisbench_auto_tools_prefix)
is a separate dependency, not the author of this skill package.

## User-authored PD accuracy workflow

The user confirmed `debugging-vllm-ascend-pd-accuracy` is our own workflow and
authorized MIT for it. Yuli-yx maintains the package; its canonical public
source is [this collection](https://github.com/Yuli-yx/awesome-va-skills/tree/codex/selected-skills-upstream-20261019/.agents/skills/debugging-vllm-ascend-pd-accuracy).
Its package includes an explicit MIT notice. The locally maintained
`pd-pure-role-benchmark` likewise carries its own MIT notice.

## Installed packages with unresolved public provenance

`compile-mooncake`, `pd-dfx-workbench`, and `vllm-ascend-debug` were collected from
local skill installations or local prototypes. Their original public package
URLs and explicit licenses were not recorded in the export. Do not substitute
the AISBench/Mooncake application URLs for the skill authors' source URLs, or
claim these are all original work by this collection's maintainer. Resolve the
original package provenance and license before recommending them upstream.

## Integrated pooling package

`skills/ascend-memcache-pooling` retains zouyida2052's A3/A5/SSD workflow at
`f5108884c387175025eecf2e58021828f802a204` under CC0-1.0 and adds Yuli-yx's
Host RoCE/P-D guidance, read-only monitor and regression tests under MIT.
See its complete NOTICE and LICENSES directory. The old private/vendor draft
is not redistributed as part of the integrated package.

## Company-format catalogue

Catalogue schema, renderer, validator and supporting documentation originate
from mindie-agent/awesome-mindie-skills at `64c2457` under CC0-1.0. Runtime skill
packages and workspace tools retain their separate original licenses.
