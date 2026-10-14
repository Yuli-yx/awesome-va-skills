---
name: vllm-ascend-build
description: Compile and verify vLLM-Ascend from a pinned workspace or PR revision inside a ready Ascend container. Use for environment builds, operator rebuilds, or deciding whether a Python overlay is sufficient. Not for initial machine setup or service-only operations.
---

# vLLM Ascend Build

Build the requested source against the intended container runtime and leave evidence that serving loads that build. Use the existing remote-dev endpoint tools; managed sessions can use `.agents/scripts/remote_job_start.py`, `remote_job_status.py`, `remote_job_tail.py`, and artifact helpers. Read their `--help` before constructing commands. Keep build records under `.vaws-local/`; never embed credentials in this skill or tracked manifests.

## Establish the build inputs

- Record the requested vLLM-Ascend SHA, PR base SHA when relevant, compatible vLLM SHA, recursive native dependency SHAs, image digest, hardware/SOC, Python, torch, torch_npu and CANN versions.
- Inspect the image's installed source and import paths. A nightly tag is mutable; package version strings alone do not establish its source base.
- Compare **image source → target source**, not merely PR base → PR HEAD. A Python-only PR may still need compilation because its base contains native changes absent from the image. Inspect `csrc/`, `cmake/`, CMake files, setup/build configuration, native submodules, generated operators and dependency requirements.
- Use a Python overlay only when the native/runtime compatibility comparison is established. If the image source cannot be identified, report that uncertainty and rebuild the target in an isolated runtime rather than claiming binary parity.
- Select the image variant and `SOC_VERSION` from the actual hardware and target build configuration. Do not assume an unsuffixed nightly image supports A3, or universally apply an A3 setting.

## Materialize and compile

Use [remote-code-parity](../remote-code-parity/SKILL.md) to sync the intended local state. Its existing install path owns normal dependency installation and runtime manifests; this skill adds build diagnosis and acceptance, not a second state system. For a PR-specific isolated source directory, preserve its provenance and use the same remote job/artifact substrate. Do not modify a live service's loaded source underneath it.

Initialize native submodules at the target's recorded commits, including catlass when required. A plain source archive omits submodule contents; transfer them explicitly and verify their revisions. Inspect the target's build files before assuming environment variables or build flags exist.

Use the container's compatible Python/toolchain and source its Ascend environment. Keep dependency installation separate from editable installation, following the parity skill's dependency policy. In a prepared runtime, the established install forms are:

```bash
# Inside the intended vLLM source directory, using the runtime Python:
VLLM_TARGET_DEVICE=empty TORCH_DEVICE_BACKEND_AUTOLOAD=0 \
  python -m pip install --no-deps -e . --no-build-isolation

# Inside the intended vLLM-Ascend source directory:
python -m pip install --no-deps -v -e . --no-build-isolation
```

The first command installs vLLM's Python runtime for an external device backend; it does not build CUDA operators. The second requires the target revision's build dependencies already present. Set `MAX_JOBS` and `CMAKE_BUILD_PARALLEL_LEVEL` to fit available CPU/RAM, and `SOC_VERSION` only to a verified supported value. Submit compilation as a durable job with a unique ID, source directory and effective build environment recorded.

On failure, inspect the first actionable compiler/configuration error. Distinguish missing submodule content, wrong SOC, incompatible build isolation, missing dependencies and ABI errors. Retry only after fixing the evidenced cause. Avoid repeatedly changing package versions or build modes without diagnosis; never treat an old `.so` or a successful pip wrapper as proof the requested operators were rebuilt.

## Verify and hand off

1. Require build exit code zero, preserve complete logs, and record installed package and native library locations. Check that generated libraries belong to the build just completed.
2. With the same Python and environment used by serving, import `torch_npu`, `vllm` and `vllm_ascend`; record `__file__`, package versions and relevant native library paths. Check representative source hashes against the target. A checkout SHA alone does not prove Python imports that checkout.
3. Validate every participating P/D container independently. A build succeeding on P does not prove D has matching source, operators or dependencies.
4. Use [vllm-ascend-serving](../vllm-ascend-serving/SKILL.md) for an authorized launch/restart and a real request. Confirm the requested model runner from logs and exercise the actual PD endpoint when applicable. Keep build success, service readiness, graph/eager coverage and accuracy as separate results.
5. Before an authorized restart in a dedicated task container, clear residual vLLM/Python inference processes (including `pkill` when requested), then verify ports and assigned NPUs are clear. Do not apply a blanket Python kill on a shared host/container or stop a service the user asked to retain.

Return source/image identities, whether native rebuild was needed and why, job/log references, import parity evidence, service/request outcome and any unvalidated modes. Do not equate a successful build or one valid answer with accuracy correctness.

For the concrete two-node A3 build that motivated this workflow, read [the validated example](references/pr14872.md). Its revisions and workarounds are historical evidence, not defaults for new builds.
