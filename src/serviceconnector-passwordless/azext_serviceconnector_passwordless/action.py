# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from collections import defaultdict
from azure.cli.core.azclierror import ValidationError
from azure.cli.command_modules.serviceconnector._resource_config import (
    RESOURCE
)


# pylint: disable=consider-using-f-string, raise-missing-from
def is_mysql_target(command_name):
    target_name = command_name.split(' ')[-1]
    return target_name.lower() == RESOURCE.MysqlFlexible.value.lower()


class AddUserAssignedIdentityAuthInfo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string, namespace.command)
        namespace.user_identity_auth_info = action

    def get_action(self, values, option_string, command_name):  # pylint: disable=no-self-use
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError(
                'usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'client-id':
                d['client_id'] = v[0]
            elif kl == 'subs-id':
                d['subscription_id'] = v[0]
            elif kl == 'user-object-id':
                d['user_object_id'] = v[0]
            elif is_mysql_target(command_name) and kl == 'mysql-identity-id':
                d['mysql-identity-id'] = v[0]
            else:
                raise ValidationError('Unsupported Key {} is provided for parameter --user-identity. All '
                                      'possible keys are: client-id, subs-id{}'.format(
                                          k, ', mysql-identity-id' if is_mysql_target(command_name) else ''))
        if 'client_id' not in d or 'subscription_id' not in d:
            raise ValidationError(
                'Required keys missing for parameter --user-identity: client-id, subs-id')
        d['auth_type'] = 'userAssignedIdentity'
        return d


class AddSystemAssignedIdentityAuthInfo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string, namespace.command)
        namespace.system_identity_auth_info = action

    def get_action(self, values, option_string, command_name):  # pylint: disable=no-self-use
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError(
                'Usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            v = properties[k]
            if is_mysql_target(command_name) and k.lower() == 'mysql-identity-id':
                d['mysql-identity-id'] = v[0]
            elif k.lower() == 'user-object-id':
                d['user_object_id'] = v[0]
            else:
                raise ValidationError(
                    'Unsupported Key {} is provided for parameter --system-identity')
        d['auth_type'] = 'systemAssignedIdentity'
        return d


class AddUserAccountAuthInfo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string, namespace.command)
        namespace.user_account_auth_info = action

    def get_action(self, values, option_string, command_name):  # pylint: disable=no-self-use
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError(
                'usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'object-id':
                d['principal_id'] = v[0]
            elif is_mysql_target(command_name) and kl == 'mysql-identity-id':
                d['mysql-identity-id'] = v[0]
            else:
                raise ValidationError('Unsupported Key {} is provided for parameter --user-account. All '
                                      'possible keys are: principal-id{}'.format(
                                          k, ', mysql-identity-id' if is_mysql_target(command_name) else ''))
        d['auth_type'] = 'userAccount'
        return d


class AddServicePrincipalAuthInfo(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string, namespace.command)
        namespace.service_principal_auth_info_secret = action

    def get_action(self, values, option_string, command_name):  # pylint: disable=no-self-use
        try:
            properties = defaultdict(list)
            for (k, v) in (x.split('=', 1) for x in values):
                properties[k].append(v)
            properties = dict(properties)
        except ValueError:
            raise ValidationError(
                'Usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'client-id':
                d['client_id'] = v[0]
            elif kl == 'object-id':
                d['principal_id'] = v[0]
            elif kl == 'secret':
                d['secret'] = v[0]
            elif is_mysql_target(command_name) and kl == 'mysql-identity-id':
                d['mysql-identity-id'] = v[0]
            else:
                raise ValidationError('Unsupported Key {} is provided for parameter --service-principal. Possible '
                                      'keys are: client-id, object-id, secret{}'.format(
                                          k, ', mysql-identity-id' if is_mysql_target(command_name) else ''))
        if 'client_id' not in d or 'secret' not in d:
            raise ValidationError('Required keys missing for parameter --service-principal. '
                                  'Required keys are: client-id, secret')
        if 'principal_id' not in d:
            from azure.cli.command_modules.serviceconnector._utils import run_cli_cmd
            output = run_cli_cmd(
                'az ad sp show --id {}'.format(d['client_id']))
            if output:
                d['principal_id'] = output.get('id')
            else:
                raise ValidationError('Could not resolve object-id from the given client-id: {}. Please '
                                      'confirm the client-id and provide the object-id (Enterprise Application) '
                                      'of the service principal, by using --service-principal client-id=XX '
                                      'object-id=XX secret=XX'.format(d['client_id']))

        d['auth_type'] = 'servicePrincipalSecret'
        return d
