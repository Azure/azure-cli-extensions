# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import json
import os
import stat
from knack.util import CLIError

from azure.cli.core.aaz import has_value
from azure.cli.core.util import user_confirmation
from azure.core.exceptions import HttpResponseError
from ._client_factory import cf_artifacts
from .aaz.latest.blueprint import Create as _BlueprintCreate, Update as _BlueprintUpdate, Delete as _BlueprintDelete, \
    Show as _BlueprintShow, List as _BlueprintList, Publish as _BlueprintPublish
from .aaz.latest.blueprint.artifact import Delete as _BlueprintArtifactDelete, Show as _BlueprintArtifactShow, \
    List as _BlueprintArtifactList
from .aaz.latest.blueprint.assignment import Delete as _BlueprintAssignmentDelete, Show as _BlueprintAssignmentShow, \
    List as _BlueprintAssignmentList, Who as _BlueprintAssignmentWho
from .aaz.latest.blueprint.version import Delete as _BlueprintVersionDelete, Show as _BlueprintVersionShow, \
    List as _BlueprintVersionList
from .aaz.latest.blueprint.version.artifact import Show as _BlueprintVersionArtifactShow, \
    List as _BlueprintVersionArtifactList


def import_blueprint_with_artifacts(cmd,
                                    client,
                                    blueprint_name,
                                    input_path,
                                    management_group=None,
                                    subscription=None,
                                    resource_scope=None):
    artifact_client = cf_artifacts(cmd.cli_ctx)
    body = {}
    blueprint_path = os.path.join(input_path, 'blueprint.json')
    art_dict = {}

    try:
        with open(blueprint_path) as blueprint_file:
            try:
                blueprint = json.load(blueprint_file)
            except json.decoder.JSONDecodeError as ex:
                raise CLIError('JSON decode error for {}: {}'.format(blueprint_path, str(ex))) from ex
            if 'properties' not in blueprint:
                raise CLIError("blueprint.json does not contain the 'properties' field")
            blueprint_properties = blueprint['properties']
            if 'displayName' in blueprint_properties:
                body['display_name'] = blueprint_properties['displayName']  # str
            if 'description' in blueprint_properties:
                body['description'] = blueprint_properties['description']  # str
            body['target_scope'] = blueprint_properties.get('targetScope', 'subscription')  # str
            if 'parameters' in blueprint_properties:
                body['parameters'] = blueprint_properties['parameters']  # dictionary
            if 'resourceGroups' in blueprint_properties:
                body['resource_groups'] = blueprint_properties['resourceGroups']  # dictionary

        for filename in os.listdir(os.path.join(input_path, 'artifacts')):
            artifact_name = filename.split('.')[0]
            filepath = os.path.join(input_path, 'artifacts', filename)
            # skip hidden files
            if ((os.name != 'nt' and not filename.startswith('.')) or
                    (os.name == 'nt' and not bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN))):
                with open(filepath) as artifact_file:
                    try:
                        artifact = json.load(artifact_file)
                        art_dict[artifact_name] = artifact
                    except json.decoder.JSONDecodeError as ex:
                        raise CLIError('JSON decode error for {}: {}'.format(filepath, str(ex))) from ex
    except FileNotFoundError as ex:
        raise CLIError('File not Found: {}'.format(str(ex))) from ex

    # Only import when all files have no errors
    blueprint_response = client.create_or_update(resource_scope=resource_scope,
                                                 blueprint_name=blueprint_name,
                                                 blueprint=body)
    # delete old artifacts
    artifacts = artifact_client.list(resource_scope=resource_scope, blueprint_name=blueprint_name)
    for artifact in artifacts:
        artifact_client.delete(resource_scope=resource_scope,
                               blueprint_name=blueprint_name,
                               artifact_name=artifact.name)
    # create new artifacts
    for artifact_name, artifact in art_dict.items():
        artifact_client.create_or_update(resource_scope=resource_scope,
                                         blueprint_name=blueprint_name,
                                         artifact_name=artifact_name,
                                         artifact=artifact)

    return blueprint_response


def _blueprint_validator(cmd):
    from azure.cli.core.commands.client_factory import get_subscription_id
    args = cmd.ctx.args
    if has_value(args.management_group):
        args.resource_scope = '/providers/Microsoft.Management/managementGroups/{}'.format(args.management_group)
    elif has_value(args.subscription_id):
        args.resource_scope = '/subscriptions/{}'.format(args.subscription_id)
    else:
        args.resource_scope = '/subscriptions/{}'.format(get_subscription_id(cmd.cli_ctx))


def build_arguments_schema(args_schema):
    from azure.cli.core.aaz import AAZStrArg
    args_schema.management_group = AAZStrArg(
        options=['--management-group', '-m'],
        arg_group="Resource_scope",
        help="Use management group for the scope of the blueprint.")
    args_schema.subscription_id = AAZStrArg(
        options=['--subscription', '-s'],
        arg_group="Resource_scope",
        help="Use subscription for the scope of the blueprint. If --management-group is not specified, "
             "--subscription value or the default subscription will be used as the scope.")
    args_schema.resource_scope._required = False
    args_schema.resource_scope._registered = False
    return args_schema


# ignore the global subscription param
def cli_arguments_loader(args):
    from knack.arguments import CLICommandArgument
    args.append(("_subscription", CLICommandArgument(dest="_subscription", options_list=["--___subscription"])))
    return args


class BlueprintCreate(_BlueprintCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintUpdate(_BlueprintUpdate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintDelete(_BlueprintDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintShow(_BlueprintShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintList(_BlueprintList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


def export_blueprint_with_artifacts(cmd, client, blueprint_name, output_path,
                                    skip_confirmation=False, management_group=None,
                                    subscription=None, resource_scope=None, **kwargs):
    # match folder structure required for import_blueprint_with_artifact
    blueprint_parent_folder = os.path.join(os.path.abspath(output_path), blueprint_name)
    blueprint_file_location = os.path.join(blueprint_parent_folder, 'blueprint.json')
    artifacts_location = os.path.join(blueprint_parent_folder, 'artifacts')

    if os.path.exists(blueprint_parent_folder) and os.listdir(blueprint_parent_folder) and not skip_confirmation:
        user_prompt = f"That directory already contains a folder" \
                      f" with the name {blueprint_name}. Would you like to continue?"
        user_confirmation(user_prompt)

    try:
        blueprint = client.get(resource_scope=resource_scope, blueprint_name=blueprint_name)
        serialized_blueprint = blueprint.serialize()
    except HttpResponseError as error:
        raise CLIError('Unable to export blueprint: {}'.format(str(error.message))) from error

    os.makedirs(artifacts_location, exist_ok=True)

    with open(blueprint_file_location, 'w') as f:
        json.dump(serialized_blueprint, f, indent=4)

    artifact_client = cf_artifacts(cmd.cli_ctx)
    available_artifacts = artifact_client.list(resource_scope=resource_scope, blueprint_name=blueprint_name)

    for artifact in available_artifacts:
        artifact_file_location = os.path.join(artifacts_location, artifact.name + '.json')
        serialized_artifact = artifact.serialize()
        with open(artifact_file_location, 'w') as f:
            json.dump(serialized_artifact, f, indent=4)

    return blueprint


class BlueprintArtifactDelete(_BlueprintArtifactDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintArtifactShow(_BlueprintArtifactShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintArtifactList(_BlueprintArtifactList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


def add_blueprint_resource_group(cmd,
                                 blueprint_name,
                                 management_group=None,
                                 subscription=None,
                                 resource_scope=None,
                                 artifact_name=None,
                                 display_name=None,
                                 rg_name=None,
                                 rg_location=None,
                                 description=None,
                                 depends_on=None,
                                 tags=None):
    args = {
        "name": blueprint_name,
        "resource_scope": resource_scope,
    }
    body = BlueprintShow(cli_ctx=cmd.cli_ctx)(command_args=args)
    rg_key = artifact_name
    body.setdefault('resourceGroups', {})
    if artifact_name is None:
        rg_len = len(body['resourceGroups'])
        for i in range(rg_len + 1):
            posix = '' if i == 0 else i + 1
            rg_key = "ResourceGroup{}".format(posix)
            if rg_key not in body['resourceGroups']:
                break
    elif artifact_name in body['resourceGroups']:
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
    args.setdefault('resource_groups', {})[rg_key] = resource_group
    rgs = BlueprintUpdate(cli_ctx=cmd.cli_ctx)(command_args=args)['resourceGroups']
    return {k: v for k, v in rgs.items() if k == artifact_name}


def update_blueprint_resource_group(cmd,
                                    blueprint_name,
                                    artifact_name,
                                    management_group=None,
                                    subscription=None,
                                    resource_scope=None,
                                    rg_name=None,
                                    rg_location=None,
                                    display_name=None,
                                    description=None,
                                    depends_on=None,
                                    tags=None):
    args = {
        "name": blueprint_name,
        "resource_scope": resource_scope,
    }
    body = BlueprintShow(cli_ctx=cmd.cli_ctx)(command_args=args)
    if artifact_name not in body.setdefault('resourceGroups', {}):
        raise CLIError('The specified artifact name: {} can not be found.'.format(artifact_name))
    resource_group = body['resourceGroups'][artifact_name]
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
    args.setdefault('resource_groups', {})[artifact_name] = resource_group
    rgs = BlueprintUpdate(cli_ctx=cmd.cli_ctx)(command_args=args)['resourceGroups']
    return {k: v for k, v in rgs.items() if k == artifact_name}


# todo test
def remove_blueprint_resource_group(cmd, blueprint_name,
                                    artifact_name, management_group=None, subscription=None, resource_scope=None):
    args = {
        "name": blueprint_name,
        "resource_scope": resource_scope,
    }
    body = BlueprintShow(cli_ctx=cmd.cli_ctx)(command_args=args)
    if artifact_name not in body.setdefault('resourceGroups', {}):
        raise CLIError('The specified artifact name: {} can not be found.'.format(artifact_name))
    deleted_rg = body['resourceGroups'][artifact_name]
    del body['resourceGroups'][artifact_name]
    args['resource_groups'] = body['resourceGroups']
    BlueprintUpdate(cli_ctx=cmd.cli_ctx)(command_args=args)
    return deleted_rg


def get_blueprint_resource_group(cmd, blueprint_name,
                                 artifact_name, management_group=None, subscription=None, resource_scope=None):
    show_args = {
        "name": blueprint_name,
        "resource_scope": resource_scope,
    }
    rgs = BlueprintShow(cli_ctx=cmd.cli_ctx)(command_args=show_args)['resourceGroups']
    return {k: v for k, v in rgs.items() if k == artifact_name}


def list_blueprint_resource_group(cmd, blueprint_name, management_group=None,
                                  subscription=None, resource_scope=None):
    show_args = {
        "name": blueprint_name,
        "resource_scope": resource_scope,
    }
    return BlueprintShow(cli_ctx=cmd.cli_ctx)(command_args=show_args)['resourceGroups']


def create_blueprint_artifact_policy(client,
                                     blueprint_name,
                                     policy_definition_id,
                                     artifact_name,
                                     management_group=None,
                                     subscription=None,
                                     resource_scope=None,
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
    return client.create_or_update(resource_scope=resource_scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def update_blueprint_artifact_policy(client,
                                     blueprint_name,
                                     artifact_name,
                                     management_group=None,
                                     subscription=None,
                                     resource_scope=None,
                                     parameters=None,
                                     display_name=None,
                                     resource_group_art=None,
                                     description=None,
                                     depends_on=None):
    body = client.get(resource_scope=resource_scope,
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

    return client.create_or_update(resource_scope=resource_scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def create_blueprint_artifact_role(client,
                                   blueprint_name,
                                   role_definition_id,
                                   principal_ids,
                                   artifact_name,
                                   management_group=None,
                                   subscription=None,
                                   resource_scope=None,
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
    return client.create_or_update(resource_scope=resource_scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def update_blueprint_artifact_role(client,
                                   blueprint_name,
                                   artifact_name,
                                   management_group=None,
                                   subscription=None,
                                   resource_scope=None,
                                   display_name=None,
                                   resource_group_art=None,
                                   description=None,
                                   depends_on=None):
    body = client.get(resource_scope=resource_scope,
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

    return client.create_or_update(resource_scope=resource_scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def create_blueprint_artifact_template(client,
                                       blueprint_name,
                                       template,
                                       artifact_name,
                                       management_group=None,
                                       subscription=None,
                                       resource_scope=None,
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
    return client.create_or_update(resource_scope=resource_scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


def update_blueprint_artifact_template(client,
                                       blueprint_name,
                                       artifact_name,
                                       management_group=None,
                                       subscription=None,
                                       resource_scope=None,
                                       template=None,
                                       parameters=None,
                                       display_name=None,
                                       resource_group_art=None,
                                       description=None,
                                       depends_on=None):
    body = client.get(resource_scope=resource_scope,
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

    return client.create_or_update(resource_scope=resource_scope,
                                   blueprint_name=blueprint_name,
                                   artifact_name=artifact_name,
                                   artifact=body)


class BlueprintPublish(_BlueprintPublish):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintVersionDelete(_BlueprintVersionDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintVersionShow(_BlueprintVersionShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintVersionList(_BlueprintVersionList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintVersionArtifactShow(_BlueprintVersionArtifactShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintVersionArtifactList(_BlueprintVersionArtifactList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


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
                                resource_scope=None,
                                location=None,
                                resource_groups=None,
                                user_assigned_identity=None,
                                display_name=None,
                                description=None,
                                blueprint_id=None,
                                locks_mode=None,
                                locks_excluded_principals=None,
                                parameters=None):
    from .vendored_sdks.blueprint.models._blueprint_management_client_enums import ManagedServiceIdentityType
    try:
        result = client.get(resource_scope=resource_scope, assignment_name=assignment_name)
        if result is not None:
            raise CLIError("An assignment with name '{}' in subscription '{}' already exists."
                           " Please use 'az blueprint assignment update' to update an existing assignment."
                           .format(assignment_name, resource_scope))
    except HttpResponseError:  # AssignmentNotFound
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
        result = client.who_is_blueprint(resource_scope=resource_scope, assignment_name=assignment_name)
        if result is None:
            raise CLIError("Blueprint service failed to return the SPN for assignment:{}".format(assignment_name))
        spn = result.object_id
        _assign_owner_role_in_target_scope(cmd, resource_scope, spn)
    return client.create_or_update(resource_scope=resource_scope, assignment_name=assignment_name, assignment=body)


def _assign_owner_role_in_target_scope(cmd, role_scope, spn_object_id,):
    from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment
    role_assignments = list_role_assignments(cmd, assignee=spn_object_id, role='Owner', scope=role_scope)
    if not role_assignments:
        create_role_assignment(cmd, role='Owner', assignee_object_id=spn_object_id, scope=role_scope,
                               assignee_principal_type='ServicePrincipal')


def update_blueprint_assignment(cmd, client,
                                assignment_name,
                                management_group=None,
                                subscription=None,
                                resource_scope=None,
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

    body = client.get(resource_scope=resource_scope, assignment_name=assignment_name).as_dict()
    if location is not None:
        body['location'] = location  # str
    if identity_type is not None:
        body['identity'] = {}
        body['identity']['type'] = identity_type  # str
    if user_assigned_identity is not None:
        body['identity']['user_assigned_identities'] = {user_assigned_identity: {}}  # dictionary
    elif 'user_assigned_identities' in body['identity']:
        for identity in body['identity']['user_assigned_identities']:
            body['identity']['user_assigned_identities'][identity] = {}
            # service only accept empty json of a user-assigned identity in request

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
        result = client.who_is_blueprint(resource_scope=resource_scope, assignment_name=assignment_name)
        if result is None:
            raise CLIError("Blueprint service failed to return the SPN for assignment:{}".format(assignment_name))
        spn = result.object_id
        _assign_owner_role_in_target_scope(client, resource_scope, spn)
    return client.create_or_update(resource_scope=resource_scope,
                                   assignment_name=assignment_name,
                                   assignment=body)


class BlueprintAssignmentDelete(_BlueprintAssignmentDelete):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


def get_blueprint_assignment(client, assignment_name, management_group=None, subscription=None, resource_scope=None):
    return client.get(resource_scope=resource_scope, assignment_name=assignment_name)


class BlueprintAssignmentShow(_BlueprintAssignmentShow):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintAssignmentList(_BlueprintAssignmentList):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


class BlueprintAssignmentWho(_BlueprintAssignmentWho):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        return build_arguments_schema(args_schema)

    # ignore the global subscription param
    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        cli_arguments_loader(args)
        return args

    def pre_operations(self):
        args = self.ctx.args
        if not has_value(args.resource_scope):
            _blueprint_validator(self)


def _process_depends_on_for_update(depends_on):
    if not depends_on:  # [] for case: --depends-on
        return None
    if not any(depends_on):  # [''] for case: --depends-on= /--depends-on ""
        return None
    return depends_on
