# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
import json


def create_attestation(cmd, client,
                       resource_group,
                       name,
                       attestation_policy=None,
                       policy_signing_certificates=None):
    return client.create(resource_group_name=resource_group, provider_name=name, attestation_policy=attestation_policy, policy_signing_certificates=policy_signing_certificates)


def update_attestation(cmd, client,
                       resource_group,
                       name,
                       attestation_policy=None,
                       policy_signing_certificates=None):
    return client.create(resource_group_name=resource_group, provider_name=name, creation_params=body)


def delete_attestation(cmd, client,
                       resource_group,
                       name):
    return client.delete(resource_group_name=resource_group, provider_name=name)


def get_attestation(cmd, client,
                    resource_group,
                    name):
    return client.get(resource_group_name=resource_group, provider_name=name)
