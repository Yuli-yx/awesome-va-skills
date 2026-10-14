---
name: pd-dfx-workbench
description: Maintain the PD-separation DFX workbook when users ask to import historical cases or feedback, assess diagnostic gaps, map cases to existing PD-side DFX, or propose, add, or strengthen DFX capabilities. Require user review before changing the DFX backlog or coverage mapping. Do not use for unrelated defect tracking or for fixing external modules.
---

# PD Separation DFX Workbench

Maintain the single-source workbook at `<user-provided-workbook.xlsx>` without turning external-module fixes into PD DFX work.

## Non-negotiable boundaries

- DFX actions must be implemented by the PD-separation module. Models, Graph, scheduler, worker, Layerwise, transport libraries, NICs, and other modules may be fault sources or test dependencies, but this workflow must not propose modifying them as a PD DFX action.
- PD DFX may reject invalid inputs, validate identities and invariants, preserve first-failure evidence, compare send/receive fingerprints, watch PD-stage progress, mock external failures, or run causal controls that prove a fault occurred before, inside, or after the PD boundary.
- Treat source documents and populated rows in `历史问题` and `反馈池` as user facts. Append normalized facts when requested; do not rewrite existing fact rows unless the user explicitly asks.
- Never create external requirements, Issues, PRs, or code changes through this skill.
- Use the available spreadsheet skill for every `.xlsx` read or edit and follow its backup, formatting, recalculation, and visual-verification rules.

Read [references/workbook-schema.md](references/workbook-schema.md) before reading or writing the workbook. Read [references/review-gate.md](references/review-gate.md) whenever DFX assessment or mutation is requested.

## Route the request

### Import historical cases or feedback

1. Read the current source file from disk; do not rely on a prior copy, prior hash, or unsaved editor content.
2. Read current IDs and critical fields from the workbook. Deduplicate by ID and normalized content fingerprint, not by row number or file timestamp.
3. Split the material into cases. Preserve links, dates, stated root causes, observed symptoms, localization steps, closure claims, and evidence gaps.
4. Do not invent dates, owners, closure state, PD causality, or deterministic root cause. Mark missing evidence in `备注`; use a non-final status when closure is not established.
5. Assign the next `HIST-YYYY-NNN` or `FB-YYYY-NNN` only after deduplication.
6. When the user has asked to import the facts, append only the fact rows after lock/concurrency checks and a timestamped backup. Do not change `DFX需求池` or `覆盖映射` in this phase.
7. Report added IDs, duplicates, incomplete evidence, and exactly what was written.

### Assess DFX coverage

For each new or modified fact, first check evidence completeness and then classify it as one of:

- `不需要新增DFX`: not a PD diagnostic gap, or already adequately handled.
- `复用已有DFX`: an existing action already answers the diagnostic question; propose only a coverage mapping.
- `加强已有DFX`: the same diagnostic problem exists, but the current action or acceptance criteria miss a reusable PD-side scenario.
- `建议新增DFX`: a new, generalizable PD-side diagnostic problem is not covered.
- `证据不足`: list the missing evidence and avoid a deterministic conclusion.

Always read the live `DFX需求池`; do not rely on a cached list of capabilities. Compare candidates by diagnostic question, PD-side action, target boundary, and acceptance criteria—not by wording alone.

Prefer reuse or strengthening. A new case, model, topology, or log signature is not by itself a new DFX capability.

Produce the review packet defined in [references/review-gate.md](references/review-gate.md), then stop. Do not write, append, edit, or reserve a formal DFX ID before the user decides.

### Apply an approved DFX decision

Only enter this phase after the user explicitly approves named candidate IDs or clearly approves all candidates in the current review packet. Approval from an earlier packet does not carry over to later candidates.

Apply each decision exactly:

- `复用`: leave `DFX需求池` unchanged and append only the approved `覆盖映射` relation.
- `加强`: update the approved existing DFX action and append its approved mapping. Preserve its ID and explain the delta.
- `新增`: allocate the next formal `DFX-YYYY-NNN`, append one action with status `待评审`, and append mappings only for approved historical-problem relationships.
- `暂缓` or `拒绝`: write nothing for that candidate.

Before writing, re-read the workbook and verify that it is unlocked and unchanged since analysis. Create a timestamped backup under `<workbook-directory>/archive`. If the workbook is open or changed concurrently, do not force an overwrite; report the blocker and retry later.

After writing, preserve formulas, styles, data validation, sheet order, and user facts. Recalculate, scan for formula errors, visually inspect all visible sheets, and update the incremental fingerprint state only after successful verification.

## Completion report

Report separately:

- fact rows imported;
- duplicates skipped;
- evidence gaps;
- DFX candidates and the user's decisions;
- approved backlog or mapping changes actually written;
- backups and validation result;
- remaining risks and next action.

Never describe a candidate as implemented merely because it was analyzed or approved for registration.
