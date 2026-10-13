# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-locals, too-many-arguments, too-many-positional-arguments, import-outside-toplevel


def cloud_service_create(cmd, resource_group_name, cloud_service_name, location=None, tags=None,
                         package_url=None, configuration=None, configuration_url=None, start_cloud_service=None,
                         upgrade_mode=None, extensions=None, load_balancer_configurations=None, id_=None,
                         secrets=None, roles=None, no_wait=False):
    from azext_cloudservice._utils import (
        as_list, convert_extensions, convert_lbs, convert_roles, convert_secrets, drop_none,
        parse_lbs, parse_roles, parse_secrets)
    from azext_cloudservice.operations.cloud_service import CloudServiceCreate

    roles = parse_roles(roles)
    lbs = parse_lbs(load_balancer_configurations, cmd, resource_group_name)
    secrets = parse_secrets(secrets, cmd, resource_group_name)
    extensions = as_list(extensions, '--extensions')

    command_args = drop_none({
        'resource_group': resource_group_name,
        'cloud_service_name': cloud_service_name,
        'location': location,
        'tags': tags,
        'package_url': package_url,
        'configuration': configuration,
        'configuration_url': configuration_url,
        'start_cloud_service': start_cloud_service,
        'upgrade_mode': upgrade_mode,
        'roles': convert_roles(roles),
        'load_balancer_configurations': convert_lbs(lbs),
        'secrets': convert_secrets(secrets),
        'swappable_cloud_service': {'id': id_} if id_ else None,
        'no_wait': no_wait,
    })
    if extensions:
        command_args['extensions'], command_args['extension_raw_properties'] = convert_extensions(extensions)
    return CloudServiceCreate(cli_ctx=cmd.cli_ctx)(command_args=command_args)
