# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)
from azext_attestation.actions import (
    AddKeys
)


def load_arguments(self, _):

    with self.argument_context('attestation operations list') as c:
        pass

    with self.argument_context('attestation attestation-providers list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('attestation attestation-providers show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('provider_name', id_part=None, help='Name of the attestation service instance')

    with self.argument_context('attestation attestation-providers create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('provider_name', id_part=None, help='Name of the attestation service instance')
        c.argument('attestation_policy', id_part=None, help='Name of attestation policy.')
        c.argument('policy_signing_certificates_keys', id_part=None, help='The value of the "keys" parameter is an array of JWK values.  By default, the order of the JWK values within the array does not imply an order of preference among them, although applications of JWK Sets can choose to assign a meaning to the order for their purposes, if desired.', action=AddKeys, nargs='+')

    with self.argument_context('attestation attestation-providers delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('provider_name', id_part=None, help='Name of the attestation service instance')
