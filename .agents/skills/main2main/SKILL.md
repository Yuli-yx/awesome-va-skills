---
name: main2main
description: Adapt vLLM-Ascend to upstream vLLM main changes. Analyze upstream diffs, diagnose main2main CI failures, and implement compatibility fixes with evidence and a change report. Use for version upgrades or failures caused by vLLM main evolution; Git and PR operations remain a separate step.
---

# main2main

Adapt vLLM-Ascend to upstream vLLM main branch evolution — proactively or reactively.

## Scenario Detection

Determine which workflow the user needs, then Read the corresponding document:

**Proactive Upgrade** — Read `proactive-upgrade.md` (in the same directory as this SKILL.md)
- User wants to analyze what changed in vLLM and adapt vllm-ascend
- User mentions upgrading, bumping, or syncing to a newer vLLM commit
- No CI failure is involved; the goal is forward-looking analysis

**CI Failure Diagnosis** — Read `error-analysis.md` (in the same directory as this SKILL.md)
- User shares a GitHub Actions URL, run ID, or mentions CI is red
- User mentions schedule_test_vllm_main failures or "main2main" test failures
- The goal is to diagnose and fix existing breakage

**If both signals are present** (e.g., user says "upstream changed an API and CI is failing"), prefer CI Failure Diagnosis — fixing active breakage takes priority over proactive analysis.

Both workflows share the common knowledge below. After reading the relevant document, also read `reference/error-patterns.md` for concrete fix examples — do this immediately if the user's message already mentions a specific error type (TypeError, AttributeError, ImportError, etc.), or whenever you encounter such errors during analysis.

---

## Common Knowledge

### Version Compatibility Pattern

Most fixes require `vllm_version_is()` guards to maintain backward compatibility:

```python
from vllm_ascend.utils import vllm_version_is

if vllm_version_is("0.16.0"):  # pinned release version
    # Use old API
else:
    # Use new API (main branch)
```

The compatible release version comes from `vllm_version` matrix in `.github/workflows/pr_test_full.yaml`.

---

## Output Contract

Both workflows produce two common outputs:

1. **Code changes** — applied to the working tree (unstaged)
2. **Structured summary** — output in conversation, following the format defined in each workflow's final step

The skill does **not** perform git or GitHub operations (no branch, commit, push, or PR). After the skill completes:

- **Standalone mode**: proceed with creating a branch, committing changes, pushing, and submitting a PR. Use the structured summary as the PR body content.
- **Workflow mode**: the orchestrating Workflow handles all git/PR operations using the structured summary.
