# DFX user review gate

## Purpose

Separate diagnostic analysis from workbook mutation. The user must decide whether a PD-side capability should be reused, strengthened, added, deferred, or rejected before the backlog or mapping changes.

## Candidate IDs

Assign temporary IDs such as `CAND-2026-001` within the current review packet. Candidate IDs are not formal DFX IDs and must not be written to the workbook.

## Review packet

For each candidate, present:

| Field | Required content |
|---|---|
| Candidate ID | Temporary review identifier |
| Source IDs | Historical-problem or feedback IDs |
| External fault source | Module or dependency that produced the problem; use `未定界` when unsupported |
| PD relationship | Direct, scene-triggered, amplified, unrelated, or undetermined |
| Evidence completeness | Complete, partial, or insufficient, plus missing items |
| Diagnostic question | What the PD side must be able to answer |
| Recommendation | No new DFX, reuse, strengthen, new, or insufficient evidence |
| Existing DFX | Matching formal ID when reuse or strengthening is proposed |
| PD-side change | Exact PD boundary, event, validation, watchdog, tool, mock, or test change |
| Why existing coverage is insufficient | Required for strengthening or new candidates |
| Refactor relationship | Must enter refactor, should enter refactor, or independent |
| Acceptance criteria | Observable PD-side rejection, localization, or evidence result; state that external modules are not modified |
| Proposed workbook effect | No write, mapping only, edit existing plus mapping, or append new plus mapping |

After the table, provide a compact decision list such as:

```text
CAND-2026-001: 建议复用 DFX-2026-002，仅新增覆盖映射
CAND-2026-002: 建议加强 DFX-2026-003，补充……
CAND-2026-003: 建议新增，原因是……
```

Then ask the user to approve each candidate. Stop without changing `DFX需求池` or `覆盖映射`.

## Accepted decisions

Treat these as explicit decisions when candidate IDs are unambiguous:

- `批准 CAND-... 复用`
- `批准 CAND-... 加强`
- `批准 CAND-... 新增`
- `CAND-... 暂缓`
- `CAND-... 拒绝`
- `全部按建议执行`

If the user changes the proposed action, follow the changed decision and restate the resulting workbook mutation before writing.

Do not treat silence, a request for explanation, or approval of historical-case import as approval to change DFX capabilities.

## Applying decisions

Before applying approved decisions:

1. Re-read the workbook because capability definitions may have changed during review.
2. Re-run duplicate detection.
3. Confirm the workbook is unlocked and unchanged since the read.
4. Back up the workbook.
5. Apply only approved candidates.
6. Recalculate and verify formulas, styles, validations, sheet order, and visible layout.
7. Report candidate-by-candidate results, including anything skipped because of a conflict or new duplicate.

An approved candidate that becomes a duplicate during re-read should be reused rather than appended again, and this deviation must be reported.
