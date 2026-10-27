# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Check that missing recordings cannot trigger implicit live Graph calls."""

import unittest
from unittest.mock import Mock, patch

from ..latest import test_nexusidentity_scenario as _scenario


class TestRecordingSafety(unittest.TestCase):
    def test_missing_recording_requires_explicit_live_mode(self):
        test = _scenario.NexusIdentityScenarioTest("test_nexusidentity_key_publication")
        test.in_recording = True
        test.is_live = False
        with patch.object(_scenario.ScenarioTest, "setUp") as setup:
            with self.assertRaisesRegex(
                AssertionError, "Record explicitly with make aaz-test-live"
            ):
                test.setUp()
        setup.assert_not_called()

    def test_explicit_recording_and_existing_playback_are_allowed(self):
        for in_recording, is_live in ((True, True), (False, False)):
            with self.subTest(in_recording=in_recording, is_live=is_live):
                test = _scenario.NexusIdentityScenarioTest(
                    "test_nexusidentity_key_publication"
                )
                test.in_recording = in_recording
                test.is_live = is_live
                with patch.object(_scenario.ScenarioTest, "setUp") as setup:
                    test.setUp()
                setup.assert_called_once_with()

    def test_existing_extension_is_never_replaced(self):
        existing = {"value": [{"id": "com.nexusidentity.keys"}]}
        for pages in (
            [existing],
            [
                {
                    "value": [],
                    "@odata.nextLink": "https://graph.microsoft.com/v1.0/me/extensions?$skip=1",
                },
                existing,
            ],
        ):
            with self.subTest(pages=len(pages)):
                test = _scenario.NexusIdentityScenarioTest(
                    "test_nexusidentity_key_publication"
                )
                test.cmd = Mock(return_value=Mock(spec=["get_output_in_json"]))
                test.cmd.return_value.get_output_in_json.side_effect = pages
                with self.assertRaisesRegex(
                    AssertionError, "existing keys will not be replaced"
                ):
                    test.test_nexusidentity_key_publication()
                self.assertEqual(test.cmd.call_count, len(pages))
                for command in test.cmd.call_args_list:
                    self.assertTrue(command.args[0].startswith("az rest --method get"))
