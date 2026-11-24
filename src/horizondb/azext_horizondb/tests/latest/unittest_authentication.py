# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from argparse import ArgumentParser
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import uuid4

from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core import PipelineClient
from azure.core.pipeline.policies import ContentDecodePolicy
from knack.prompting import NoTTYException

from azext_horizondb import HorizonDBCommandsLoader


class AuthenticationTests(TestCase):
    def setUp(self):
        prefix = 'horizondb cluster authentication '
        table = HorizonDBCommandsLoader(cli_ctx=get_default_cli()).load_command_table(None)
        self.commands = {name[len(prefix):]: cmd for name, cmd in table.items() if name.startswith(prefix)}
        self.args = dict(subscription='00000000-0000-0000-0000-000000000001', resource_group='rg', cluster_name='db')
        self.client = Mock(wraps=PipelineClient('https://management.azure.com'))
        self.client.build_lro_polling = Mock()
        client_patch = patch('azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client', return_value=self.client)
        client_patch.start()
        self.addCleanup(client_patch.stop)
        self.url = ('https://management.azure.com/subscriptions/' + self.args['subscription'] +
                    '/resourceGroups/rg/providers/Microsoft.HorizonDb/clusters/db/authentications')
        self.query = '?api-version=2026-10-01-preview'
        self.secret = '[' + uuid4().hex + ']'  # Include punctuation meaningful to AAZ shorthand.
        self.method = {'name': 'passwordMethod', 'properties': {
            'state': 'Enabled', 'provisioningState': 'Succeeded', 'administratorLogin': 'dbadmin',
            'administratorLoginPassword': self.secret,
        }}

    @staticmethod
    def response(status, data):
        response = Mock(context={ContentDecodePolicy.CONTEXT_NAME: data})
        response.http_response.status_code = status
        return response

    def run_command(self, name, **kwargs):
        return self.commands[name](command_args=dict(self.args, **kwargs))

    def test_collection_and_password_get(self):
        self.assertEqual(set(self.commands), {'list', 'password show', 'password create', 'password update',
                                              'password wait'})
        entra = {'name': 'microsoftEntra', 'properties': {'state': 'Disabled'}}
        next_page = self.url + '?page=2'
        self.client.send_request.side_effect = [
            self.response(200, {'value': [self.method], 'nextLink': next_page}),
            self.response(200, {'value': [entra]}),
            self.response(200, self.method),
        ]
        methods = list(self.run_command('list'))
        self.assertEqual([item['name'] for item in methods], ['passwordMethod', 'microsoftEntra'])
        shown = self.run_command('password show')
        self.assertEqual(shown['properties'], {
            'administratorLogin': 'dbadmin', 'state': 'Enabled', 'provisioningState': 'Succeeded'})
        self.assertNotIn(self.secret, str(methods))
        requests = [call.kwargs['request'] for call in self.client.send_request.call_args_list]
        self.assertEqual([(r.method, r.url) for r in requests], [
            ('GET', self.url + self.query), ('GET', next_page), ('GET', self.url + '/passwordMethod' + self.query)])

    def password_argument(self, command, *values, option='--admin-password'):
        command.load_arguments()
        settings = command.arguments['administrator_login_password'].type.settings
        self.assertCountEqual(settings['options_list'], ['--admin-password', '--administrator-login-password'])
        parser = ArgumentParser()
        parser.add_argument(*settings['options_list'], dest='administrator_login_password',
                            nargs=settings['nargs'], action=settings['action'])
        return vars(parser.parse_args([option, *values]))

    def test_no_wait_put_and_sparse_patch(self):
        self.client.send_request.return_value = self.response(202, None)
        for verb, options, expected in [
                ('create', {'state': 'Enabled', 'administrator_login': 'dbadmin'},
                 {'state': 'Enabled', 'administratorLogin': 'dbadmin', 'administratorLoginPassword': self.secret}),
                ('update', {}, {'administratorLoginPassword': self.secret}),
                ('update', {'state': 'Enabled'}, {'state': 'Enabled', 'administratorLoginPassword': self.secret}),
                ('update', {'state': 'Disabled'}, {'state': 'Disabled'})]:
            with self.subTest(verb=verb, state=options.get('state')):
                name = 'password ' + verb
                if 'administratorLoginPassword' in expected:
                    option = '--administrator-login-password' if verb == 'create' else '--admin-password'
                    options.update(self.password_argument(self.commands[name], self.secret, option=option))
                self.assertIsNone(self.run_command(name, no_wait=True, **options))
                request = self.client.send_request.call_args.kwargs['request']
                self.assertEqual((request.method, request.url), (
                    'PUT' if verb == 'create' else 'PATCH', self.url + '/passwordMethod' + self.query))
                self.assertEqual(json.loads(request.body), {'properties': expected})
                self.assertFalse(self.client.send_request.call_args.kwargs['logging_enable'])
                self.assertTrue(self.client.build_lro_polling.call_args.args[0])
                self.client.build_lro_polling.return_value.run.assert_not_called()

    def test_wait_polls_password_method(self):
        pending = {'properties': {'provisioningState': 'Updating'}}
        self.client.send_request.side_effect = [self.response(200, pending), self.response(200, self.method)]
        with patch('time.sleep') as sleep:
            result = self.run_command('password wait', updated=True, created=False, exists=False, deleted=False,
                                      custom=None, interval=1, timeout=2)
        self.assertIsNone(result)
        sleep.assert_called_once_with(1)
        for call in self.client.send_request.call_args_list:
            self.assertEqual(call.kwargs['request'].url, self.url + '/passwordMethod' + self.query)

    def test_prompt_is_confirmed_and_optional(self):
        self.client.send_request.return_value = self.response(202, None)
        with patch('azure.cli.core.aaz._prompt.prompt_pass', return_value=self.secret) as prompt:
            self.run_command('password update', state='Disabled', no_wait=True)
            prompt.assert_not_called()
            options = self.password_argument(self.commands['password update'])
            self.run_command('password update', no_wait=True, **options)
            self.assertTrue(prompt.call_args.kwargs['confirm'])
            request = self.client.send_request.call_args.kwargs['request']
            self.assertEqual(json.loads(request.body)['properties']['administratorLoginPassword'], self.secret)
            prompt.side_effect = NoTTYException
            with self.assertRaisesRegex(ValueError, 'non-interactive'):
                self.run_command('password update', no_wait=True, **options)

    def test_validation_does_not_echo_password_or_contact_service(self):
        for verb in ['create', 'update']:
            with self.subTest(verb=verb):
                for invalid in [self.secret[:7], self.secret * 4]:
                    with self.assertRaises(InvalidArgumentValueError) as error:
                        self.run_command('password ' + verb, state='Enabled', administrator_login_password=invalid)
                    self.assertNotIn(invalid, str(error.exception))
                with self.assertRaisesRegex(InvalidArgumentValueError, '--state'):
                    self.run_command('password ' + verb, state='Disabled', administrator_login_password=self.secret,
                                     no_wait=True)
        self.client.send_request.assert_not_called()

    def test_completed_write_returns_safe_resource_with_or_without_final_body(self):
        for verb, body in [('create', self.method), ('update', None)]:
            with self.subTest(verb=verb):
                self.client.send_request.side_effect = [self.response(202, None), self.response(200, self.method)]

                def build_polling(_no_wait, _session, callback, *_args, final_body=body, **_kwargs):
                    poller = Mock()
                    if final_body:
                        poller.resource.side_effect = lambda: callback(self.response(200, final_body))
                    return poller

                self.client.build_lro_polling.side_effect = build_polling
                result = self.run_command('password ' + verb, state='Enabled').result()
                self.assertEqual(result['properties']['provisioningState'], 'Succeeded')
                self.assertNotIn(self.secret, str(result))
                self.assertEqual(self.client.send_request.call_count, 1 if body else 2)
                self.client.send_request.reset_mock()
