#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${RUN_DIR:-$PWD}"
INPUT_LEN="${INPUT_LEN:-2048}"
OUTPUT_LEN="${OUTPUT_LEN:-2048}"
DATA_NUM="${DATA_NUM:-4}"
CONCURRENCY="${CONCURRENCY:-1}"
REQUEST_RATE="${REQUEST_RATE:-0}"
TEST_TYPE="${TEST_TYPE:-stream}"
REPEAT="${REPEAT:-1}"
NPU_NUM="${NPU_NUM:-32}"
DATASET_TYPE="${DATASET_TYPE:-normal}"
REPEAT_RATE="${REPEAT_RATE:-0}"
PREFIX_NUM="${PREFIX_NUM:-1}"
DP_SIZE="${DP_SIZE:-1}"
SEED="${SEED:-1}"
WARMUP="${WARMUP:-1}"
WARMUP_DATA_NUM="${WARMUP_DATA_NUM:-}"
WARMUP_REQUEST_RATE="${WARMUP_REQUEST_RATE:-}"
PREFIX_TEST="${PREFIX_TEST:-0}"
DATASET_FILE="${DATASET_FILE:-}"

if [[ "${WARMUP}" == "1" ]]; then
  if [[ -z "${WARMUP_REQUEST_RATE}" ]]; then
    # REQUEST_RATE=0 is already the fastest, concurrency-limited mode.
    WARMUP_REQUEST_RATE="$(python3 - "${REQUEST_RATE}" <<'PY'
from decimal import Decimal
import sys

rate = Decimal(sys.argv[1])
if rate < 0 or not rate.is_finite():
    raise ValueError("REQUEST_RATE must be a finite nonnegative number")
warmup_rate = rate * Decimal("1.5") if rate else rate
formatted = format(warmup_rate, "f")
print(formatted.rstrip("0").rstrip(".") if "." in formatted else formatted)
PY
)"
  fi
  if [[ -z "${WARMUP_DATA_NUM}" ]]; then
    # At least two concurrency waves, with a modest floor for longer cases.
    WARMUP_DATA_NUM="$(python3 - "${CONCURRENCY}" "${DATA_NUM}" <<'PY'
import sys

concurrency, formal_count = map(int, sys.argv[1:])
if concurrency < 1 or formal_count < 1:
    raise ValueError("CONCURRENCY and DATA_NUM must be positive integers")
print(max(2 * concurrency, min(formal_count, 16)))
PY
)"
  fi
  if [[ ! "${WARMUP_DATA_NUM}" =~ ^[1-9][0-9]*$ ]]; then
    echo "WARMUP_DATA_NUM must be a positive integer: ${WARMUP_DATA_NUM}" >&2
    exit 2
  fi
fi

cd "${RUN_DIR}"
if [[ ! -f aisbench_test.py || ! -f config.py ]]; then
  echo "RUN_DIR is not an AISBench run prepared by prepare_run.py: ${RUN_DIR}" >&2
  exit 2
fi
if [[ "${WARMUP}" == "1" ]]; then
  printf 'warmup_data_num=%s\nwarmup_request_rate=%s\nformal_data_num=%s\nformal_request_rate=%s\n' \
    "${WARMUP_DATA_NUM}" "${WARMUP_REQUEST_RATE}" "${DATA_NUM}" "${REQUEST_RATE}" \
    > warmup_settings.txt
fi

common_args=(
  --input_len "${INPUT_LEN}"
  --output_len "${OUTPUT_LEN}"
  --concurrency "${CONCURRENCY}"
  --test_type "${TEST_TYPE}"
  --repeat "${REPEAT}"
  --npu_num "${NPU_NUM}"
  --dataset_type "${DATASET_TYPE}"
  --repeat_rate "${REPEAT_RATE}"
  --prefix_num "${PREFIX_NUM}"
  --dp "${DP_SIZE}"
  --seed "${SEED}"
)

run_one() {
  local label="$1"
  local count="$2"
  local request_rate="$3"
  local use_dataset="$4"
  local use_prefix_test="$5"
  local args=("${common_args[@]}" --request_rate "${request_rate}" --data_num "${count}")
  if [[ -n "${use_dataset}" ]]; then
    args+=(--dataset "${use_dataset}")
  fi
  if [[ "${use_prefix_test}" == "1" ]]; then
    args+=(--prefix_test)
  fi

  {
    printf '%q ' python3 aisbench_test.py "${args[@]}"
    printf '\n'
  } > "${label}_command.txt"

  set +e
  python3 aisbench_test.py "${args[@]}" 2>&1 | tee "${label}_console.log" >&2
  LAST_RC="${PIPESTATUS[0]}"
  set -e
  printf '%s\n' "${LAST_RC}" > "${label}_return_code.txt"
}

LAST_RC=0
warmup_rc=0
if [[ "${WARMUP}" == "1" ]]; then
  # Regenerate from the same seed so a prefix-cache warmup uses the same prefix.
  run_one warmup "${WARMUP_DATA_NUM}" "${WARMUP_REQUEST_RATE}" "" 0
  warmup_rc="${LAST_RC}"
  if [[ "${warmup_rc}" -ne 0 ]]; then
    python3 - "$RUN_DIR" "$warmup_rc" <<'PY'
import json, sys
print(json.dumps({
    "status": "warmup_failed",
    "run_dir": sys.argv[1],
    "warmup_return_code": int(sys.argv[2]),
    "warmup_console": f"{sys.argv[1]}/warmup_console.log",
}, separators=(",", ":")))
PY
    exit "${warmup_rc}"
  fi
fi

run_one formal "${DATA_NUM}" "${REQUEST_RATE}" "${DATASET_FILE}" "${PREFIX_TEST}"
formal_rc="${LAST_RC}"
python3 - "$RUN_DIR" "$warmup_rc" "$formal_rc" <<'PY'
import json, sys
print(json.dumps({
    "status": "ok" if int(sys.argv[3]) == 0 else "formal_failed",
    "run_dir": sys.argv[1],
    "warmup_return_code": int(sys.argv[2]),
    "formal_return_code": int(sys.argv[3]),
    "formal_command": f"{sys.argv[1]}/formal_command.txt",
    "formal_console": f"{sys.argv[1]}/formal_console.log",
}, separators=(",", ":")))
PY
exit "${formal_rc}"
