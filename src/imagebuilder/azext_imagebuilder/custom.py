# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_imagebuilder(cmd, client,
                        resource_group,
                        image_template_name,
                        location,
                        distribute_run_output_name,
                        tags=None,
                        customize_name=None,
                        distribute_artifact_tags=None,
                        build_timeout_in_minutes=None,
                        vm_profile_vm_size=None,
                        _type=None,
                        user_assigned_identities=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body.setdefault('customize', {})['name'] = customize_name
    body.setdefault('distribute', {})['run_output_name'] = distribute_run_output_name
    body.setdefault('distribute', {})['artifact_tags'] = distribute_artifact_tags
    body['build_timeout_in_minutes'] = build_timeout_in_minutes  # number
    body.setdefault('vm_profile', {})['vm_size'] = vm_profile_vm_size  # str
    body.setdefault('identity', {})['type'] = _type  # str
    body.setdefault('identity', {})['user_assigned_identities'] = user_assigned_identities  # dictionary
    return client.create_or_update(resource_group_name=resource_group, image_template_name=image_template_name, parameters=body)


def update_imagebuilder(cmd, client,
                        resource_group,
                        image_template_name,
                        location=None,
                        tags=None,
                        customize_name=None,
                        distribute_run_output_name=None,
                        distribute_artifact_tags=None,
                        build_timeout_in_minutes=None,
                        vm_profile_vm_size=None,
                        _type=None,
                        user_assigned_identities=None):
    body = client.get(resource_group_name=resource_group, image_template_name=image_template_name).as_dict()
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if customize_name is not None:
        body.setdefault('customize', {})['name'] = customize_name
    if distribute_run_output_name is not None:
        body.setdefault('distribute', {})['run_output_name'] = distribute_run_output_name
    if distribute_artifact_tags is not None:
        body.setdefault('distribute', {})['artifact_tags'] = distribute_artifact_tags
    if build_timeout_in_minutes is not None:
        body['build_timeout_in_minutes'] = build_timeout_in_minutes  # number
    if vm_profile_vm_size is not None:
        body.setdefault('vm_profile', {})['vm_size'] = vm_profile_vm_size  # str
    if _type is not None:
        body.setdefault('identity', {})['type'] = _type  # str
    if user_assigned_identities is not None:
        body.setdefault('identity', {})['user_assigned_identities'] = user_assigned_identities  # dictionary
    return client.create_or_update(resource_group_name=resource_group, image_template_name=image_template_name, parameters=body)


def delete_imagebuilder(cmd, client,
                        resource_group,
                        image_template_name):
    return client.delete(resource_group_name=resource_group, image_template_name=image_template_name)


def get_imagebuilder(cmd, client,
                     resource_group,
                     image_template_name):
    return client.get(resource_group_name=resource_group, image_template_name=image_template_name)


def list_imagebuilder(cmd, client,
                      resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()


def run_imagebuilder(cmd, client,
                     resource_group,
                     image_template_name):
    return client.run(resource_group_name=resource_group, image_template_name=image_template_name)


def list_run_outputs_imagebuilder(cmd, client,
                                  resource_group,
                                  image_template_name):
    return client.list_run_outputs(resource_group_name=resource_group, image_template_name=image_template_name)


def get_run_output_imagebuilder(cmd, client,
                                resource_group,
                                image_template_name,
                                name):
    return client.get_run_output(resource_group_name=resource_group, image_template_name=image_template_name, run_output_name=name)


def list_imagebuilder(cmd, client):
    return client.list()
