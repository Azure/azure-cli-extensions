# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)


def load_arguments(self, _):
    with self.argument_context('healthcare create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the service instance.')
        c.argument('kind', arg_type=get_enum_type(['fhir', 'fhir-Stu3', 'fhir-R4']), id_part=None, help='The kind of the service. Valid values are: fhir, fhir-Stu3 and fhir-R4.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('etag', id_part=None, help='An etag associated with the resource, used for optimistic concurrency when editing it.')
        c.argument('access_policies_object_id', id_part=None, help='An object ID that is allowed access to the FHIR service.')
        c.argument('cosmos_db_offer_throughput', id_part=None, help='The provisioned throughput for the backing database.')
        c.argument('authentication_authority', id_part=None, help='The authority url for the service')
        c.argument('authentication_audience', id_part=None, help='The audience url for the service')
        c.argument('authentication_smart_proxy_enabled', arg_type=get_three_state_flag(), id_part=None, help='If the SMART on FHIR proxy is enabled')
        c.argument('cors_origins', id_part=None, help='The origins to be allowed via CORS.')
        c.argument('cors_headers', id_part=None, help='The headers to be allowed via CORS.')
        c.argument('cors_methods', id_part=None, help='The methods to be allowed via CORS.')
        c.argument('cors_max_age', id_part=None, help='The max age to be allowed via CORS.')
        c.argument('cors_allow_credentials', arg_type=get_three_state_flag(), id_part=None, help='If credentials are allowed via CORS.')

    with self.argument_context('healthcare update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the service instance.')
        c.argument('kind', arg_type=get_enum_type(['fhir', 'fhir-Stu3', 'fhir-R4']), id_part=None, help='The kind of the service. Valid values are: fhir, fhir-Stu3 and fhir-R4.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('etag', id_part=None, help='An etag associated with the resource, used for optimistic concurrency when editing it.')
        c.argument('access_policies_object_id', id_part=None, help='An object ID that is allowed access to the FHIR service.')
        c.argument('cosmos_db_offer_throughput', id_part=None, help='The provisioned throughput for the backing database.')
        c.argument('authentication_authority', id_part=None, help='The authority url for the service')
        c.argument('authentication_audience', id_part=None, help='The audience url for the service')
        c.argument('authentication_smart_proxy_enabled', arg_type=get_three_state_flag(), id_part=None, help='If the SMART on FHIR proxy is enabled')
        c.argument('cors_origins', id_part=None, help='The origins to be allowed via CORS.')
        c.argument('cors_headers', id_part=None, help='The headers to be allowed via CORS.')
        c.argument('cors_methods', id_part=None, help='The methods to be allowed via CORS.')
        c.argument('cors_max_age', id_part=None, help='The max age to be allowed via CORS.')
        c.argument('cors_allow_credentials', arg_type=get_three_state_flag(), id_part=None, help='If credentials are allowed via CORS.')

    with self.argument_context('healthcare delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the service instance.')

    with self.argument_context('healthcare list') as c:
        c.argument('resource_group', resource_group_name_type)

    with self.argument_context('healthcare show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the service instance.')
