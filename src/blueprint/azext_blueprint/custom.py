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
import os
from knack.util import CLIError


def import_blueprint_with_artifacts(cmd,
                                    client,
                                    blueprint_name,
                                    input_path,
                                    management_group=None,
                                    subscription=None,
                                    scope=None):
    from ._client_factory import cf_artifacts

    artifact_client = cf_artifacts(cmd.cli_ctx)
    body = {}
    blueprint_path = os.path.join(input_path, 'blueprint.json')
    art_dict = {}

    try:
        with open(blueprint_path) as blueprint_file:
            try:
                blueprint = json.load(blueprint_file)
            except json.decoder.JSONDecodeError as ex:
                raise CLIError('JSON decode error for {}: {}'.format(blueprint_path, str(ex)))
            if 'properties' not in blueprint:
                raise CLIError("blueprint.json does not contain the 'properties' field")
            blueprint_properties = blueprint['properties']
            if 'displayName' in blueprint_properties:
                body['display_name'] = blueprint_properties['displayName']  # str
            if 'description' in blueprint_properties:
                body['description'] = blueprint_properties['description']  # str
            body['target_scope'] = blueprint_properties.get('targetScope', 'subscription')  # str
            if 'parameters' in blueprint_properties:
                body['parameters'] = blueprint_properties[
                    'parameters']  # dictionary
            if 'resourceGroups' in blueprint_properties:
                body['resource_groups'] = blueprint_properties['resourceGroups']  # dictionary

        for filename in os.listdir(os.path.join(input_path, 'artifacts')):
            artifact_name = filename.split('.')[0]
            filepath = os.path.join(input_path, 'artifacts', filename)
            with open(filepath) as artifact_file:
                try:
                    artifact = json.load(artifact_file)
                    art_dict[artifact_name] = artifact
                except json.decoder.JSONDecodeError as ex:
                    raise CLIError('JSON decode error for {}: {}'.format(filepath, str(ex)))
    except FileNotFoundError as ex:
        raise CLIError('File not Found: {}'.format(str(ex)))

    # Only import when all files have no errors
    blueprint_response = client.create_or_update(scope=scope, blueprint_name=blueprint_name, blueprint=body)
    # delete old artifacts
    artifacts = artifact_client.list(scope=scope, blueprint_name=blueprint_name)
    for artifact in artifacts:
        artifact_client.delete(scope=scope,
                               blueprint_name=blueprint_name,
                               artifact_name=artifact.name)
    # create new artifacts
    for artifact_name, artifact in art_dict.items():
        artifact_client.create_or_update(scope=scope,
                                         blueprint_name=blueprint_name,
                                         artifact_name=artifact_name,
                                         artifact=artifact)

    return blueprint_response


def create_blueprint(cmd,
                     client,
                     blueprint_name,
                     management_group=None,
                     subscription=None,
                     scope=None,
                     target_scope=None,
                     display_name=None,
                     description=None,
                     parameters=None):
    body = {}
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['target_scope'] = target_scope  # str
    body['parameters'] = parameters if parameters is not None else {}  # dictionary

    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   blueprint=body)


def update_blueprint(cmd,
                     instance,
                     blueprint_name,
                     management_group=None,
                     subscription=None,
                     scope=None,
                     description=None,
                     parameters=None):
    if description is not None:
        instance.description = description  # str
    if parameters is not None:
        instance.parameters = parameters  # dictionary
    return instance


def delete_blueprint(cmd, client, blueprint_name, management_group=None, subscription=None, scope=None):
    return client.delete(scope=scope, blueprint_name=blueprint_name)


def get_blueprint(cmd, client, blueprint_name, management_group=None, subscription=None, scope=None):
    return client.get(scope=scope, blueprint_name=blueprint_name)


def list_blueprint(cmd, client, management_group=None, subscription=None, scope=None, **kwargs):
    return client.list(scope=scope)


def delete_blueprint_artifact(cmd, client, blueprint_name, artifact_name,
                              management_group=None, subscription=None, scope=None):
    return client.delete(scope=scope,
                         blueprint_name=blueprint_name,
                         artifact_name=artifact_name)


def get_blueprint_artifact(cmd, client, blueprint_name, artifact_name, management_group=None, subscription=None, scope=None):
    return client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      artifact_name=artifact_name)


def list_blueprint_artifact(cmd, client, blueprint_name, management_group=None, subscription=None, scope=None):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def add_blueprint_resource_group(cmd,
                                 client,
                                 blueprint_name,
                                 management_group=None,
                                 subscription=None,
                                 scope=None,
                                 artifact_name=None,
                                 display_name=None,
                                 rg_name=None,
                                 rg_location=None,
                                 description=None,
                                 depends_on=None,
                                 tags=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    rg_key = artifact_name
    body.setdefault('resource_groups', {})
    if artifact_name is None:
        rg_len = len(body['resource_groups'])
        for i in range(rg_len + 1):
            posix = '' if i == 0 else i + 1
            rg_key = "ResourceGroup{}".format(posix)
            if rg_key not in body['resource_groups']:
                break
    elif artifact_name in body['resource_groups']:
        raise CLIError(
            'A resource group artifact with the same name already exists.')

    resource_group = {
        "name": rg_name,
        "location": rg_location,
        "display_name": display_name,
        "description": description,
        "depends_on": depends_on,
        "tags": tags
    }
    body.setdefault('resource_groups', {})[rg_key] = resource_group
    rgs = client.create_or_update(scope=scope,
                                  blueprint_name=blueprint_name,
                                  blueprint=body).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


def update_blueprint_resource_group(cmd,
                                    client,
                                    blueprint_name,
                                    artifact_name,
                                    management_group=None,
                                    subscription=None,
                                    scope=None,
                                    rg_name=None,
                                    rg_location=None,
                                    display_name=None,
                                    description=None,
                                    depends_on=None,
                                    tags=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    if artifact_name not in body.setdefault('resource_groups', {}):
        raise CLIError('The specified artifact name: {} can not be found.'.format(artifact_name))
    resource_group = body['resource_groups'][artifact_name]
    if rg_name is not None:
        resource_group['name'] = rg_name
    if rg_location is not None:
        resource_group['location'] = rg_location
    if display_name is not None:
        resource_group['display_name'] = display_name
    if description is not None:
        resource_group['description'] = description  # str
    if depends_on is not None:
        resource_group['depends_on'] = _process_depends_on_for_update(depends_on)
    if tags is not None:
        resource_group['tags'] = tags

    rgs = client.create_or_update(scope=scope,
                                  blueprint_name=blueprint_name,
                                  blueprint=body).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


# todo test
def remove_blueprint_resource_group(cmd, client, blueprint_name,
                                    artifact_name, management_group=None, subscription=None, scope=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    if artifact_name not in body.setdefault('resource_groups', {}):
        raise CLIError('The specified artifact name: {} can not be found.'.format(artifact_name))
    deleted_rg = body['resource_groups'][artifact_name]
    del body['resource_groups'][artifact_name]
    client.create_or_update(scope=scope,
                            blueprint_name=blueprint_name,
                            blueprint=body)
    return deleted_rg


def get_blueprint_resource_group(cmd, client, blueprint_name,
                                 artifact_name, management_group=None, subscription=None, scope=None):
    rgs = client.get(scope=scope,
                     blueprint_name=blueprint_name).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


def list_blueprint_resource_group(cmd, client, blueprint_name, management_group=None, subscription=None, scope=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name)
    return body.resource_groups


def create_blueprint_artifact_policy(cmd,
                                     client,
                                     blueprint_name,
                                     policy_definition_id,
                                     artifact_name,
                                     management_group=None,
                                     subscription=None,
                                     scope=None,
                                     parameters=None,
                                     display_name=None,
                                     resource_group_art=None,
                                     description=None,
                                     depends_on=None):
    body = {
        'display_name': display_name,
        'policy_definition_id': policy_definition_id,
        'kind': 'policyAssignment',
        'description': description,
        'depends_on': depends_on,
        'parameters': parameters,
        'resource_group': resource_group_art
    }
    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def update_blueprint_artifact_policy(cmd,
                                     client,
                                     blueprint_name,
                                     artifact_name,
                                     management_group=None,
                                     subscription=None,
                                     scope=None,
                                     parameters=None,
                                     display_name=None,
                                     resource_group_art=None,
                                     description=None,
                                     depends_on=None):
    body = client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      artifact_name=artifact_name).as_dict()
    if parameters is not None:
        body['parameters'] = parameters
    if display_name is not None:
        body['display_name'] = display_name
    if resource_group_art is not None:
        body['resource_group'] = resource_group_art
    if description is not None:
        body['description'] = description
    if depends_on is not None:
        body['depends_on'] = _process_depends_on_for_update(depends_on)

    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def create_blueprint_artifact_role(cmd,
                                   client,
                                   blueprint_name,
                                   role_definition_id,
                                   principal_ids,
                                   artifact_name,
                                   management_group=None,
                                   subscription=None,
                                   scope=None,
                                   display_name=None,
                                   resource_group_art=None,
                                   description=None,
                                   depends_on=None):
    # princial_ids can be a parameter reference that resolves to a principal ID string
    # or a list of real principal IDs
    if len(principal_ids) == 1 and principal_ids[0].startswith('[parameters'):
        principal_ids = principal_ids[0]
    body = {
        'display_name': display_name,
        'role_definition_id': role_definition_id,
        'kind': 'roleAssignment',
        'description': description,
        'depends_on': depends_on,
        'resource_group': resource_group_art,
        'principal_ids': principal_ids
    }
    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def update_blueprint_artifact_role(cmd,
                                   client,
                                   blueprint_name,
                                   artifact_name,
                                   management_group=None,
                                   subscription=None,
                                   scope=None,
                                   display_name=None,
                                   resource_group_art=None,
                                   description=None,
                                   depends_on=None):
    body = client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      artifact_name=artifact_name).as_dict()

    if display_name is not None:
        body['display_name'] = display_name
    if resource_group_art is not None:
        body['resource_group'] = resource_group_art
    if description is not None:
        body['description'] = description
    if depends_on is not None:
        body['depends_on'] = _process_depends_on_for_update(depends_on)

    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def create_blueprint_artifact_template(cmd,
                                       client,
                                       blueprint_name,
                                       template,
                                       artifact_name,
                                       management_group=None,
                                       subscription=None,
                                       scope=None,
                                       parameters=None,
                                       display_name=None,
                                       resource_group_art=None,
                                       description=None,
                                       depends_on=None):
    body = {
        'display_name': display_name,
        'template': template,
        'kind': 'template',
        'description': description,
        'depends_on': depends_on,
        'parameters': parameters,
        'resource_group': resource_group_art
    }
    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def update_blueprint_artifact_template(cmd,
                                       client,
                                       blueprint_name,
                                       artifact_name,
                                       management_group=None,
                                       subscription=None,
                                       scope=None,
                                       template=None,
                                       parameters=None,
                                       display_name=None,
                                       resource_group_art=None,
                                       description=None,
                                       depends_on=None):
    body = client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      artifact_name=artifact_name).as_dict()

    if template is not None:
        body['template'] = template
    if parameters is not None:
        body['parameters'] = parameters
    if display_name is not None:
        body['display_name'] = display_name
    if resource_group_art is not None:
        body['resource_group'] = resource_group_art
    if description is not None:
        body['description'] = description
    if depends_on is not None:
        body['depends_on'] = _process_depends_on_for_update(depends_on)

    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def publish_blueprint(cmd,
                      client,
                      blueprint_name,
                      version_id,
                      management_group=None,
                      subscription=None,
                      scope=None,
                      change_notes=None):
    body = {}
    body['change_notes'] = change_notes  # str
    body['blueprint_name'] = blueprint_name
    return client.create(scope=scope,
                         blueprint_name=blueprint_name,
                         version_id=version_id,
                         published_blueprint=body)


def delete_blueprint_version(cmd, client, blueprint_name, version_id, management_group=None, subscription=None, scope=None):
    return client.delete(scope=scope,
                         blueprint_name=blueprint_name,
                         version_id=version_id)


def get_blueprint_version(cmd, client, blueprint_name, version_id, management_group=None, subscription=None, scope=None):
    return client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      version_id=version_id)


def list_blueprint_version(cmd, client, blueprint_name, management_group=None, subscription=None, scope=None):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def get_blueprint_version_artifact(cmd, client, blueprint_name,
                                   version_id, artifact_name, management_group=None, subscription=None, scope=None):
    return client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      version_id=version_id,
                      artifact_name=artifact_name)


def list_blueprint_version_artifact(cmd, client, blueprint_name,
                                    version_id, management_group=None, subscription=None, scope=None):
    return client.list(scope=scope,
                       blueprint_name=blueprint_name,
                       version_id=version_id)


def resource_group_list_2_dict(resource_groups):
    result = {}
    if resource_groups is not None:
        for rg in resource_groups:
            key = rg['artifact_name']
            del rg['artifact_name']
            result[key] = rg
    return result


def create_blueprint_assignment(cmd,
                                client,
                                assignment_name,
                                identity_type=None,
                                management_group=None,
                                subscription=None,
                                scope=None,
                                location=None,
                                resource_groups=None,
                                user_assigned_identity=None,
                                display_name=None,
                                description=None,
                                blueprint_id=None,
                                locks_mode=None,
                                locks_excluded_principals=None,
                                parameters=None):
    from msrestazure.azure_exceptions import CloudError
    from .vendored_sdks.blueprint.models._blueprint_management_client_enums import ManagedServiceIdentityType
    try:
        result = client.get(scope=scope, assignment_name=assignment_name)
        if result is not None:
            raise CLIError("An assignment with name '{}' in subscription '{}' already exists. Please use 'az blueprint assignment update' to update an existing assignment.".format(assignment_name, scope))
    except CloudError:  # AssignmentNotFound
        pass
    body = {}
    body['location'] = location  # str
    body.setdefault('identity', {})['type'] = identity_type  # str
    if user_assigned_identity is not None:
        body.setdefault(
            'identity', {}
        )['user_assigned_identities'] = {user_assigned_identity: {}}  # dictionary
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['blueprint_id'] = blueprint_id  # str
    body['parameters'] = parameters  # dictionary
    body['resource_groups'] = resource_group_list_2_dict(resource_groups)  # dictionary

    body.setdefault('locks', {})['mode'] = locks_mode  # str
    body.setdefault('locks', {})['excluded_principals'] = locks_excluded_principals

    # Assign owner permission to Blueprint SPN only if assignment is being done using
    # system assigned identity.
    # This is a no-op for user assigned identity.
    if identity_type == ManagedServiceIdentityType.system_assigned.value:
        result = client.who_is_blueprint(scope=scope, assignment_name=assignment_name)
        if result is None:
            raise CLIError("Blueprint service failed to return the SPN for assignment:{}".format(assignment_name))
        spn = result.object_id
        _assign_owner_role_in_target_scope(cmd, scope, spn)
    return client.create_or_update(scope=scope, assignment_name=assignment_name, assignment=body)


def _assign_owner_role_in_target_scope(cmd, role_scope, spn_object_id,):
    from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment
    role_assignments = list_role_assignments(cmd, assignee=spn_object_id, role='Owner', scope=role_scope)
    if not role_assignments:
        create_role_assignment(cmd, role='Owner', assignee_object_id=spn_object_id, scope=role_scope,
                               assignee_principal_type='ServicePrincipal')


def update_blueprint_assignment(cmd,
                                client,
                                assignment_name,
                                management_group=None,
                                subscription=None,
                                scope=None,
                                location=None,
                                identity_type=None,
                                user_assigned_identity=None,
                                display_name=None,
                                description=None,
                                blueprint_id=None,
                                parameters=None,
                                resource_groups=None,
                                locks_mode=None,
                                locks_excluded_principals=None):
    from .vendored_sdks.blueprint.models._blueprint_management_client_enums import ManagedServiceIdentityType

    body = client.get(scope=scope, assignment_name=assignment_name).as_dict()
    if location is not None:
        body['location'] = location  # str
    if identity_type is not None:
        body['identity'] = {}
        body['identity']['type'] = identity_type  # str
    if user_assigned_identity is not None:
        body['identity']['user_assigned_identities'] = {user_assigned_identity: {}}  # dictionary
    elif 'user_assigned_identities' in body['identity']:
        for identity in body['identity']['user_assigned_identities']:
            body['identity']['user_assigned_identities'][identity] = {}  # service only accept empty json of a user-assigned identity in request

    if display_name is not None:
        body['display_name'] = display_name  # str
    if description is not None:
        body['description'] = description  # str
    if blueprint_id is not None:
        body['blueprint_id'] = blueprint_id  # str
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if resource_groups is not None:
        body['resource_groups'] = resource_group_list_2_dict(resource_groups)  # dictionary
    if locks_mode is not None:
        body.setdefault('locks', {})['mode'] = locks_mode  # str
    if locks_excluded_principals is not None:
        body.setdefault('locks', {})['excluded_principals'] = locks_excluded_principals

    # Assign owner permission to Blueprint SPN only if assignment is being done using
    # system assigned identity.
    # This is a no-op for user assigned identity.
    if identity_type == ManagedServiceIdentityType.system_assigned.value:
        result = client.who_is_blueprint(scope=scope, assignment_name=assignment_name)
        if result is None:
            raise CLIError("Blueprint service failed to return the SPN for assignment:{}".format(assignment_name))
        spn = result.object_id
        _assign_owner_role_in_target_scope(cmd, scope, spn)
    return client.create_or_update(scope=scope,
                                   assignment_name=assignment_name,
                                   assignment=body)


def delete_blueprint_assignment(cmd, client, assignment_name, management_group=None, subscription=None, scope=None):
    return client.delete(scope=scope, assignment_name=assignment_name)


def get_blueprint_assignment(cmd, client, assignment_name, management_group=None, subscription=None, scope=None):
    return client.get(scope=scope, assignment_name=assignment_name)


def list_blueprint_assignment(cmd, client, management_group=None, subscription=None, scope=None):
    return client.list(scope=scope)


def wait_for_blueprint_assignment(cmd, client, assignment_name, management_group=None, subscription=None, scope=None):
    client.wait(scope=scope, assignment_name=assignment_name)


def who_is_blueprint_blueprint_assignment(cmd, client, assignment_name, management_group=None, subscription=None, scope=None):
    return client.who_is_blueprint(scope=scope, assignment_name=assignment_name)


def _process_depends_on_for_update(depends_on):
    if not depends_on:  # [] for case: --depends-on
        return None
    if not any(depends_on):  # [''] for case: --depends-on= /--depends-on ""
        return None
    return depends_on
