# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ValidationError, InvalidArgumentValueError, ArgumentUsageError
from ._client_factory import web_client_factory, cf_resource_groups


def _normalize_sku(sku):
    sku = sku.upper()
    if sku == 'FREE':
        return 'F1'
    if sku == 'SHARED':
        return 'D1'
    if sku in ('ANY', 'ELASTICANY'):  # old kube skus
        return 'K1'
    if sku == 'KUBE':
        return 'K1'
    return sku


def _validate_asp_sku(app_service_environment, custom_location, sku):
    # Isolated SKU is supported only for ASE
    if sku.upper() not in ['F1', 'FREE', 'D1', 'SHARED', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1V2', 'P1V3', 'P2V2',
                           'P3V2', 'PC2', 'PC3', 'PC4', 'I1', 'I2', 'I3', 'K1']:
        raise InvalidArgumentValueError(f'Invalid sku entered: {sku}')

    if sku.upper() in ['I1', 'I2', 'I3', 'I1V2', 'I2V2', 'I3V2']:
        if not app_service_environment:
            raise ValidationError("The pricing tier 'Isolated' is not allowed for this app service plan. "
                                  "Use this link to learn more: "
                                  "https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans")
    elif app_service_environment:
        raise ValidationError("Only pricing tier 'Isolated' is allowed in this app service plan. Use this link to "
                              "learn more: https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans")
    elif custom_location:
        # Custom Location only supports K1
        if sku.upper() != 'K1':
            raise ValidationError("Only pricing tier 'K1' is allowed for this type of app service plan.")


def get_sku_name(tier):  # pylint: disable=too-many-return-statements
    tier = tier.upper()
    if tier in ['F1', 'FREE']:
        return 'FREE'
    if tier in ['D1', "SHARED"]:
        return 'SHARED'
    if tier in ['B1', 'B2', 'B3', 'BASIC']:
        return 'BASIC'
    if tier in ['S1', 'S2', 'S3']:
        return 'STANDARD'
    if tier in ['P1', 'P2', 'P3']:
        return 'PREMIUM'
    if tier in ['P1V2', 'P2V2', 'P3V2']:
        return 'PREMIUMV2'
    if tier in ['P1V3', 'P2V3', 'P3V3']:
        return 'PREMIUMV3'
    if tier in ['PC2', 'PC3', 'PC4']:
        return 'PremiumContainer'
    if tier in ['EP1', 'EP2', 'EP3']:
        return 'ElasticPremium'
    if tier in ['I1', 'I2', 'I3']:
        return 'Isolated'
    if tier in ['I1V2', 'I2V2', 'I3V2']:
        return 'IsolatedV2'
    if tier in ['K1']:
        return 'Kubernetes'
    raise InvalidArgumentValueError("Invalid sku(pricing tier), please refer to command help for valid values")


def validate_subnet_id(cli_ctx, subnet, vnet_name, resource_group_name):
    from msrestazure.tools import is_valid_resource_id
    subnet_is_id = is_valid_resource_id(subnet)

    if subnet_is_id and not vnet_name:
        return subnet
    if subnet and not subnet_is_id and vnet_name:
        from msrestazure.tools import resource_id
        from azure.cli.core.commands.client_factory import get_subscription_id
        return resource_id(
            subscription=get_subscription_id(cli_ctx),
            resource_group=resource_group_name,
            namespace='Microsoft.Network',
            type='virtualNetworks',
            name=vnet_name,
            child_type_1='subnets',
            child_name_1=subnet)
    raise ArgumentUsageError('Usage error: --subnet ID | --subnet NAME --vnet-name NAME')


def validate_aks_id(cli_ctx, aks, resource_group_name):
    from msrestazure.tools import is_valid_resource_id
    aks_is_id = is_valid_resource_id(aks)

    if aks_is_id:
        return aks
    if aks and not aks_is_id:
        from msrestazure.tools import resource_id
        from azure.cli.core.commands.client_factory import get_subscription_id
        return resource_id(
            subscription=get_subscription_id(cli_ctx),
            resource_group=resource_group_name,
            namespace='Microsoft.ContainerService',
            type='managedClusters',
            name=aks)
    raise ArgumentUsageError('Usage error: --aks')


def _generic_site_operation(cli_ctx, resource_group_name, name, operation_name, slot=None,
                            extra_parameter=None, client=None, api_version=None):
    # api_version was added to support targeting a specific API
    # Based on get_appconfig_service_client example
    client = client or web_client_factory(cli_ctx, api_version=api_version)
    operation = getattr(client.web_apps,
                        operation_name if slot is None else operation_name + '_slot')
    if slot is None:
        return (operation(resource_group_name, name)
                if extra_parameter is None else operation(resource_group_name,
                                                          name, extra_parameter))
    return (operation(resource_group_name, name, slot)
            if extra_parameter is None else operation(resource_group_name,
                                                      name, slot, extra_parameter))


def _get_location_from_resource_group(cli_ctx, resource_group_name):
    client = cf_resource_groups(cli_ctx)
    group = client.get(resource_group_name)
    return group.location
