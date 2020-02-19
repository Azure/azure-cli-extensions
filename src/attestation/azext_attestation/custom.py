# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def attestation_operations_list(cmd, client):
    return client.list()


def attestation_attestation_providers_list(cmd, client,
                                           resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def attestation_attestation_providers_show(cmd, client,
                                           resource_group_name,
                                           provider_name):
    return client.get(resource_group_name=resource_group_name, provider_name=provider_name)


def attestation_attestation_providers_create(cmd, client,
                                             resource_group_name,
                                             provider_name,
                                             attestation_policy=None,
                                             policy_signing_certificates_keys=None):
    creation_params = {}
    creation_params['attestation_policy'] = attestation_policy  # string
    creation_params.setdefault('policy_signing_certificates', {})['keys'] = None if policy_signing_certificates_keys is None else policy_signing_certificates_keys
    return client.create(resource_group_name=resource_group_name, provider_name=provider_name, creation_params=creation_params)


def attestation_attestation_providers_delete(cmd, client,
                                             resource_group_name,
                                             provider_name):
    return client.delete(resource_group_name=resource_group_name, provider_name=provider_name)
