# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


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
    body['parameters'] = parameters  # dictionary
    return client.create_or_update(scope=scope, blueprint_name=name, blueprint=body)


def update_blueprint(cmd, client,
                     name,
                     scope,
                     description=None
                     ):
    body = client.get(scope=scope, blueprint_name=name).as_dict()
    if description is not None:
        body['description'] = description  # str
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

def create_blueprint_artifact_resource_group(cmd, client,
                              blueprint_name,
                              scope,
                              artifact_name=None,
                              display_name=None,
                              name=None,
                              location=None,
                              description=None,
                              depends_on=None,
                              tags=None
                              ):
    body = client.get(scope=scope, blueprint_name=blueprint_name).as_dict()
    rg_key = artifact_name
    body.setdefault('resource_groups', {})
    if artifact_name is None:
        rg_len = len(body['resource_groups'])
        for i in range(rg_len+1):
            posix = '' if i == 0 else i + 1 
            rg_key = "ResourceGroup{}".format(posix)
            if rg_key not in body['resource_groups']:
                break 
    elif artifact_name in body['resource_groups']:
        raise CLIError('A resource group artifact with the same name already exists.') 
    
    resource_group = {
        "name": name, 
        "location": location,
        "display_name": display_name,
        "description": description,
        "depends_on": depends_on,
        "tags":tags
        }
    body.setdefault('resource_groups', {})[rg_key] = resource_group
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, blueprint=body).resource_groups

def create_blueprint_artifact_policy(cmd, client,
                              blueprint_name,
                              scope,
                              policy_definition_id,
                              name,
                              parameters=None,
                              display_name=None,
                              resource_group_art=None,
                              description=None,
                              depends_on=None
                              ):
    import json                   
    body = {'display_name': display_name,
            'policy_definition_id': policy_definition_id,
            'kind': 'policyAssignment',
            'description': description,
            'depends_on': depends_on,
            'parameters': json.loads(parameters) if parameters else {},
            'resource_group': resource_group_art
        }
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=name, artifact=body)

def create_blueprint_artifact_role(cmd, client,
                              blueprint_name,
                              scope,
                              role_definition_id,
                              principal_ids,
                              name,
                              parameters=None,
                              display_name=None,
                              resource_group_art=None,
                              description=None,
                              depends_on=None
                              ):
    import json                   
    body = {'display_name': display_name,
            'role_definition_id': role_definition_id,
            'kind': 'roleAssignment',
            'description': description,
            'depends_on': depends_on,
            'parameters': json.loads(parameters) if parameters else {},
            'resource_group': resource_group_art,
            'principal_ids': principal_ids
        }
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=name, artifact=body)

def update_blueprint_artifact_resource_group(cmd, client,
                              blueprint_name,
                              scope,
                              artifact_name,
                              name=None,
                              location=None,
                              display_name=None,
                              description=None,
                              depends_on=None,
                              tags=None):
    body = client.get(scope=scope, blueprint_name=name).as_dict()
    if artifact_name not in body.setdefault('resource_groups', {}):
        raise CLIError('The specified artifact name can not be found.')
    resource_group = body['resource_groups'][artifact_name]
    if name is not None:
        resource_group['name'] = name
    if location is not None:
        resource_group['location'] = location
    if display_name is not None:
        resource_group['display_name'] = display_name
    if description is not None:
        resource_group['description'] = description  # str
    if depends_on is not None:
        resource_group['depends_on'] = depends_on
    if tags is not None:
        resource_group['tags'] = tags
    
    return client.create_or_update(scope=scope, blueprint_name=name, blueprint=body)


def delete_blueprint_artifact(cmd, client,
                              blueprint_name,
                              name,
                              scope):
    return client.delete(scope=scope, blueprint_name=blueprint_name, artifact_name=name)


def get_blueprint_artifact(cmd, client,
                           blueprint_name,
                           name,
                           scope):
    return client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=name)


def list_blueprint_artifact(cmd, client,
                            blueprint_name,
                            scope):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def create_blueprint_published(cmd, client,
                               name,
                               scope,
                               version_id,
                               display_name=None,
                               description=None,
                               target_scope=None,
                               parameters=None,
                               resource_groups=None,
                               blueprint_name=None,
                               change_notes=None):
    body = {}
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['target_scope'] = target_scope  # str
    body['parameters'] = parameters  # dictionary
    body['resource_groups'] = resource_groups  # dictionary
    body['blueprint_name'] = blueprint_name  # str
    body['change_notes'] = change_notes  # str
    return client.create(scope=scope, blueprint_name=name, version_id=version_id, published_blueprint=body)


def delete_blueprint_published(cmd, client,
                               name,
                               scope,
                               version_id):
    return client.delete(scope=scope, blueprint_name=name, version_id=version_id)


def get_blueprint_published(cmd, client,
                            name,
                            scope,
                            version_id):
    return client.get(scope=scope, blueprint_name=name, version_id=version_id)


def list_blueprint_published(cmd, client,
                             name,
                             scope):
    return client.list(scope=scope, blueprint_name=name)


def get_blueprint_published_artifact(cmd, client,
                                     blueprint_name,
                                     scope,
                                     version_id,
                                     name):
    return client.get(scope=scope, blueprint_name=blueprint_name, version_id=version_id, artifact_name=name)


def list_blueprint_published_artifact(cmd, client,
                                      blueprint_name,
                                      scope,
                                      version_id):
    return client.list(scope=scope, blueprint_name=blueprint_name, version_id=version_id)


def create_blueprint_assignment(cmd, client,
                     name,
                     scope,
                     location,
                     identity_type,
                     parameters,
                     resource_groups,
                     identity_principal_id=None,
                     identity_tenant_id=None,
                     identity_user_assigned_identities=None,
                     display_name=None,
                     description=None,
                     blueprint_id=None,
                     locks_mode=None,
                     locks_excluded_principals=None):
    body = {}
    body['location'] = location  # str
    body.setdefault('identity', {})['type'] = identity_type  # str
    body.setdefault('identity', {})['principal_id'] = identity_principal_id  # str
    body.setdefault('identity', {})['tenant_id'] = identity_tenant_id  # str
    body.setdefault('identity', {})['user_assigned_identities'] = identity_user_assigned_identities  # dictionary
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['blueprint_id'] = blueprint_id  # str
    body['parameters'] = parameters  # dictionary
    body['resource_groups'] = resource_groups  # dictionary
    body.setdefault('locks', {})['mode'] = locks_mode  # str
    body.setdefault('locks', {})['excluded_principals'] = None if locks_excluded_principals is None else locks_excluded_principals.split(',')
    return client.create_or_update(scope=scope, assignment_name=name, assignment=body)


def update_blueprint_assignment(cmd, client,
                     name,
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
    body = client.get(scope=scope, assignment_name=name).as_dict()
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
        body['parameters'] = parameters  # dictionary
    if resource_groups is not None:
        body['resource_groups'] = resource_groups  # dictionary
    if locks_mode is not None:
        body.setdefault('locks', {})['mode'] = locks_mode  # str
    if locks_excluded_principals is not None:
        body.setdefault('locks', {})['excluded_principals'] = None if locks_excluded_principals is None else locks_excluded_principals.split(',')
    return client.create_or_update(scope=scope, assignment_name=name, assignment=body)


def delete_blueprint_assignment(cmd, client,
                     name,
                     scope):
    return client.delete(scope=scope, assignment_name=name)


def get_blueprint_assignment(cmd, client,
                  name,
                  scope):
    return client.get(scope=scope, assignment_name=name)


def list_blueprint_assignment(cmd, client,
                   scope):
    return client.list(scope=scope)


def who_is_blueprint_blueprint_assignment(cmd, client,
                               name,
                               scope):
    return client.who_is_blueprint(scope=scope, assignment_name=name)
