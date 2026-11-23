# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_dataprotection.manual import helpers

DEFAULT_SUBSCRIPTION = "00000000-0000-0000-0000-00000000000a"
SELECTED_SUBSCRIPTION = "00000000-0000-0000-0000-00000000000b"


def _cmd_with_subscription(subscription_id):
    cmd = mock.MagicMock()
    cmd.cli_ctx.data = {"subscription_id": subscription_id}
    return cmd


@mock.patch("azure.cli.core._profile.Profile.get_subscription_id", return_value=DEFAULT_SUBSCRIPTION)
@mock.patch("azext_dataprotection.manual._client_factory.cf_resource_graph_client")
class ResourceGraphSubscriptionTest(unittest.TestCase):
    """Resource Graph lookups used by --use-secondary-region must honor --subscription."""

    def test_backup_instance_lookup_uses_subscription_argument(self, _client, _default_sub):
        with mock.patch.object(helpers, "dataprotection_backup_instance_list_from_resourcegraph",
                               return_value=[{"id": "bi"}]) as list_bi:
            result = helpers.get_backup_instance_from_resourcegraph(
                _cmd_with_subscription(SELECTED_SUBSCRIPTION), "rg", "vault", "bi")

        self.assertEqual(result, {"id": "bi"})
        self.assertEqual(list_bi.call_args.args[4], [SELECTED_SUBSCRIPTION])

    def test_backup_vault_lookup_uses_subscription_argument(self, _client, _default_sub):
        with mock.patch.object(helpers, "dataprotection_backup_vault_list_from_resourcegraph",
                               return_value=[{"id": "vault"}]) as list_vault:
            result = helpers.get_backup_vault_from_resourcegraph(
                _cmd_with_subscription(SELECTED_SUBSCRIPTION), "rg", "vault")

        self.assertEqual(result, {"id": "vault"})
        self.assertEqual(list_vault.call_args.args[3], [SELECTED_SUBSCRIPTION])

    def test_lookup_falls_back_to_default_subscription(self, _client, _default_sub):
        cmd = mock.MagicMock()
        cmd.cli_ctx.data = {}
        with mock.patch.object(helpers, "dataprotection_backup_vault_list_from_resourcegraph",
                               return_value=[{"id": "vault"}]) as list_vault:
            helpers.get_backup_vault_from_resourcegraph(cmd, "rg", "vault")

        self.assertEqual(list_vault.call_args.args[3], [DEFAULT_SUBSCRIPTION])


if __name__ == "__main__":
    unittest.main()
