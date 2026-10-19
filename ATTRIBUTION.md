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
Its inspected Git commit is authored by **WZN-JJB**. Credit belongs to that
source author and contributors; Yuli-yx maintains only this collected copy and
its documented export adjustments. The inspected checkout is shallow, so this
does not assert that the latest commit author is the only original author.

The original package has no explicit license in the inspected file/root;
`unspecified` remains the manifest value. Attribution does not add a license.
Do not submit it as an original Yuli-yx skill or register it in a catalogue
requiring an explicit source license until that information is supplied.

## Installed packages with unresolved public provenance

`aisbench-pd-benchmark`, `compile-mooncake`, `pd-dfx-workbench`,
`vllm-ascend-debug`, and `debugging-vllm-ascend-pd-accuracy` were collected from
local skill installations or local prototypes. Their original public package
URLs and explicit licenses were not recorded in the export. Do not substitute
the AISBench/Mooncake application URLs for the skill authors' source URLs, or
claim these are all original work by this collection's maintainer. Resolve the
original package provenance and license before recommending them upstream.

## Deferred work

The A5 MemCache pooling draft is outside the current catalogue contribution.
Any later submission needs its own source, license, package and validation
review. Existing local drafts and runtime results are not changed by this
attribution record.
