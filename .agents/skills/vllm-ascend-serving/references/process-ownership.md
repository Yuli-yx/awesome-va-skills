# Process ownership on shared Ascend hosts

Long-running NPU services must expose a short owner identifier in the process
names that colleagues see on the **host**. Resolve the identifier from the
current task or the ignored local `.vaws-local/process-owner.json` file when it
exists. Keep personal names, employee IDs, host addresses, and populated owner
files out of Git. Do not infer ownership from a container name alone.

The local file may contain `{"owner_id": "<short-id>",
"display_name": "<local-name>"}`. Use `owner_id` in process titles; the display
name is context for the local operator only.

## Launch

1. Set `VLLM_PROCESS_NAME_PREFIX=<owner-id>` before `vllm serve`. This is the
   vLLM setting used by `set_process_title()` for EngineCore and Worker
   processes, which usually hold NPU memory. The serving wrapper accepts it
   through `--extra-env VLLM_PROCESS_NAME_PREFIX=<owner-id>`.
2. Give the main `vllm serve` process an owner-prefixed title as well. vLLM
   does not call its process-title helper for that main process. Where the
   environment supports `setproctitle`, put a small `sitecustomize.py` in a
   dedicated directory on `PYTHONPATH`; only set the title when the launch
   provides both `VLLM_OWNER` and `VLLM_SERVE_ROLE`:

   ```python
   import os

   owner = os.getenv("VLLM_OWNER")
   role = os.getenv("VLLM_SERVE_ROLE")
   if owner and role:
       import setproctitle

       setproctitle.setproctitle(f"{owner}::{role}")
   ```

   Set `VLLM_OWNER=<owner-id>` and a short role such as
   `VLLM_SERVE_ROLE=vllm-serve` for the launch. `VLLM_OWNER` is a local
   convention for this helper and any auxiliary processes; vLLM itself does
   not consume it. Supply `PYTHONPATH` as an actual remote path through the
   wrapper; `--extra-env` quotes values literally and does not expand
   `${PYTHONPATH}`. Check that this directory exists in the target container
   before launch and that `setproctitle` imports there.
3. In manually managed shared environments, include the owner ID in the
   container name. Keep the launch script and logs below
   `/mnt/share/<owner-id>/` if that shared filesystem is mounted and writable;
   otherwise use the machine-local `/home/<owner-id>/`. Append one row to the
   service ledger with the owner ID, machine IP (or stable hostname), role,
   container, start time, launch-script path, and log location. On shared
   storage, each log set **must** identify its source machine and role (for
   example, `prefill` or `decode`) in the path or adjacent metadata so logs
   from different hosts cannot be confused. Use the same labeling on local
   storage when possible. A layout such as
   `<base>/<machine-id>/<role>/<run-id>/start.sh` and `stdout.log` keeps the
   script and logs together. Container and ledger labels help colleagues find
   context but do not replace process naming.

The managed `serve_start.py` launcher currently generates `_serve.sh` and logs
under `<workdir>/.vaws-runtime/serving/<timestamp>/`. Record those actual paths
in the ledger. An owner directory or ledger entry does not relocate the
managed launcher's files; change its runtime path deliberately before claiming
the owner-directory layout is in use.

Do not use `exec -a` to rename the `vllm` command: its shebang interpreter
replaces that `argv[0]`. An earlier Ascend environment also reproduced native
EngineCore crashes when using `exec -a NAME python <vllm-script> serve` as a
workaround. Treat that as an observed failure of that launch variant, not a
claim about every Python environment.

## Verify from the host

Inspect the actual host-side views after startup, especially the EngineCore and
Worker rows holding NPU memory:

```bash
npu-smi info
ps -eo pid,comm,args
```

Confirm the owner identifier appears in `npu-smi`'s `Process name` column and
in the main and engine/worker process titles shown by `ps`. Linux `comm` is
limited to 15 bytes; put a short identifier first and verify the rendered
output instead of relying on the full `argv` or launcher logs. Some `npu-smi`
renderings omit punctuation such as `::`. Process tags identify an owner; they
do not reserve a device or resolve a competing claim. Coordinate with the
current owner before changing or stopping an occupied service.
