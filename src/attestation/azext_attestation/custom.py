# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def list_attestation_operation(cmd, client):
    return client.list()


def create_attestation_attestation_provider(cmd, client,
                                            resource_group,
                                            name,
                                            attestation_policy=None,
                                            policy_signing_certificates=None):
    return client.create(resource_group_name=resource_group, provider_name=name, attestation_policy=attestation_policy, policy_signing_certificates=policy_signing_certificates)


def update_attestation_attestation_provider(cmd, client,
                                            resource_group,
                                            name,
                                            attestation_policy=None,
                                            policy_signing_certificates=None):
    return client.create(resource_group_name=resource_group, provider_name=name, attestation_policy=attestation_policy, policy_signing_certificates=policy_signing_certificates)


def delete_attestation_attestation_provider(cmd, client,
                                            resource_group,
                                            name):
    return client.delete(resource_group_name=resource_group, provider_name=name)


def get_attestation_attestation_provider(cmd, client,
                                         resource_group,
                                         name):
    return client.get(resource_group_name=resource_group, provider_name=name)


def list_attestation_attestation_provider(cmd, client,
                                          resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()
