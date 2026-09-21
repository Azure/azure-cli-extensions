# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_storage_container


def load_command_table(self, _):
    data_product_sdk = CliCommandType(
        operations_tmpl="azext_network_analytics.vendored_sdks.data_product.operations#IngestOperations.{}",
        client_factory=cf_storage_container,
    )

    with self.command_group('network-analytics data-product', data_product_sdk, is_preview=True) as g:
        g.custom_command('ingest', 'data_product_ingest')
