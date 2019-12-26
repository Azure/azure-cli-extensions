# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from knack.util import CLIError


def create_imagebuilder(cmd, client,
                        resource_group,
                        image_template_name,
                        location,
                        source_type,
                        distribute_type,
                        tags=None,
                        customize=None,
                        build_timeout_in_minutes=None,
                        vm_size=None,
                        _type=None,
                        user_assigned_identities=None,
                        source_image=None,
                        source_uri=None,
                        source_checksum=None,
                        source_urn=None,
                        distribute_location=None,
                        distribute_image=None,
                        artifact_tag=None,
                        run_output_name=None):

    if source_type == 'PlatformImage':
        if not source_urn:
            raise CLIError('usage error: Please provide --source-urn')

    if distribute_type == 'VHD':
        if distribute_location or distribute_image:
            raise CLIError('usage error: Do not provide --distribute-location or --distribute-image for VHD')
    elif distribute_type in ['ManagedImage', 'SharedImage']:
        if not distribute_location or not distribute_image:
            raise CLIError('usage error: Please provide --distribute-location and --distribute-image')

    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['customize'] = customize

    # source
    if source_type == 'PlatformImage':
        terms = source_urn.split(':')
        if len(terms) != 4:
            raise CLIError('usage error: URN format error')
        source = {
            "type": source_type,
            "publisher": terms[0],
            "offer": terms[1],
            "sku": terms[2],
            "version": terms[3]
        }
        body['source'] = source
    else:
        raise CLIError('usage error: Do not support this source type now')

    # distribute
    if not run_output_name:
        run_output_name = 'runoutput_' + image_template_name
    distribute = {
        "type": distribute_type,
        "runOutputName": run_output_name
    }
    if distribute_type == 'ManagedImage':
        distribute["imageId"] = distribute_image
        if len(distribute_location) != 1:
            raise CLIError('usage error: Only one location allowed')
        distribute["location"] = distribute_location[0]
    elif distribute_type == 'SharedImage':
        distribute["galleryImageId"] = distribute_image
        distribute["replicationRegions"] = distribute_location
    body['distribute'] = [distribute]

    body['build_timeout_in_minutes'] = build_timeout_in_minutes  # number
    body.setdefault('vm_profile', {})['vm_size'] = vm_size  # str
    body.setdefault('identity', {})['type'] = _type  # str
    body.setdefault('identity', {})['user_assigned_identities'] = user_assigned_identities  # dictionary
    return client.create_or_update(resource_group_name=resource_group, image_template_name=image_template_name, parameters=body)


def update_imagebuilder(cmd, client,
                        resource_group,
                        image_template_name,
                        location=None,
                        tags=None,
                        customize=None,
                        distribute=None,
                        build_timeout_in_minutes=None,
                        vm_profile_vm_size=None,
                        _type=None,
                        user_assigned_identities=None):
    body = client.get(resource_group_name=resource_group, image_template_name=image_template_name).as_dict()
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if customize is not None:
        body['customize'] = customize
    if distribute is not None:
        body['distribute'] = distribute
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
