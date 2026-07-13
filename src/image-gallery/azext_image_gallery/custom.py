# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.azclierror import RequiredArgumentMissingError


def sig_community_image_definition_list(cmd, location, public_gallery_name, pagination_limit=None,
                                        pagination_token=None):
    from azure.cli.command_modules.vm.aaz.latest.sig.image_definition import ListCommunity
    return ListCommunity(cli_ctx=cmd.cli_ctx)(command_args={
        'location': location,
        'public_gallery_name': public_gallery_name,
        'pagination_limit': pagination_limit,
        'pagination_token': pagination_token
    })


def sig_community_image_version_list(cmd, location, public_gallery_name, gallery_image_name,
                                     pagination_limit=None, pagination_token=None):
    from azure.cli.command_modules.vm.aaz.latest.sig.image_version import ListCommunity
    return ListCommunity(cli_ctx=cmd.cli_ctx)(command_args={
        'location': location,
        'public_gallery_name': public_gallery_name,
        'gallery_image_definition': gallery_image_name,
        'pagination_limit': pagination_limit,
        'pagination_token': pagination_token
    })


def _get_resource_group_location(cli_ctx, resource_group_name):
    client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    # pylint: disable=no-member
    return client.resource_groups.get(resource_group_name).location


def create_image_gallery(cmd, resource_group_name, gallery_name, description=None, location=None,
                         no_wait=False, tags=None, permissions=None, soft_delete=None, publisher_uri=None,
                         publisher_contact=None, eula=None, public_name_prefix=None):
    from azure.cli.command_modules.vm.operations.sig import SigCreate
    location = location or _get_resource_group_location(cmd.cli_ctx, resource_group_name)
    command_args = {
        'resource_group': resource_group_name,
        'gallery_name': gallery_name,
        'location': location,
        'tags': tags or {},
        'no_wait': no_wait,
    }

    if description is not None:
        command_args['description'] = description

    if soft_delete is not None:
        command_args['soft_delete'] = soft_delete

    if permissions:
        command_args['permissions'] = permissions
        if permissions == 'Community':
            if publisher_uri is None \
                    or publisher_contact is None \
                    or eula is None \
                    or public_name_prefix is None:
                raise RequiredArgumentMissingError('If you want to share to the community, '
                                                   'you need to fill in all the following parameters:'
                                                   ' --publisher-uri, --publisher-email, --eula, --public-name-prefix.')

            command_args['publisher_uri'] = publisher_uri
            command_args['publisher_contact'] = publisher_contact
            command_args['eula'] = eula
            command_args['public_name_prefix'] = public_name_prefix
    return SigCreate(cli_ctx=cmd.cli_ctx)(command_args=command_args)


def sig_community_gallery_show(cmd, location, public_gallery_name):
    from azure.cli.command_modules.vm.aaz.latest.sig import ShowCommunity
    return ShowCommunity(cli_ctx=cmd.cli_ctx)(command_args={
        'location': location,
        'public_gallery_name': public_gallery_name,
    })


def sig_community_gallery_image_show(cmd, location, public_gallery_name, gallery_image_name):
    from azure.cli.command_modules.vm.aaz.latest.sig.image_definition import ShowCommunity
    return ShowCommunity(cli_ctx=cmd.cli_ctx)(command_args={
        'location': location,
        'public_gallery_name': public_gallery_name,
        'gallery_image_definition': gallery_image_name,
    })


def sig_community_image_version_show(cmd, location, public_gallery_name, gallery_image_name,
                                     gallery_image_version_name):
    from azure.cli.command_modules.vm.aaz.latest.sig.image_version import ShowCommunity
    return ShowCommunity(cli_ctx=cmd.cli_ctx)(command_args={
        'location': location,
        'public_gallery_name': public_gallery_name,
        'gallery_image_definition': gallery_image_name,
        'gallery_image_version_name': gallery_image_version_name,
    })


def sig_share_enable_community(cmd, resource_group_name, gallery_name, subscription_ids=None, tenant_ids=None,
                               no_wait=False, op_type=None):
    from azure.cli.command_modules.vm.operations.sig_share import SigShareEnableCommunity

    if op_type != 'EnableCommunity' and subscription_ids is None and tenant_ids is None:
        raise RequiredArgumentMissingError('At least one of subscription ids or tenant ids must be provided')

    command_args = {
        'resource_group': resource_group_name,
        'gallery_name': gallery_name,
        'no_wait': no_wait,
    }
    if subscription_ids:
        command_args['subscription_ids'] = subscription_ids
    if tenant_ids:
        command_args['tenant_ids'] = tenant_ids
    if op_type:
        command_args['operation_type'] = op_type
    return SigShareEnableCommunity(cli_ctx=cmd.cli_ctx)(command_args=command_args)