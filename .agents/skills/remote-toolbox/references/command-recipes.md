# Remote Toolbox Command Recipes

Probe both managed base containers:

```bash
python3 .agents/scripts/remote_probe.py --machine 192.0.2.10
python3 .agents/scripts/remote_probe.py --machine 192.0.2.20
```

Create two sessions on one machine, then prove isolation:

```bash
python3 .agents/skills/session-management/scripts/session_create.py --machine 192.0.2.20 --session-id toolbox-a --npu-count 1 --no-worktree
python3 .agents/skills/session-management/scripts/session_create.py --machine 192.0.2.20 --session-id toolbox-b --npu-count 1 --no-worktree
python3 .agents/scripts/remote_target_resolve.py --session-id toolbox-a
python3 .agents/scripts/remote_target_resolve.py --session-id toolbox-b
```

Plan sync without install:

```bash
python3 .agents/scripts/remote_sync_plan.py --session-id toolbox-a --mode source-only
```

Plan install with explicit reasons and consent state:

```bash
python3 .agents/scripts/remote_sync_plan.py --session-id toolbox-a --mode install
```

Validate service failure cleanup:

```bash
python3 .agents/scripts/remote_service_start.py --session-id toolbox-a -- --model /no/such/model --skip-parity
python3 .agents/scripts/remote_cleanup.py --session-id toolbox-a --service --force
```

Pull a service log directory:

```bash
python3 .agents/scripts/remote_artifact_manifest.py --session-id toolbox-a --remote-path /vllm-workspace/.vaws-runtime/serving
python3 .agents/scripts/remote_artifact_pull.py --session-id toolbox-a --remote-path /vllm-workspace/.vaws-runtime/serving --local-dir .vaws-local/remote-toolbox/artifacts/toolbox-a-serving
```
