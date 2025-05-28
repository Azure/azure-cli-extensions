# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# flake8: noqa

import subprocess
import unittest
from unittest import mock

from azext_networkcloud.operations.custom_properties import CustomActionProperties
from azure.cli.core.aaz._base import AAZUndefined
from azure.cli.core.azclierror import AzureInternalError


class TestCustomProperties(unittest.TestCase):
    """Test CustomProperties methods"""

    def test_resulturl_output(self):
        self.cmd = mock.Mock()

        # Mock args
        args = mock.Mock()
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        # Mock deserialize method
        self.cmd.deserialize_output.return_value = mock.Mock()

        # Mock vars
        self.cmd.ctx.vars = mock.Mock()
        self.cmd.ctx.vars.instance = mock.Mock()

        # Mock output head
        self.cmd.ctx.vars.instance.properties = mock.Mock()
        self.cmd.ctx.vars.instance.properties.output_head = mock.Mock()
        self.cmd.ctx.vars.instance.properties.output_head.to_serialized_data = (
            mock.Mock(side_effect="HEADER")
        )

        # Validate URL download skipped when result URL not provided
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            # Set result url to undefined
            self.cmd.ctx.vars.instance.properties.resultUrl = AAZUndefined
            self.cmd.ctx.vars.instance.properties.resultRef = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_urlopen.assert_not_called()

        # Mock result URL
        test_url = "https://aka.ms/fakeurl"
        self.cmd.ctx.vars.instance.properties.resultUrl = mock.Mock()
        self.cmd.ctx.vars.instance.properties.resultUrl.to_serialized_data = mock.Mock(
            side_effect=test_url
        )

        # Validate results not downloaded when no output dir provided
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_urlopen.assert_not_called()

        # Validate exceptions handled
        with mock.patch("urllib.request.urlopen") as mock_urlopen:
            test_output_dir = "/path/to/test/output/dir"
            self.cmd.ctx.args.output = mock.Mock()
            self.cmd.ctx.args.output.to_serialized_data.return_value = test_output_dir

            # Raise exception when calling tar lib
            with mock.patch("tarfile.open") as tar_open:
                tar_open.side_effect = Exception
                with self.assertRaises(Exception):
                    CustomActionProperties()._output(self.cmd, args)

            # Raise exception when calling URL
            mock_urlopen.side_effect = Exception
            with self.assertRaises(Exception):
                CustomActionProperties()._output(self.cmd, args)

    def test_resultref_output(self):
        self.cmd = mock.Mock()

        # Mock args
        args = mock.Mock()
        self.cmd.ctx = mock.Mock()
        self.cmd.ctx.args = args

        # Validate URL download skipped when resultRef not provided
        with mock.patch("subprocess.run") as mock_subprocess_run:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            # Set result url to undefined
            self.cmd.ctx.vars.instance.properties.resultRef = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_subprocess_run.assert_not_called()

        # Mock result URL
        test_url = "https://aka.ms/fakeurl"
        self.cmd.ctx.vars.instance.properties.resultRef = mock.Mock()
        self.cmd.ctx.vars.instance.properties.resultRef.to_serialized_data = mock.Mock(
            side_effect=test_url
        )

        # Validate results not downloaded when no output dir provided
        with mock.patch("subprocess.run") as mock_subprocess_run:
            # Set output dir to undefined
            self.cmd.ctx.args.output = AAZUndefined

            CustomActionProperties()._output(self.cmd, args)
            mock_subprocess_run.assert_not_called()

        # Validate exceptions handled
        with mock.patch("subprocess.run") as mock_subprocess_run:
            test_output_dir = "/path/to/test/output/dir"
            self.cmd.ctx.args.output = test_output_dir

            # Simulate subprocess.run raising an error
            mock_subprocess_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd="az storage blob download", stderr="Simulated error"
            )

            # Raise exception when downloading blob
            mock_subprocess_run.side_effect = Exception
            with self.assertRaises(AzureInternalError) as cm:
                CustomActionProperties()._output(self.cmd, args)
