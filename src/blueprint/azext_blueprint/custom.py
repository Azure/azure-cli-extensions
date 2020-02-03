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
from knack.util import CLIError


def create_blueprint(cmd, client,
                     name,
                     scope,
                     display_name=None,
                     description=None,
                     target_scope=None,
                     parameters=None):
    body = {}
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['target_scope'] = target_scope  # str
    body['parameters'] = json.loads(parameters) if parameters is not None else {}  # dictionary
    return client.create_or_update(scope=scope, blueprint_name=name, blueprint=body)


def update_blueprint(cmd, client,
                     name,
                     scope,
                     description=None,
                     parameters=None):
    body = client.get(scope=scope, blueprint_name=name).as_dict()
    if description is not None:
        body['description'] = description  # str
    if parameters is not None:
        body['parameters'] = json.loads(parameters)  # dictionary
    return client.create_or_update(scope=scope, blueprint_name=name, blueprint=body)


def delete_blueprint(cmd, client,
                     name,
                     scope):
    return client.delete(scope=scope, blueprint_name=name)


def get_blueprint(cmd, client,
                  name,
                  scope):
    return client.get(scope=scope, blueprint_name=name)


def list_blueprint(cmd, client,
                   scope):
    return client.list(scope=scope)


def delete_blueprint_artifact(cmd, client,
                              blueprint_name,
                              artifact_name,
                              scope):
    return client.delete(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name)


def get_blueprint_artifact(cmd, client,
                           blueprint_name,
                           artifact_name,
                           scope):
    return client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name)


def list_blueprint_artifact(cmd, client,
                            blueprint_name,
                            scope):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def create_blueprint_resource_group(cmd, client,
                                    blueprint_name,
                                    scope,
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
        raise CLIError('A resource group artifact with the same name already exists.')

    resource_group = {
        "name": rg_name,
        "location": rg_location,
        "display_name": display_name,
        "description": description,
        "depends_on": depends_on,
        "tags": tags
    }
    body.setdefault('resource_groups', {})[rg_key] = resource_group
    rgs = client.create_or_update(scope=scope, blueprint_name=blueprint_name, blueprint=body).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


def update_blueprint_resource_group(cmd, client,
                                    blueprint_name,
                                    scope,
                                    artifact_name,
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

    rgs = client.create_or_update(scope=scope, blueprint_name=blueprint_name, blueprint=body).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


# todo test
def delete_blueprint_resource_group(cmd, client,
                                    blueprint_name,
                                    scope,
                                    artifact_name):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    if artifact_name not in body.setdefault('resource_groups', {}):
        raise CLIError('The specified artifact name can not be found.')
    deleted_rg = body['resource_groups'][artifact_name]
    del body['resource_groups'][artifact_name]
    client.create_or_update(scope=scope, blueprint_name=blueprint_name, blueprint=body)
    return deleted_rg


def get_blueprint_resource_group(cmd, client,
                                 blueprint_name,
                                 scope,
                                 artifact_name):
    rgs = client.get(scope=scope, blueprint_name=blueprint_name).resource_groups
    return {k: v for k, v in rgs.items() if k == artifact_name}


def list_blueprint_resource_group(cmd, client,
                                  blueprint_name,
                                  scope):
    body = client.get(scope=scope, blueprint_name=blueprint_name)
    return body.resource_groups


def create_blueprint_artifact_policy(cmd, client,
                                     blueprint_name,
                                     scope,
                                     policy_definition_id,
                                     artifact_name,
                                     parameters=None,
                                     display_name=None,
                                     resource_group_art=None,
                                     description=None,
                                     depends_on=None):
    body = {'display_name': display_name,
            'policy_definition_id': policy_definition_id,
            'kind': 'policyAssignment',
            'description': description,
            'depends_on': depends_on,
            'parameters': json.loads(parameters) if parameters is not None else {},
            'resource_group': resource_group_art
            }
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name, artifact=body)


def update_blueprint_artifact_policy(cmd, client,
                                     blueprint_name,
                                     scope,
                                     artifact_name,
                                     parameters=None,
                                     display_name=None,
                                     resource_group_art=None,
                                     description=None,
                                     depends_on=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name).as_dict()
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

    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name, artifact=body)


def create_blueprint_artifact_role(cmd, client,
                                   blueprint_name,
                                   scope,
                                   role_definition_id,
                                   principal_ids,
                                   artifact_name,
                                   display_name=None,
                                   resource_group_art=None,
                                   description=None,
                                   depends_on=None):

    body = {'display_name': display_name,
            'role_definition_id': role_definition_id,
            'kind': 'roleAssignment',
            'description': description,
            'depends_on': depends_on,
            'resource_group': resource_group_art,
            'principal_ids': principal_ids
            }
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name, artifact=body)


def update_blueprint_artifact_role(cmd, client,
                                   blueprint_name,
                                   scope,
                                   artifact_name,
                                   display_name=None,
                                   resource_group_art=None,
                                   description=None,
                                   depends_on=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name).as_dict()

    if display_name is not None:
        body['display_name'] = display_name
    if resource_group_art is not None:
        body['resource_group'] = resource_group_art
    if description is not None:
        body['description'] = description
    if depends_on is not None:
        body['depends_on'] = depends_on

    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name, artifact=body)


def create_blueprint_artifact_template(cmd, client,
                                       blueprint_name,
                                       scope,
                                       template,
                                       artifact_name,
                                       parameters=None,
                                       display_name=None,
                                       resource_group_art=None,
                                       description=None,
                                       depends_on=None):
    body = {'display_name': display_name,
            'template': json.loads(template),
            'kind': 'template',
            'description': description,
            'depends_on': depends_on,
            'parameters': json.loads(parameters) if parameters is not None else {},
            'resource_group': resource_group_art
            }
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name, artifact=body)


def update_blueprint_artifact_template(cmd, client,
                                       blueprint_name,
                                       scope,
                                       artifact_name,
                                       template=None,
                                       parameters=None,
                                       display_name=None,
                                       resource_group_art=None,
                                       description=None,
                                       depends_on=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name).as_dict()

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

    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=artifact_name, artifact=body)


def create_blueprint_published(cmd, client,
                               blueprint_name,
                               scope,
                               version_id,
                               change_notes=None):
    body = {}
    body['change_notes'] = change_notes  # str
    return client.create(scope=scope, blueprint_name=blueprint_name, version_id=version_id, published_blueprint=body)


def delete_blueprint_published(cmd, client,
                               blueprint_name,
                               scope,
                               version_id):
    return client.delete(scope=scope, blueprint_name=blueprint_name, version_id=version_id)


def get_blueprint_published(cmd, client,
                            blueprint_name,
                            scope,
                            version_id):
    return client.get(scope=scope, blueprint_name=blueprint_name, version_id=version_id)


def list_blueprint_published(cmd, client,
                             blueprint_name,
                             scope):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def get_blueprint_published_artifact(cmd, client,
                                     blueprint_name,
                                     scope,
                                     version_id,
                                     artifact_name):
    return client.get(scope=scope, blueprint_name=blueprint_name, version_id=version_id, artifact_name=artifact_name)


def list_blueprint_published_artifact(cmd, client,
                                      blueprint_name,
                                      scope,
                                      version_id):
    return client.list(scope=scope, blueprint_name=blueprint_name, version_id=version_id)


def create_blueprint_assignment(cmd, client,
                                assignment_name,
                                scope,
                                identity_type,
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
    body.setdefault('identity', {})['principal_id'] = identity_principal_id  # str
    body.setdefault('identity', {})['tenant_id'] = identity_tenant_id  # str
    body.setdefault('identity', {})['user_assigned_identities'] = identity_user_assigned_identities  # dictionary
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['blueprint_id'] = blueprint_id  # str
    body['parameters'] = json.loads(parameters) if parameters is not None else {}   # dictionary
    body['resource_groups'] = json.loads(resource_groups) if resource_groups is not None else {}  # dictionary
    body.setdefault('locks', {})['mode'] = locks_mode  # str
    body.setdefault('locks', {})['excluded_principals'] = None if locks_excluded_principals is None else locks_excluded_principals.split(',')
    return client.create_or_update(scope=scope, assignment_name=assignment_name, assignment=body)


def update_blueprint_assignment(cmd, client,
                                assignment_name,
                                scope,
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
        body.setdefault('identity', {})['principal_id'] = identity_principal_id  # str
    if identity_tenant_id is not None:
        body.setdefault('identity', {})['tenant_id'] = identity_tenant_id  # str
    if identity_user_assigned_identities is not None:
        body.setdefault('identity', {})['user_assigned_identities'] = identity_user_assigned_identities  # dictionary
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
        body.setdefault('locks', {})['excluded_principals'] = None if locks_excluded_principals is None else locks_excluded_principals.split(',')
    return client.create_or_update(scope=scope, assignment_name=assignment_name, assignment=body)


def delete_blueprint_assignment(cmd, client,
                                assignment_name,
                                scope):
    return client.delete(scope=scope, assignment_name=assignment_name)


def get_blueprint_assignment(cmd, client,
                             assignment_name,
                             scope):
    return client.get(scope=scope, assignment_name=assignment_name)


def list_blueprint_assignment(cmd, client,
                              scope):
    return client.list(scope=scope)


def who_is_blueprint_blueprint_assignment(cmd, client,
                                          assignment_name,
                                          scope):
    return client.who_is_blueprint(scope=scope, assignment_name=assignment_name)
