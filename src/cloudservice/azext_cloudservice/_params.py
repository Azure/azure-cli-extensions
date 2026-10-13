# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import (
    tags_type, get_three_state_flag, get_enum_type, resource_group_name_type, get_location_type, file_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group, validate_file_or_dict


def load_arguments(self, _):

    with self.argument_context('cloud-service create') as c:
        c.argument('cloud_service_name', options_list=['--name', '-n', '--cloud-service-name'], type=str,
                   help='Name of the cloud service.')
        c.argument('configuration', type=file_type, help='Specify the XML service configuration (.cscfg) '
                   'for the cloud service. Expected value: xml-string/@xml-file.')
        c.argument('configuration_url', type=str, help='Specify a URL that refers to the location of the service '
                   'configuration in the Blob service. The service package URL  can be Shared Access Signature (SAS) '
                   'URI from any storage account. This is a write-only property and is not returned in GET calls.')
        c.argument('extensions', type=validate_file_or_dict, arg_group='Extension Profile',
                   help='List of extensions for the cloud service. Expected value: json-string/@json-file. Example: '
                   '[{"properties": {"type": "RDP", "autoUpgradeMinorVersion": false, "protectedSettings": "settings",'
                   '"publisher": "Microsoft.Windows.Azure.Extensions", "settings": "settings", '
                   '"typeHandlerVersion": "1.2.1"}, "name": "RDPExtension"}]')
        c.argument('id_', options_list=['--id'], type=str, help='Resource Id',
                   arg_group='Network Profile Swappable Cloud Service')
        c.argument('load_balancer_configurations', nargs='+', type=str, arg_group='Network Profile',
                   options_list=['--load-balancer-configurations', '--lb'],
                   help='The list of load balancer configurations separated by space for the cloud service. '
                   'The public IP is a mandatory field. Format: '
                   'LBName:FrontendIPConfiguration:PublicIPAddress:Subnet:PrivateIP.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('package_url', type=str, help='Specify a URL that refers to the location of the service package '
                   'in the Blob service. The service package URL can be Shared Access Signature (SAS) URI from any '
                   'storage account. This is a write-only property and is not returned in GET calls.')
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('roles', nargs='+', type=str, help='List of roles separated by space for the cloud service. '
                   'Format: RoleName:SkuName:SkuCapacity:SkuTier.', arg_group='Role Profile')
        c.argument('secrets', nargs='+', type=str, arg_group='Os Profile',
                   help='Specify certificates separated by space that should be installed onto the role instances. '
                   'Format: KeyVaultName:CertificateUrl:CertificateUrl2:...:CertificateUrlN.')
        c.argument('start_cloud_service', arg_type=get_three_state_flag(), help='Indicate whether to start '
                   'the cloud service immediately after it is created. The default value is `true`. If false, the '
                   'service model is still deployed, but the code is not run immediately. Instead, the service is '
                   'PoweredOff until you call Start, at which time the service will be started. A deployed service '
                   'still incurs charges, even if it is poweredoff.')
        c.argument('tags', tags_type)
        c.argument('upgrade_mode', arg_type=get_enum_type(['Auto', 'Manual', 'Simultaneous']), help='Update mode for '
                   'the cloud service. Role instances are allocated to update domains when the service is deployed. '
                   'Updates can be initiated manually in each update domain or initiated automatically in all update '
                   'domains. Possible Values are Auto, Manual, Simultaneous. '
                   'If not specified, the default value is Auto. If set to Manual, PUT '
                   'UpdateDomain must be called to apply the update. If set to Auto, the update is automatically '
                   'applied to each update domain in sequence.')
