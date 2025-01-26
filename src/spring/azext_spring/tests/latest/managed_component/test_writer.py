# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
import io
import unittest
from ....log_stream.writer import DefaultWriter, PrefixWriter


class TestValidateComponentList(unittest.TestCase):
    def test_default_writer(self):
        writer = DefaultWriter()
        buffer = io.StringIO()
        writer.write("test-data", end='', file=buffer)
        self.assertEqual("test-data", buffer.getvalue().strip())

    def test_prefix_writer(self):
        writer = PrefixWriter("prefix")
        buffer = io.StringIO()
        writer.write("test-data", end='', file=buffer)
        self.assertEqual("prefix test-data", buffer.getvalue().strip())
