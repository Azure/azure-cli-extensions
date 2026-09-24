#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import textwrap
import unittest


def _load_raw_deserializer_class():
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "vendored_sdks", "subscription", "_serialization.py"))
    with open(src_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=src_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RawDeserializer":
            for method in node.body:
                if isinstance(method, ast.FunctionDef) and method.name == "deserialize_from_http_generics":
                    method_source = ast.get_source_segment(source, method)
                    method_source = textwrap.indent(textwrap.dedent(method_source), "    ")
                    class_source = f"""
class RawDeserializer:
    @classmethod
{method_source}
    @classmethod
    def deserialize_from_text(cls, data, content_type=None):
        return data, content_type
"""
                    namespace = {}
                    exec(class_source, namespace)  # pylint: disable=exec-used
                    return namespace["RawDeserializer"]
    raise ValueError("RawDeserializer.deserialize_from_http_generics not found")


class TestRawDeserializer(unittest.TestCase):

    def test_deserialize_from_http_generics_handles_none_headers(self):
        raw_deserializer = _load_raw_deserializer_class()
        data, content_type = raw_deserializer.deserialize_from_http_generics(b'{"value": []}', None)
        self.assertEqual(data, b'{"value": []}')
        self.assertEqual(content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
