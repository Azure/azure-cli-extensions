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

    from ._client_factory import cf_legacy_peerings
    peering_legacy_peerings = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._legacy_peerings_operations#LegacyPeeringsOperations.{}',
        client_factory=cf_legacy_peerings)
    with self.command_group('peering legacy', peering_legacy_peerings, client_factory=cf_legacy_peerings) as g:
        g.custom_command('list', 'list_peering_legacy')

    from ._client_factory import cf_peer_asns
    peering_peer_asns = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._peer_asns_operations#PeerAsnsOperations.{}',
        client_factory=cf_peer_asns)
    with self.command_group('peering asn', peering_peer_asns, client_factory=cf_peer_asns) as g:
        g.custom_command('create', 'create_peering_asn')
        g.custom_command('update', 'update_peering_asn')
        g.custom_command('delete', 'delete_peering_asn')
        g.custom_command('list', 'list_peering_asn')
        g.show_command('show', 'get')

    from ._client_factory import cf_peering_locations
    peering_peering_locations = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._peering_locations_operations#PeeringLocationsOperations.{}',
        client_factory=cf_peering_locations)
    with self.command_group('peering location', peering_peering_locations, client_factory=cf_peering_locations) as g:
        g.custom_command('list', 'list_peering_location')

    from ._client_factory import cf_peerings
    peering_peerings = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._peerings_operations#PeeringsOperations.{}',
        client_factory=cf_peerings)
    with self.command_group('peering', peering_peerings, client_factory=cf_peerings) as g:
        g.custom_command('create', 'create_peering')
        g.custom_command('update', 'update_peering')
        g.custom_command('delete', 'delete_peering')
        g.custom_command('list', 'list_peering')
        g.show_command('show', 'get')

    from ._client_factory import cf_peering_service_locations
    peering_peering_service_locations = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._peering_service_locations_operations#PeeringServiceLocationsOperations.{}',
        client_factory=cf_peering_service_locations)
    with self.command_group('peering service location', peering_peering_service_locations, client_factory=cf_peering_service_locations) as g:
        g.custom_command('list', 'list_peering_service_location')

    from ._client_factory import cf_prefixes
    peering_prefixes = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._prefixes_operations#PrefixesOperations.{}',
        client_factory=cf_prefixes)
    with self.command_group('peering service prefix', peering_prefixes, client_factory=cf_prefixes) as g:
        g.custom_command('create', 'create_peering_service_prefix')
        g.custom_command('update', 'update_peering_service_prefix')
        g.custom_command('delete', 'delete_peering_service_prefix')
        g.custom_command('list', 'list_peering_service_prefix')
        g.show_command('show', 'get')

    from ._client_factory import cf_peering_service_providers
    peering_peering_service_providers = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._peering_service_providers_operations#PeeringServiceProvidersOperations.{}',
        client_factory=cf_peering_service_providers)
    with self.command_group('peering service provider', peering_peering_service_providers, client_factory=cf_peering_service_providers) as g:
        g.custom_command('list', 'list_peering_service_provider')

    from ._client_factory import cf_peering_services
    peering_peering_services = CliCommandType(
        operations_tmpl='azext_peering.vendored_sdks.peering.operations._peering_services_operations#PeeringServicesOperations.{}',
        client_factory=cf_peering_services)
    with self.command_group('peering service', peering_peering_services, client_factory=cf_peering_services) as g:
        g.custom_command('create', 'create_peering_service')
        g.custom_command('update', 'update_peering_service')
        g.custom_command('delete', 'delete_peering_service')
        g.custom_command('list', 'list_peering_service')
        g.show_command('show', 'get')
