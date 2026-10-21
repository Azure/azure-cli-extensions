# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from azext_cdn.aaz.latest.cdn.profile_migration import Commit as _CDNProfileMigrationCommit
from azext_cdn.custom.custom_cdn import (
    CDNProfileMigrationCommit,
    POST_MIGRATION_ENDPOINT_CUTOVER_NO_WAIT_WARNING,
    POST_MIGRATION_ENDPOINT_CUTOVER_WARNING,
)


class CDNProfileMigrationCommitTest(TestCase):

    @patch('azext_cdn.custom.custom_cdn.logger.warning')
    def test_warning_is_logged_after_synchronous_completion(self, warning_mock):
        command = object.__new__(CDNProfileMigrationCommit)

        command.post_operations()

        warning_mock.assert_called_once_with(POST_MIGRATION_ENDPOINT_CUTOVER_WARNING)

    @patch('azext_cdn.custom.custom_cdn.logger.warning')
    @patch.object(_CDNProfileMigrationCommit, '_handler', return_value=None)
    def test_warning_is_logged_after_no_wait_submission(self, handler_mock, warning_mock):
        command = object.__new__(CDNProfileMigrationCommit)
        command.ctx = SimpleNamespace(lro_no_wait=True)
        command_args = {'no_wait': True}

        result = command._handler(command_args)

        self.assertIsNone(result)
        handler_mock.assert_called_once_with(command_args)
        warning_mock.assert_called_once_with(POST_MIGRATION_ENDPOINT_CUTOVER_NO_WAIT_WARNING)

    @patch('azext_cdn.custom.custom_cdn.logger.warning')
    @patch.object(_CDNProfileMigrationCommit, '_handler', return_value='poller')
    def test_warning_waits_for_synchronous_post_operations(self, handler_mock, warning_mock):
        command = object.__new__(CDNProfileMigrationCommit)
        command.ctx = SimpleNamespace(lro_no_wait=False)
        command_args = {'no_wait': False}

        result = command._handler(command_args)

        self.assertEqual('poller', result)
        handler_mock.assert_called_once_with(command_args)
        warning_mock.assert_not_called()