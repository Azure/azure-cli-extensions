# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import deepcopy

from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.aaz import AAZUndefined
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.command_operation import WaitCommandOperation

from ._create import Create as _ClusterCreate
from ._show import Show as _ClusterShow
from ._update import Update as _ClusterUpdate


logger = get_logger(__name__)


def _split_encryption_arguments(args_schema):
    args_schema.data_encryption._registered = False  # pylint: disable=protected-access
    for name in ['primary_key_uri', 'primary_user_assigned_identity_id']:
        argument = deepcopy(getattr(args_schema.data_encryption, name))
        options = ['--' + name.replace('_', '-')]
        if name == 'primary_user_assigned_identity_id':
            options.append('--primary-user-id')
        argument._options = options  # pylint: disable=protected-access
        argument._help['name'] = ' '.join(options)  # pylint: disable=protected-access
        setattr(args_schema, name, argument)
    return args_schema


class ClusterCreate(_ClusterCreate):
    AZ_HELP = {
        'type': 'command',
        'short-summary': 'Create a HorizonDB cluster.',
        'long-summary': 'Waits for cluster provisioning and retrieves the cluster to return its current state.',
        'examples': [{
            'name': 'Create a HorizonDB cluster',
            'text': 'az horizondb cluster create --resource-group example-resource-group '
                    '--cluster-name example-cluster --location eastus2 --version 17 '
                    '--geo-redundancy Enabled',
        }],
    }

    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = _split_encryption_arguments(super()._build_arguments_schema(*args, **kwargs))
        for name, summary in {
            'primary_key_uri': (
                'Versionless Azure Key Vault key URI. Must be supplied together with '
                '--primary-user-assigned-identity-id to enable data encryption.'
            ),
            'primary_user_assigned_identity_id': (
                'Resource ID of the user-assigned managed identity used to access the encryption key. '
                'Must be supplied together with --primary-key-uri.'
            ),
        }.items():
            argument = getattr(args_schema, name)
            argument._help['short-summary'] = summary  # pylint: disable=protected-access
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        key_uri = args.primary_key_uri.to_serialized_data()
        identity_id = args.primary_user_assigned_identity_id.to_serialized_data()
        has_key = key_uri not in (AAZUndefined, None)
        has_identity = identity_id not in (AAZUndefined, None)
        if has_key != has_identity or key_uri == '' or identity_id == '':
            raise InvalidArgumentValueError(
                '--primary-key-uri and --primary-user-assigned-identity-id '
                'must both be supplied with non-empty values to enable data encryption.'
            )
        if has_key:
            args.data_encryption = {
                'primary_key_uri': key_uri,
                'primary_user_assigned_identity_id': identity_id,
                'type': 'AzureKeyVault',
            }

    def _output(self, *args, **kwargs):
        command_args = {
            name: getattr(self.ctx.args, name).to_serialized_data()
            for name in ['cluster_name', 'resource_group']
        }
        command_args['subscription'] = self.ctx.subscription_id
        return _ClusterShow(cli_ctx=self.cli_ctx)(command_args=command_args)

    def post_operations(self):
        args = self.ctx.args
        cluster_args = {
            'cluster_name': args.cluster_name.to_serialized_data(),
            'resource_group': args.resource_group.to_serialized_data(),
            'subscription': self.ctx.subscription_id,
        }

        def get_cluster(**command_args):
            return _ClusterShow(cli_ctx=self.cli_ctx)(command_args=command_args)

        logger.warning("Waiting for cluster '%s' provisioning to complete...", cluster_args['cluster_name'])
        wait_result = WaitCommandOperation.wait(
            command_args={
                **cluster_args,
                'created': True,
                'updated': False,
                'deleted': False,
                'exists': False,
                'custom': None,
                'interval': 30,
                'timeout': 3600,
            },
            cli_ctx=self.cli_ctx,
            getter=get_cluster,
        )
        # The standard wait helper returns a CLIError on timeout instead of raising it.
        if isinstance(wait_result, CLIError):
            raise wait_result


class ClusterUpdate(_ClusterUpdate):
    AZ_HELP = {
        **_ClusterUpdate.AZ_HELP,
        'examples': [{
            'name': 'Rotate the customer-managed key used by a HorizonDB cluster',
            'text': 'az horizondb cluster update --resource-group example-resource-group '
                    '--cluster-name example-cluster --primary-key-uri https://example.vault.azure.net/keys/new-key',
        }, {
            'name': 'Update the managed identity used to access the encryption key',
            'text': 'az horizondb cluster update --resource-group example-resource-group '
                    '--cluster-name example-cluster --primary-user-id '
                    '/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/'
                    'example-resource-group/providers/Microsoft.ManagedIdentity/userAssignedIdentities/example-identity',
        }],
    }

    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        return _split_encryption_arguments(super()._build_arguments_schema(*args, **kwargs))

    def pre_operations(self):
        encryption = {}
        for name in ['primary_key_uri', 'primary_user_assigned_identity_id']:
            value = getattr(self.ctx.args, name).to_serialized_data()
            if value == '':
                raise InvalidArgumentValueError(f"--{name.replace('_', '-')} must not be empty.")
            if value not in (AAZUndefined, None):
                encryption[name] = value
        if encryption:
            self.ctx.args.data_encryption = encryption
