# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import os
import tempfile
import unittest
from azext_acrcssc.helper._constants import CONTINUOUSPATCH_IMAGE_LIMIT, CONTINUOUSPATCH_IMAGE_LIMIT_TEMPLATE_TOKEN, TMP_DRY_RUN_FILE_NAME
from azext_acrcssc.helper._taskoperations import _create_encoded_task
from azext_acrcssc.helper._utility import convert_cron_to_schedule, convert_timespan_to_cron, create_temporary_dry_run_file
from azure.cli.core.azclierror import InvalidArgumentValueError


class TestCSSCUtilities(unittest.TestCase):
    def test_convert_timespan_to_cron_valid(self):
        # convert_timespan_to_cron() will return a cron that will include the current minute and hour, 
        # only match with the day of the month
        test_cases = [
            ('1d', r'\d+ \d+ \*/1 \* \*'),
            ('5d', r'\d+ \d+ \*/5 \* \*'),
            ('10d', r'\d+ \d+ \*/10 \* \*')
        ]

        for timespan, result in test_cases:
            converted_value = convert_timespan_to_cron(timespan)
            self.assertRegex(converted_value, result)

    def test_convert_timespan_to_cron_invalid(self):
        test_cases = [('12'), ('0d'), ('99d'), ('dd'), ('d')]

        for timespan in test_cases:
            self.assertRaises(InvalidArgumentValueError, convert_timespan_to_cron, timespan)

    def test_convert_cron_to_schedule_valid(self):
        test_cases = [
            ('0 0 */1 * *', '1d'),
            ('0 0 */5 * *', '5d'),
            ('0 0 */10 * *', '10d')
        ]

        for cron, result in test_cases:
            self.assertEqual(convert_cron_to_schedule(cron), result)

    def test_convert_cron_to_schedule_invalid(self):
        test_cases = [('*'), (''), ('* * * * *'), ('dd'), ('d')]

        for cron in test_cases:
            self.assertEqual(convert_cron_to_schedule(cron), None)

    def test_trigger_task_uses_cli_image_limit(self):
        trigger_task = base64.b64decode(_create_encoded_task("task/cssc_trigger_workflow.yaml")).decode("utf-8")
        self.assertIn(f"maxLimit: {CONTINUOUSPATCH_IMAGE_LIMIT}\n", trigger_task)
        self.assertNotIn(CONTINUOUSPATCH_IMAGE_LIMIT_TEMPLATE_TOKEN, trigger_task)

    def test_dry_run_template_uses_cli_image_limit(self):
        with tempfile.TemporaryDirectory() as tmp_folder:
            config_file = os.path.join(tmp_folder, "config.json")
            with open(config_file, "w") as f:
                f.write("{}")
            output_folder = os.path.join(tmp_folder, "out")
            create_temporary_dry_run_file(config_file, output_folder)
            with open(os.path.join(output_folder, TMP_DRY_RUN_FILE_NAME)) as f:
                dry_run_template = f.read()
            self.assertTrue(os.path.exists(os.path.join(output_folder, "config.json")))
        self.assertIn(f"maxLimit: {CONTINUOUSPATCH_IMAGE_LIMIT}", dry_run_template)
        self.assertNotIn(CONTINUOUSPATCH_IMAGE_LIMIT_TEMPLATE_TOKEN, dry_run_template)
