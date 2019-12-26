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
                     scope=None,
                     display_name=None,
                     description=None,
                     target_scope=None,
                     parameters=None,
                     resource_groups=None,
                     versions=None,
                     layout=None):
    body = {}
    body['display_name'] = display_name  # str
    body['description'] = description  # str
    body['target_scope'] = target_scope  # str
    body['parameters'] = parameters  # dictionary
    body['resource_groups'] = resource_groups  # dictionary
    body['versions'] = versions  # unknown-primary[object]
    body['layout'] = layout  # unknown-primary[object]
    return client.create_or_update(scope=scope, blueprint_name=name, blueprint=body)


def update_blueprint(cmd, client,
                     name,
                     scope=None,
                     display_name=None,
                     description=None,
                     target_scope=None,
                     parameters=None,
                     resource_groups=None,
                     versions=None,
                     layout=None):
    body = client.get(scope=scope, blueprint_name=name).as_dict()
    if display_name is not None:
        body['display_name'] = display_name  # str
    if description is not None:
        body['description'] = description  # str
    if target_scope is not None:
        body['target_scope'] = target_scope  # str
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if resource_groups is not None:
        body['resource_groups'] = resource_groups  # dictionary
    if versions is not None:
        body['versions'] = versions  # unknown-primary[object]
    if layout is not None:
        body['layout'] = layout  # unknown-primary[object]
    return client.create_or_update(scope=scope, blueprint_name=name, blueprint=body)


def delete_blueprint(cmd, client,
                     name,
                     scope=None):
    return client.delete(scope=scope, blueprint_name=name)


def get_blueprint(cmd, client,
                  name,
                  scope=None):
    return client.get(scope=scope, blueprint_name=name)


def list_blueprint(cmd, client,
                   scope=None):
    return client.list(scope=scope)


def create_blueprint_artifact(cmd, client,
                              blueprint_name,
                              name,
                              scope=None):
    body = {}
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=name, artifact=body)


def update_blueprint_artifact(cmd, client,
                              blueprint_name,
                              name,
                              scope=None):
    body = client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=name).as_dict()
    return client.create_or_update(scope=scope, blueprint_name=blueprint_name, artifact_name=name, artifact=body)


def delete_blueprint_artifact(cmd, client,
                              blueprint_name,
                              name,
                              scope=None):
    return client.delete(scope=scope, blueprint_name=blueprint_name, artifact_name=name)


def get_blueprint_artifact(cmd, client,
                           blueprint_name,
                           name,
                           scope=None):
    return client.get(scope=scope, blueprint_name=blueprint_name, artifact_name=name)


def list_blueprint_artifact(cmd, client,
                            blueprint_name,
                            scope=None):
    return client.list(scope=scope, blueprint_name=blueprint_name)


def create_blueprint_published(cmd, client,
                               name,
                               version_id,
                               scope=None,
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


def update_blueprint_published(cmd, client,
                               name,
                               version_id,
                               scope=None,
                               display_name=None,
                               description=None,
                               target_scope=None,
                               parameters=None,
                               resource_groups=None,
                               blueprint_name=None,
                               change_notes=None):
    body = client.get(scope=scope, blueprint_name=name, version_id=version_id).as_dict()
    if display_name is not None:
        body['display_name'] = display_name  # str
    if description is not None:
        body['description'] = description  # str
    if target_scope is not None:
        body['target_scope'] = target_scope  # str
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if resource_groups is not None:
        body['resource_groups'] = resource_groups  # dictionary
    if blueprint_name is not None:
        body['blueprint_name'] = blueprint_name  # str
    if change_notes is not None:
        body['change_notes'] = change_notes  # str
    return client.create(scope=scope, blueprint_name=name, version_id=version_id, published_blueprint=body)


def delete_blueprint_published(cmd, client,
                               name,
                               version_id,
                               scope=None):
    return client.delete(scope=scope, blueprint_name=name, version_id=version_id)


def get_blueprint_published(cmd, client,
                            name,
                            version_id,
                            scope=None):
    return client.get(scope=scope, blueprint_name=name, version_id=version_id)


def list_blueprint_published(cmd, client,
                             name,
                             scope=None):
    return client.list(scope=scope, blueprint_name=name)


def get_blueprint_published_artifact(cmd, client,
                                     blueprint_name,
                                     version_id,
                                     name,
                                     scope=None):
    return client.get(scope=scope, blueprint_name=blueprint_name, version_id=version_id, artifact_name=name)


def list_blueprint_published_artifact(cmd, client,
                                      blueprint_name,
                                      version_id,
                                      scope=None):
    return client.list(scope=scope, blueprint_name=blueprint_name, version_id=version_id)


def create_blueprint_assignment(cmd, client,
                     name,
                     location,
                     identity_type,
                     parameters,
                     resource_groups,
                     scope=None,
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
                     scope=None):
    return client.delete(scope=scope, assignment_name=name)


def get_blueprint_assignment(cmd, client,
                  name,
                  scope=None):
    return client.get(scope=scope, assignment_name=name)


def list_blueprint_assignment(cmd, client,
                   scope=None):
    return client.list(scope=scope)


def who_is_blueprint_blueprint_assignment(cmd, client,
                               name,
                               scope=None):
    return client.who_is_blueprint(scope=scope, assignment_name=name)
