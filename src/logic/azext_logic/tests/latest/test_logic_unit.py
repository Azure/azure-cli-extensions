import ast
import os
import textwrap
import unittest
from types import SimpleNamespace

import yaml


def _extract_function(func_name):
    src_path = os.path.join(os.path.dirname(__file__), "..", "..", "custom.py")
    src_path = os.path.normpath(src_path)
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=src_path)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_source = ast.get_source_segment(source, node)
            namespace = {"yaml": yaml}
            exec(compile(textwrap.dedent(func_source), src_path, "exec"), namespace)  # pylint: disable=exec-used
            return namespace[func_name]

    raise ValueError(f"Function {func_name!r} not found in {src_path}")


class TestFormatWorkflowShowOutput(unittest.TestCase):

    def test_yaml_output_disables_wrapping_for_long_expression(self):
        formatter = _extract_function("_format_workflow_show_output")
        cli_ctx = SimpleNamespace(invocation=SimpleNamespace(data={"output": "yaml"}))
        expression = "@greaterOrEquals(ticks(addSeconds(utcNow(), 5)) ,ticks(convertToUtc('2050-06-01T00:00:00', 'Tokyo Standard Time')))"
        result = {
            "definition": {
                "actions": {
                    "Compose": {
                        "inputs": expression,
                        "runAfter": {},
                        "type": "Compose",
                    }
                }
            }
        }

        output = formatter(cli_ctx, result)

        self.assertEqual(cli_ctx.invocation.data["output"], "tsv")
        self.assertIn(
            "inputs: '@greaterOrEquals(ticks(addSeconds(utcNow(), 5)) ,ticks(convertToUtc(''2050-06-01T00:00:00'', ''Tokyo Standard Time'')))'",
            output,
        )
        self.assertNotIn("\n        ''Tokyo Standard Time'')))'", output)
        self.assertEqual(yaml.safe_load(output), result)

    def test_non_yaml_output_is_unchanged(self):
        formatter = _extract_function("_format_workflow_show_output")
        cli_ctx = SimpleNamespace(invocation=SimpleNamespace(data={"output": "json"}))
        result = {"name": "workflow"}

        output = formatter(cli_ctx, result)

        self.assertIs(output, result)
        self.assertEqual(cli_ctx.invocation.data["output"], "json")
