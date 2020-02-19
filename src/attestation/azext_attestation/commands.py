# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_operations
    attestation_operations = CliCommandType(
        operations_tmpl='azext_attestation.vendored_sdks.attestation.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('attestation operations', attestation_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'attestation_operations_list')

    from ._client_factory import cf_attestation_providers
    attestation_attestation_providers = CliCommandType(
        operations_tmpl='azext_attestation.vendored_sdks.attestation.operations._attestation_providers_operations#AttestationProvidersOperations.{}',
        client_factory=cf_attestation_providers)
    with self.command_group('attestation attestation_providers', attestation_attestation_providers, client_factory=cf_attestation_providers) as g:
        g.custom_command('list', 'attestation_attestation_providers_list')
        g.custom_show_command('show', 'attestation_attestation_providers_show')
        g.custom_command('create', 'attestation_attestation_providers_create')
        g.custom_command('delete', 'attestation_attestation_providers_delete')
