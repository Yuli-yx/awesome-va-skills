"""Exercise probe helpers without running SSH, imports or NPU discovery."""

import ast
import json
from pathlib import Path
import re
import unittest


class ProbeRedactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / "scripts/remote_orchestrator.py"
        module = ast.parse(source.read_text(encoding="utf-8"))
        probe = next(node.value.value for node in module.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "PROBE" for target in node.targets))
        tree = ast.parse(probe)
        helpers = [node for node in tree.body if
                   (isinstance(node, ast.FunctionDef) and node.name in {"redact", "redact_argv"}) or
                   (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SECRET_KEY" for target in node.targets))]
        namespace = {"re": re, "json": json}
        exec(compile(ast.Module(body=helpers, type_ignores=[]), "probe-helpers", "exec"), namespace)
        cls.helpers = namespace

    def test_command_credentials_are_redacted_without_losing_token_budget(self):
        result = self.helpers["redact_argv"]([
            "vllm", "serve", "example", "--api-key", "fixture-secret-a",
            "--password=fixture-secret-b", "--max-tokens", "100",
            '{"auth_token":"fixture-secret-c","max_tokens":100}',
        ])
        encoded = json.dumps(result)
        self.assertNotIn("fixture-secret", encoded)
        self.assertIn("100", encoded)
        self.assertEqual(json.loads(result[-1])["max_tokens"], 100)

    def test_nested_config_credentials_and_environment_keys(self):
        result = self.helpers["redact"]({"nested": [{"api_key": "fixture-secret", "max_tokens": 4}]})
        self.assertEqual(result["nested"][0], {"api_key": "<redacted>", "max_tokens": 4})
        self.assertIsNotNone(self.helpers["SECRET_KEY"].search("VLLM_API_KEY"))
        self.assertIsNone(self.helpers["SECRET_KEY"].search("VLLM_MAX_MODEL_LEN"))


if __name__ == "__main__":
    unittest.main()
