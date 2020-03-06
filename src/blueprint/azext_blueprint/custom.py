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
                                    scope=None):
    from ._client_factory import cf_artifacts

    artifact_client = cf_artifacts(cmd.cli_ctx)
    body = {}
    blueprint_path = os.path.join(os.path.expanduser(input_path), 'blueprint.json')

    with open(blueprint_path) as blueprint_file:
        blueprint = json.load(blueprint_file)
        if 'properties' not in blueprint:
            raise CLIError("blueprint.json does not contain 'properties' field")
        blueprint_properties = blueprint['properties']
        if 'displayName' in blueprint_properties:
            body['display_name'] = blueprint_properties['displayName']  # str
        if 'description' in blueprint_properties:
            body['description'] = blueprint_properties['description']  # str
        if 'targetScope' in blueprint_properties:
            body['target_scope'] = blueprint_properties['targetScope']  # str
        else:
            body['target_scope'] = 'subscription'
        if 'parameters' in blueprint_properties:
            body['parameters'] = blueprint_properties[
                'parameters']  # dictionary
        if 'resourceGroups' in blueprint_properties:
            body['resource_groups'] = blueprint_properties[
                'resourceGroups']  # dictionary
        blueprint_response = client.create_or_update(
            scope=scope, blueprint_name=blueprint_name, blueprint=body)

    # delete old artifacts
    artifacts = artifact_client.list(scope=scope, blueprint_name=blueprint_name)
    for artifact in artifacts:
        artifact_client.delete(scope=scope,
                               blueprint_name=blueprint_name,
                               artifact_name=artifact.name)

    for filename in os.listdir(os.path.join(os.path.expanduser(input_path), 'artifacts')):
        artifact_name = filename.split('.')[0]
        filepath = os.path.join(os.path.expanduser(input_path), 'artifacts', filename)
        with open(filepath) as artifact_file:
            artifact = json.load(artifact_file)
            artifact_client.create_or_update(scope=scope,
                                             blueprint_name=blueprint_name,
                                             artifact_name=artifact_name,
                                             artifact=artifact)

    return blueprint_response


def create_blueprint(cmd,
                     client,
                     blueprint_name,
                     management_group=None,
                     scope=None,
                     target_scope='subscription',
                     display_name=None,
                     description=None,
                     parameters=None):
    body = {}
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['target_scope'] = target_scope  # str
    body['parameters'] = json.loads(
        parameters) if parameters is not None else {}  # dictionary

    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   blueprint=body)


def update_blueprint(cmd,
                     client,
                     blueprint_name,
                     management_group=None,
                     scope=None,
                     description=None,
                     parameters=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    if description is not None:
        body['description'] = description  # str
    if parameters is not None:
        body['parameters'] = json.loads(parameters)  # dictionary
    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   blueprint=body)


def delete_blueprint(cmd, client, blueprint_name, management_group=None, scope=None):
    return client.delete(scope=scope, blueprint_name=blueprint_name)


def get_blueprint(cmd, client, blueprint_name, management_group=None, scope=None):
    return client.get(scope=scope, blueprint_name=blueprint_name)


def list_blueprint(cmd, client, management_group=None, scope=None):
    return client.list(scope=scope)


def delete_blueprint_artifact(cmd, client, blueprint_name, artifact_name,
                              management_group=None, scope=None):
    return client.delete(scope=scope,
                         blueprint_name=blueprint_name,
                         artifact_name=artifact_name)


def get_blueprint_artifact(cmd, client, blueprint_name, artifact_name, management_group=None, scope=None):
    return client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      artifact_name=artifact_name)


def list_blueprint_artifact(cmd, client, blueprint_name, management_group=None, scope=None):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def add_blueprint_resource_group(cmd,
                                 client,
                                 blueprint_name,
                                 management_group=None,
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
                                    scope=None,
                                    rg_name=None,
                                    rg_location=None,
                                    display_name=None,
                                    description=None,
                                    depends_on=None,
                                    tags=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    if artifact_name not in body.setdefault('resource_groups', {}):
        raise CLIError('The specified artifact name can not be found.')
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
        resource_group['depends_on'] = depends_on
    if tags is not None:
        resource_group['tags'] = tags

    rgs = client.create_or_update(scope=scope,
                                  blueprint_name=blueprint_name,
                                  blueprint=body).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


# todo test
def remove_blueprint_resource_group(cmd, client, blueprint_name,
                                    artifact_name, management_group=None, scope=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    if artifact_name not in body.setdefault('resource_groups', {}):
        raise CLIError('The specified artifact name can not be found.')
    deleted_rg = body['resource_groups'][artifact_name]
    del body['resource_groups'][artifact_name]
    client.create_or_update(scope=scope,
                            blueprint_name=blueprint_name,
                            blueprint=body)
    return deleted_rg


def get_blueprint_resource_group(cmd, client, blueprint_name,
                                 artifact_name, management_group=None, scope=None):
    rgs = client.get(scope=scope,
                     blueprint_name=blueprint_name).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


def list_blueprint_resource_group(cmd, client, blueprint_name, management_group=None, scope=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name)
    return body.resource_groups


def create_blueprint_artifact_policy(cmd,
                                     client,
                                     blueprint_name,
                                     policy_definition_id,
                                     artifact_name,
                                     management_group=None,
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
        'parameters': json.loads(parameters) if parameters is not None else {},
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
        body['parameters'] = json.loads(parameters)
    if display_name is not None:
        body['display_name'] = display_name
    if resource_group_art is not None:
        body['resource_group'] = resource_group_art
    if description is not None:
        body['description'] = description
    if depends_on is not None:
        body['depends_on'] = depends_on

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
                                   scope=None,
                                   display_name=None,
                                   resource_group_art=None,
                                   description=None,
                                   depends_on=None):
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
        body['depends_on'] = depends_on

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
                                       scope=None,
                                       parameters=None,
                                       display_name=None,
                                       resource_group_art=None,
                                       description=None,
                                       depends_on=None):
    body = {
        'display_name': display_name,
        'template': json.loads(template),
        'kind': 'template',
        'description': description,
        'depends_on': depends_on,
        'parameters': json.loads(parameters) if parameters is not None else {},
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
        body['template'] = json.loads(template)
    if parameters is not None:
        body['parameters'] = json.loads(parameters)
    if display_name is not None:
        body['display_name'] = display_name
    if resource_group_art is not None:
        body['resource_group'] = resource_group_art
    if description is not None:
        body['description'] = description
    if depends_on is not None:
        body['depends_on'] = depends_on

    return client.create_or_update(scope=scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def publish_blueprint(cmd,
                      client,
                      blueprint_name,
                      version_id,
                      management_group=None,
                      scope=None,
                      change_notes=None):
    body = {}
    body['change_notes'] = change_notes  # str
    return client.create(scope=scope,
                         blueprint_name=blueprint_name,
                         version_id=version_id,
                         published_blueprint=body)


def delete_blueprint_version(cmd, client, blueprint_name, version_id, management_group=None, scope=None):
    return client.delete(scope=scope,
                         blueprint_name=blueprint_name,
                         version_id=version_id)


def get_blueprint_version(cmd, client, blueprint_name, version_id, management_group=None, scope=None):
    return client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      version_id=version_id)


def list_blueprint_version(cmd, client, blueprint_name, management_group=None, scope=None):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def get_blueprint_version_artifact(cmd, client, blueprint_name,
                                   version_id, artifact_name, management_group=None, scope=None):
    return client.get(scope=scope,
                      blueprint_name=blueprint_name,
                      version_id=version_id,
                      artifact_name=artifact_name)


def list_blueprint_version_artifact(cmd, client, blueprint_name,
                                    version_id, management_group=None, scope=None):
    return client.list(scope=scope,
                       blueprint_name=blueprint_name,
                       version_id=version_id)


def create_blueprint_assignment(cmd,
                                client,
                                assignment_name,
                                identity_type,
                                management_group=None,
                                scope=None,
                                location=None,
                                resource_groups=None,
                                identity_principal_id=None,
                                identity_tenant_id=None,
                                identity_user_assigned_identities=None,
                                display_name=None,
                                description=None,
                                blueprint_id=None,
                                locks_mode=None,
                                locks_excluded_principals=None,
                                parameters=None):
    body = {}
    body['location'] = location  # str
    body.setdefault('identity', {})['type'] = identity_type  # str
    body.setdefault('identity',
                    {})['principal_id'] = identity_principal_id  # str
    body.setdefault('identity', {})['tenant_id'] = identity_tenant_id  # str
    body.setdefault(
        'identity', {}
    )['user_assigned_identities'] = identity_user_assigned_identities  # dictionary
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['blueprint_id'] = blueprint_id  # str
    body['parameters'] = json.loads(
        parameters) if parameters is not None else {}  # dictionary
    body['resource_groups'] = json.loads(
        resource_groups) if resource_groups is not None else {}  # dictionary
    body.setdefault('locks', {})['mode'] = locks_mode  # str
    body.setdefault(
        'locks', {}
    )['excluded_principals'] = None if locks_excluded_principals is None else locks_excluded_principals.split(
        ',')
    return client.create_or_update(scope=scope,
                                   assignment_name=assignment_name,
                                   assignment=body)


def update_blueprint_assignment(cmd,
                                client,
                                assignment_name,
                                management_group=None,
                                scope=None,
                                location=None,
                                identity_type=None,
                                identity_principal_id=None,
                                identity_tenant_id=None,
                                identity_user_assigned_identities=None,
                                display_name=None,
                                description=None,
                                blueprint_id=None,
                                parameters=None,
                                resource_groups=None,
                                locks_mode=None,
                                locks_excluded_principals=None):
    body = client.get(scope=scope, assignment_name=assignment_name).as_dict()
    if location is not None:
        body['location'] = location  # str
    if identity_type is not None:
        body.setdefault('identity', {})['type'] = identity_type  # str
    if identity_principal_id is not None:
        body.setdefault('identity',
                        {})['principal_id'] = identity_principal_id  # str
    if identity_tenant_id is not None:
        body.setdefault('identity',
                        {})['tenant_id'] = identity_tenant_id  # str
    if identity_user_assigned_identities is not None:
        body.setdefault(
            'identity', {}
        )['user_assigned_identities'] = identity_user_assigned_identities  # dictionary
    if display_name is not None:
        body['display_name'] = display_name  # str
    if description is not None:
        body['description'] = description  # str
    if blueprint_id is not None:
        body['blueprint_id'] = blueprint_id  # str
    if parameters is not None:
        body['parameters'] = json.loads(parameters)  # dictionary
    if resource_groups is not None:
        body['resource_groups'] = json.loads(resource_groups)  # dictionary
    if locks_mode is not None:
        body.setdefault('locks', {})['mode'] = locks_mode  # str
    if locks_excluded_principals is not None:
        body.setdefault(
            'locks', {}
        )['excluded_principals'] = None if locks_excluded_principals is None else locks_excluded_principals.split(
            ',')
    return client.create_or_update(scope=scope,
                                   assignment_name=assignment_name,
                                   assignment=body)


def delete_blueprint_assignment(cmd, client, assignment_name, management_group=None, scope=None):
    return client.delete(scope=scope, assignment_name=assignment_name)


def get_blueprint_assignment(cmd, client, assignment_name, management_group=None, scope=None):
    return client.get(scope=scope, assignment_name=assignment_name)


def list_blueprint_assignment(cmd, client, management_group=None, scope=None):
    return client.list(scope=scope)


def wait_for_blueprint_assignment(cmd, client, assignment_name, management_group=None, scope=None):
    client.wait(scope=scope, assignment_name=assignment_name)


def who_is_blueprint_blueprint_assignment(cmd, client, assignment_name, management_group=None, scope=None):
    return client.who_is_blueprint(scope=scope,
                                   assignment_name=assignment_name)
