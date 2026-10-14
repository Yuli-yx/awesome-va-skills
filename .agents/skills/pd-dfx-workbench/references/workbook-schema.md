# Workbook schema and fact rules

## Official artifact

- Workbook: `<user-provided-workbook.xlsx>`
- Backup directory: `<workbook-directory>/archive`
- Incremental state: `<workbook-directory>/.automation/pd-dfx-state.json`
- Preserve the existing worksheet order. Do not rebuild the workbook from the empty-template generator.

## Sheets

### `历史问题`

Columns A:L: 问题ID、问题描述、现象、根因、定位方式、发现时间、闭环时间、PD关系、DFX改进点、状态、负责人、备注。

Use real Excel dates when a date is known. Keep unknown dates blank and explain the gap in `备注`.

Allowed PD-causality meanings include `PD直接导致`, `PD场景触发`, `PD放大`, `与PD无关`, and `未定界`. A failure on a P or D node is not evidence that PD caused it.

### `反馈池`

Columns A:H: 反馈ID、反馈描述、场景/痛点、建议方向、来源/反馈人、收集时间、状态、备注。

### `DFX需求池`

Columns A:K: DFX ID、来源问题/反馈ID、诊断问题、改进内容、能力方向/类型、与重构关系、验收标准、负责人、计划完成、状态、需求/PR链接。

All actions must be PD-side actions. `来源问题/反馈ID` may point to an external-module root cause, but `改进内容` and `验收标准` must describe what PD will reject, observe, classify, test, or preserve.

Use `必须随重构进入` for PD boundary fields, request/transfer identity, PD stage state machines, event models, or error semantics. Use `建议随重构进入` for PD invariants, logs, or testable interfaces. PD tools, E2E, fault injection, and documentation can normally be `可独立演进`.

New formal actions are registered as `待评审` even after the user approves adding them to the workbook; workbook registration is not implementation approval.

### `覆盖映射`

Columns A:D: 问题ID、DFX ID、覆盖说明、验证状态。

Only add a relation when a historical problem has a clear connection to an approved existing, strengthened, or new DFX action. The description must say how the PD-side capability rejects, localizes, or captures the problem. New mappings begin as `待验证`.

## Evidence checklist

For every case, look for:

- reproducible symptom and user impact;
- discovery and closure dates;
- deployed version or commit;
- topology, model, feature flags, and launch/request commands;
- first failing component and first-failure evidence;
- direct-P, controlled-D, and full-PD controls where causality is disputed;
- stated root cause and supporting PR or logs;
- fix validation under the same environment;
- owner and localization effort.

Missing evidence must be recorded. Do not convert an initial inference into a confirmed root cause.

## Incremental identity

- Use the explicit ID as the primary key.
- Use a fingerprint of critical field contents to detect modifications.
- Do not infer newness from row number, workbook modification time, or source filename.
- A source file that is byte-identical or semantically identical to an imported case creates no new row.
