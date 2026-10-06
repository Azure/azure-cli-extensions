# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_servicegroup.aaz.latest.service_group._create import Create
from azext_servicegroup.aaz.latest.service_group._delete import Delete
from azext_servicegroup.aaz.latest.service_group._show import Show
from azext_servicegroup.aaz.latest.service_group._update import Update
from azext_servicegroup.aaz.latest.service_group._wait import Wait
from azure.cli.core.aaz import AAZFloatType


def test_servicegroup_commands_use_stable_api_version():
    for command in [Create, Delete, Show, Update, Wait]:
        assert command._aaz_info["version"] == "2026-08-01"
        assert command._aaz_info["resources"] == [
            [
                "mgmt-plane",
                "/providers/microsoft.management/servicegroups/{}",
                "2026-08-01",
            ]
        ]


def test_servicegroup_criticality_range():
    for command in [Create, Update]:
        criticality_format = command._build_arguments_schema().attributes.criticality._fmt
        assert criticality_format._minimum == 0
        assert criticality_format._maximum == 4


def test_servicegroup_criticality_response_accepts_float():
    # The GA service returns values such as 1.0 despite criticality being specified as int32.
    response_schemas = [
        Create.ServiceGroupsCreateOrUpdate._build_schema_on_200_201(),
        Show.ServiceGroupsGet._build_schema_on_200(),
        Update.ServiceGroupsUpdate._build_schema_on_200(),
        Wait.ServiceGroupsGet._build_schema_on_200(),
    ]
    for schema in response_schemas:
        assert isinstance(schema.properties.attributes.criticality, AAZFloatType)
