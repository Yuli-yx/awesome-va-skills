"""Offline helper regression checks; no AISBench or service is started."""

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parents[1]


class HelperTests(unittest.TestCase):
    def test_warmup_rates_preserve_integer_zeroes_and_fractional_rates(self):
        script = (PACKAGE / "scripts/run_case.sh").read_text(encoding="utf-8")
        code = re.findall(r"<<'PY'\n(.*?)\nPY", script, re.S)[0]
        for rate, expected in (("0", "0"), ("20", "30"), ("2e1", "30"), ("0.02", "0.03")):
            with self.subTest(rate=rate):
                result = subprocess.run([sys.executable, "-", rate], input=code, text=True, capture_output=True, check=True)
                self.assertEqual(result.stdout.strip(), expected)

    def test_invalid_warmup_rate_fails(self):
        script = (PACKAGE / "scripts/run_case.sh").read_text(encoding="utf-8")
        code = re.findall(r"<<'PY'\n(.*?)\nPY", script, re.S)[0]
        for rate in ("-1", "Infinity", "NaN"):
            result = subprocess.run([sys.executable, "-", rate], input=code, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_preparation_preserves_shared_tool_and_refuses_implicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tool, run = root / "tool", root / "run"
            tool.mkdir()
            config = "\n".join(name + " = ''" for name in (
                "DATASET_PATH", "WORK_PATH", "MODEL_NAME", "MODEL_PATH",
                "HOST_IP", "HOST_PORT", "OUTPUT_DIR", "POD_INFO",
            ))
            (tool / "config.py").write_text(config, encoding="utf-8")
            for name in ("aisbench_test.py", "default_api.py", "generate_dataset.py", "save_file.py"):
                (tool / name).write_text("# Fixture only\n", encoding="utf-8")
            command = [sys.executable, str(PACKAGE / "scripts/prepare_run.py"),
                       "--tool-dir", str(tool), "--run-dir", str(run),
                       "--model-name", "example", "--model-path", "/models/example",
                       "--host-ip", "192.0.2.1", "--host-port", "8000",
                       "--work-path", "/opt/aisbench"]
            subprocess.run(command, capture_output=True, check=True)
            self.assertEqual((tool / "config.py").read_text(encoding="utf-8"), config)
            generated = json.loads((run / "run_config.json").read_text(encoding="utf-8"))
            self.assertEqual(generated["HOST_IP"], "192.0.2.1")
            self.assertTrue((run / "datasets").is_dir())
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
