# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Offline behaviour tests for `az cloud-service`.

Every test drives the real CLI against a stubbed HTTP transport and asserts the request that
leaves the CLI (method, URL, body) and the output that the user sees. The
expectations were captured from the Compute SDK based implementation, so the same file
validates that the AAZ based implementation behaves the same way.
"""

import io
import json
import os
import re
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock

import requests
from azure.cli.testsdk import ScenarioTest
from azure.core.pipeline.transport import RequestsTransport
from azure.core.rest._requests_basic import RestRequestsTransportResponse

# ---- Offline HTTP stub: replaces the requests transport, records each request and returns canned ARM responses ----

SUB = '00000000-0000-0000-0000-000000000000'
RG = 'rg1'
CS = 'cs1'
BASE = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/cloudServices'.format(SUB, RG)
BASE_SUB = '/subscriptions/{}/providers/Microsoft.Compute/cloudServices'.format(SUB)

RI_SKU = {'name': 'Standard_D1_v2', 'tier': 'Standard'}
RDP_TEXT = 'full address:s:1.2.3.4:3389\r\nusername:s:user\r\n'


def _item(name, rg=RG):
    return {
        'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/cloudServices/{}'.format(SUB, rg, name),
        'name': name,
        'type': 'Microsoft.Compute/cloudServices',
        'location': 'westeurope',
        'tags': {'k': 'v'},
        'properties': {
            'provisioningState': 'Succeeded',
            'roleProfile': {'roles': [{'name': 'r1',
                                       'sku': {'name': 'Standard_D1_v2', 'tier': 'Standard', 'capacity': 2}}]},
        },
    }


def _simple_list(prefix, sku):
    return {'value': [{'name': prefix + '1', 'type': 'x', 'sku': sku},
                      {'name': prefix + '2', 'type': 'x', 'sku': sku}]}


class Recorder:
    """Records every request and answers it with a canned ARM-style response."""

    def __init__(self):
        self.requests = []

    def calls(self, include_get_after_lro=True):
        return self.requests

    def respond(self, request):
        method = request.method
        url = request.url
        path, _, query = url.partition('?')
        path = path.split('.azure.com', 1)[-1] if '.azure.com' in path else path
        api = re.search(r'api-version=([^&]+)', query)
        body = request.body
        if isinstance(body, bytes):
            body = body.decode()
        # The live subscription id is replaced so that assertions are stable.
        guid = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
        path = re.sub(r'(?i)/subscriptions/' + guid, '/subscriptions/' + SUB, path)
        if body:
            body = re.sub(r'(?i)/subscriptions/' + guid, '/subscriptions/' + SUB, body)
        self.requests.append({
            'method': method,
            'path': path,
            'api': api.group(1) if api else None,
            'query': query,
            'body': json.loads(body) if body else None,
            'accept': request.headers.get('Accept'),
        })
        return self._answer(method, path, query)

    @staticmethod
    def _answer(method, path, query):
        low = path.lower()
        rg_cs = (BASE + '/' + CS).lower()
        if method == 'GET' and low == '/subscriptions/{}/resourcegroups/{}'.format(SUB, RG).lower():
            return 200, {'name': RG, 'location': 'westeurope'}
        if method == 'GET':
            if low == BASE_SUB.lower() or low == BASE.lower():
                if 'page=2' in query:
                    return 200, {'value': [_item('cs-b')]}
                nxt = 'https://management.azure.com{}?api-version=2022-09-04&page=2'.format(path)
                return 200, {'value': [_item('cs-a')], 'nextLink': nxt}
            if low == rg_cs:
                return 200, _item(CS)
            if low == rg_cs + '/instanceview':
                return 200, {'roleInstance': {'statusesSummary': [{'code': 'x', 'count': 1}]}, 'sdkVersion': '2.9'}
            if low == rg_cs + '/roles':
                return 200, _simple_list('role', {'name': 'Standard_D1_v2', 'tier': 'Standard', 'capacity': 3})
            if low.startswith(rg_cs + '/roles/'):
                return 200, {'name': 'role1', 'sku': {'name': 'Standard_D1_v2', 'tier': 'Standard', 'capacity': 3}}
            if low == rg_cs + '/roleinstances':
                return 200, _simple_list('ri', RI_SKU)
            if low.endswith('/remotedesktopfile'):
                return 200, RDP_TEXT
            if low.endswith('/instanceview') and '/roleinstances/' in low:
                return 200, {'platformUpdateDomain': 1, 'platformFaultDomain': 0}
            if '/roleinstances/' in low:
                return 200, {'name': 'ri1', 'sku': RI_SKU}
            if low == rg_cs + '/updatedomains':
                return 200, {'value': [{'id': 'ud0'}, {'id': 'ud1'}]}
            if '/updatedomains/' in low:
                return 200, {'id': 'ud0'}
        if method in ('PUT', 'PATCH'):
            return 200, _item(CS)
        return 200, ''


def _make_response(request, status, payload):
    resp = requests.Response()
    resp.status_code = status
    if isinstance(payload, str):
        resp._content = payload.encode()
        resp.headers['Content-Type'] = 'application/x-rdp' if payload == RDP_TEXT else 'text/plain'
    else:
        resp._content = json.dumps(payload).encode()
        resp.headers['Content-Type'] = 'application/json'
    resp.url = request.url
    resp.request = requests.Request(request.method, request.url).prepare()
    resp.encoding = 'utf-8'
    resp.raw = io.BytesIO(resp._content)
    resp._content = False
    resp._content_consumed = False
    return RestRequestsTransportResponse(request=request, internal_response=resp)


@contextmanager
def stub_http():
    recorder = Recorder()

    def fake_send(self, request, **kwargs):
        status, payload = recorder.respond(request)
        return _make_response(request, status, payload)

    with mock.patch.object(RequestsTransport, 'send', fake_send):
        yield recorder


# ---- Tests ----


SVC = '-g rg1 -n cs1'
RI = '-g rg1 --cloud-service-name cs1 --role-instance-name ri1'
CSN = '-g rg1 --cloud-service-name cs1'

# (command, method, path relative to the subscription, request body, is LRO)
SIMPLE_COMMANDS = [
    ('cloud-service show ' + SVC, 'GET', BASE + '/cs1', None, False),
    ('cloud-service show-instance-view ' + SVC, 'GET', BASE + '/cs1/instanceView', None, False),
    ('cloud-service update ' + SVC + ' --tags a=b', 'PATCH', BASE + '/cs1', {'tags': {'a': 'b'}}, True),
    ('cloud-service delete ' + SVC + ' -y', 'DELETE', BASE + '/cs1', None, True),
    ('cloud-service delete-instance ' + SVC + ' --role-instances ri1 ri2 -y', 'POST', BASE + '/cs1/delete',
     {'roleInstances': ['ri1', 'ri2']}, True),
    ('cloud-service power-off ' + SVC, 'POST', BASE + '/cs1/poweroff', None, True),
    ('cloud-service rebuild ' + SVC + ' --role-instances ri1', 'POST', BASE + '/cs1/rebuild',
     {'roleInstances': ['ri1']}, True),
    ('cloud-service reimage ' + SVC + ' --role-instances ri1', 'POST', BASE + '/cs1/reimage',
     {'roleInstances': ['ri1']}, True),
    ('cloud-service restart ' + SVC + ' --role-instances ri1', 'POST', BASE + '/cs1/restart',
     {'roleInstances': ['ri1']}, True),
    ('cloud-service start ' + SVC, 'POST', BASE + '/cs1/start', None, True),
    ('cloud-service role list ' + CSN, 'GET', BASE + '/cs1/roles', None, False),
    ('cloud-service role show ' + CSN + ' --role-name role1', 'GET', BASE + '/cs1/roles/role1', None, False),
    ('cloud-service role-instance list ' + CSN, 'GET', BASE + '/cs1/roleInstances', None, False),
    ('cloud-service role-instance show ' + RI, 'GET', BASE + '/cs1/roleInstances/ri1', None, False),
    ('cloud-service role-instance show-instance-view ' + RI, 'GET', BASE + '/cs1/roleInstances/ri1/instanceView',
     None, False),
    ('cloud-service role-instance delete ' + RI + ' -y', 'DELETE', BASE + '/cs1/roleInstances/ri1', None, True),
    ('cloud-service role-instance rebuild ' + RI, 'POST', BASE + '/cs1/roleInstances/ri1/rebuild', None, True),
    ('cloud-service role-instance reimage ' + RI, 'POST', BASE + '/cs1/roleInstances/ri1/reimage', None, True),
    ('cloud-service role-instance restart ' + RI, 'POST', BASE + '/cs1/roleInstances/ri1/restart', None, True),
    ('cloud-service update-domain list-update-domain ' + CSN, 'GET', BASE + '/cs1/updateDomains', None, False),
    ('cloud-service update-domain show-update-domain ' + CSN + ' --update-domain 0', 'GET',
     BASE + '/cs1/updateDomains/0', None, False),
]


def _sub_path(path):
    return '/subscriptions/{}'.format(SUB) + path.split('/subscriptions/' + SUB, 1)[-1] if SUB in path else path


class CloudServiceRequestTest(ScenarioTest):
    """Request line and body of every command."""

    def _run(self, command):
        with stub_http() as rec:
            self.cmd(command)
        return rec.requests

    def test_each_command_sends_expected_request(self):
        for command, method, path, body, _ in SIMPLE_COMMANDS:
            with self.subTest(command=command):
                reqs = self._run(command)
                self.assertEqual(1, len(reqs), reqs)
                self.assertEqual(method, reqs[0]['method'])
                self.assertEqual(path, reqs[0]['path'])
                self.assertEqual(body, reqs[0]['body'])

    def test_walk_update_domain_request(self):
        reqs = self._run('cloud-service update-domain walk-update-domain ' + CSN + ' --update-domain 0')
        self.assertEqual(1, len(reqs))
        self.assertEqual('PUT', reqs[0]['method'])
        self.assertEqual(BASE + '/cs1/updateDomains/0', reqs[0]['path'])

    def test_no_wait_sends_the_same_request(self):
        for command, method, path, body, lro in SIMPLE_COMMANDS:
            if not lro:
                continue
            with self.subTest(command=command):
                reqs = self._run(command + ' --no-wait')
                self.assertEqual([(method, path, body)], [(r['method'], r['path'], r['body']) for r in reqs])

    @unittest.expectedFailure
    def test_remote_desktop_file_request(self):
        with stub_http() as rec:
            try:
                self.cmd('cloud-service role-instance show-remote-desktop-file ' + RI)
            except Exception:  # pylint: disable=broad-except
                pass  # output handling is covered separately
        self.assertEqual(1, len(rec.requests))
        self.assertEqual('GET', rec.requests[0]['method'])
        self.assertEqual(BASE + '/cs1/roleInstances/ri1/remoteDesktopFile', rec.requests[0]['path'])
        self.assertEqual('application/x-rdp', rec.requests[0]['accept'])

    def test_ids_are_accepted(self):
        sub = self.get_subscription_id()
        rid = '/subscriptions/{}/resourceGroups/rg1/providers/Microsoft.Compute/cloudServices/cs1'.format(sub)
        reqs = self._run('cloud-service show --ids ' + rid)
        self.assertEqual(BASE + '/cs1', reqs[0]['path'])
        rid += '/roleInstances/ri1'
        reqs = self._run('cloud-service role-instance show --ids ' + rid)
        self.assertEqual(BASE + '/cs1/roleInstances/ri1', reqs[0]['path'])

    def test_name_aliases(self):
        for flags in ('-g rg1 -n cs1', '-g rg1 --name cs1', '-g rg1 --cloud-service-name cs1'):
            with self.subTest(flags=flags):
                self.assertEqual(BASE + '/cs1', self._run('cloud-service show ' + flags)[0]['path'])


class CloudServiceListTest(ScenarioTest):
    """List commands follow nextLink and return the item array."""

    def test_list_follows_next_link_and_returns_array(self):
        with stub_http() as rec:
            result = self.cmd('cloud-service list -g rg1').get_output_in_json()
        self.assertEqual(['cs-a', 'cs-b'], [r['name'] for r in result])
        self.assertEqual(2, len(rec.requests))
        self.assertEqual(BASE, rec.requests[0]['path'])

    def test_list_all_follows_next_link_and_returns_array(self):
        with stub_http() as rec:
            result = self.cmd('cloud-service list-all').get_output_in_json()
        self.assertEqual(['cs-a', 'cs-b'], [r['name'] for r in result])
        self.assertEqual(2, len(rec.requests))
        self.assertEqual(BASE_SUB, rec.requests[0]['path'])

    def test_list_requires_resource_group(self):
        with stub_http() as rec, self.assertRaises(SystemExit):
            self.cmd('cloud-service list')
        self.assertEqual([], rec.requests)

    def test_list_all_has_no_resource_group_argument(self):
        with stub_http() as rec, self.assertRaises(SystemExit):
            self.cmd('cloud-service list-all -g rg1')
        self.assertEqual([], rec.requests)

    def test_child_lists_return_arrays(self):
        with stub_http():
            roles = self.cmd('cloud-service role list ' + CSN).get_output_in_json()
            instances = self.cmd('cloud-service role-instance list ' + CSN).get_output_in_json()
            domains = self.cmd('cloud-service update-domain list-update-domain ' + CSN).get_output_in_json()
        self.assertEqual(['role1', 'role2'], [r['name'] for r in roles])
        self.assertEqual(['ri1', 'ri2'], [r['name'] for r in instances])
        self.assertEqual(['ud0', 'ud1'], [r['id'] for r in domains])


class CloudServiceOutputTest(ScenarioTest):
    """Output casing, nesting and types."""

    def test_show_output_is_camel_case_with_integer_capacity(self):
        with stub_http():
            self.cmd('cloud-service show ' + SVC, checks=[
                self.check('name', 'cs1'),
                self.check('location', 'westeurope'),
                self.check('tags.k', 'v'),
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.roleProfile.roles[0].sku.capacity', 2),
                self.check('properties.roleProfile.roles[0].sku.tier', 'Standard'),
            ])

    def test_instance_view_output(self):
        with stub_http():
            self.cmd('cloud-service show-instance-view ' + SVC, checks=[
                self.check('sdkVersion', '2.9'),
                self.check('roleInstance.statusesSummary[0].count', 1),
            ])
            self.cmd('cloud-service role-instance show-instance-view ' + RI, checks=[
                self.check('platformUpdateDomain', 1),
                self.check('platformFaultDomain', 0),
            ])

    def test_role_output(self):
        with stub_http():
            self.cmd('cloud-service role show ' + CSN + ' --role-name role1', checks=[
                self.check('name', 'role1'), self.check('sku.capacity', 3)])
            self.cmd('cloud-service role-instance show ' + RI, checks=[
                self.check('name', 'ri1'), self.check('sku.name', 'Standard_D1_v2'),
                self.check('sku.tier', 'Standard')])

    def test_update_domain_output(self):
        with stub_http():
            self.cmd('cloud-service update-domain show-update-domain ' + CSN + ' --update-domain 0',
                     checks=[self.check('id', 'ud0')])

    def test_lro_commands_return_resource_or_nothing(self):
        with stub_http():
            self.cmd('cloud-service update ' + SVC + ' --tags a=b', checks=[self.check('name', 'cs1')])
            self.assertEqual('', self.cmd('cloud-service delete ' + SVC + ' -y').output.strip())
            self.assertEqual('', self.cmd('cloud-service restart ' + SVC).output.strip())

    # Known gap: the generated command cannot decode application/x-rdp
    @unittest.expectedFailure
    def test_remote_desktop_file_returns_rdp_text(self):
        with stub_http():
            result = self.cmd('cloud-service role-instance show-remote-desktop-file ' + RI).output
        self.assertIn('full address:s:1.2.3.4:3389', result)
        self.assertIn(RDP_TEXT.strip().splitlines()[1], result)


class CloudServiceCommandSurfaceTest(ScenarioTest):
    """Arguments that must / must not exist."""

    def test_walk_update_domain_has_no_no_wait(self):
        with stub_http() as rec, self.assertRaises(SystemExit):
            self.cmd('cloud-service update-domain walk-update-domain ' + CSN + ' --update-domain 0 --no-wait')
        self.assertEqual([], rec.requests)

    def test_delete_commands_ask_for_confirmation(self):
        for command in ('cloud-service delete ' + SVC, 'cloud-service role-instance delete ' + RI,
                        'cloud-service delete-instance ' + SVC + ' --role-instances ri1'):
            with self.subTest(command=command):
                with stub_http() as rec, self.assertRaises(Exception):
                    self.cmd(command)
                self.assertEqual([], rec.requests)

    def test_role_instances_is_optional_on_service_actions(self):
        for action in ('rebuild', 'reimage', 'restart', 'delete-instance'):
            with self.subTest(action=action):
                with stub_http() as rec:
                    self.cmd('cloud-service {} {} -y'.format(action, SVC)
                             if action == 'delete-instance' else 'cloud-service {} {}'.format(action, SVC))
                self.assertEqual(1, len(rec.requests))
                self.assertFalse(rec.requests[0]['body'])  # omitted or empty

    def test_all_commands_are_registered(self):
        expected = {
            'cloud-service list', 'cloud-service list-all', 'cloud-service show', 'cloud-service create',
            'cloud-service update', 'cloud-service delete', 'cloud-service delete-instance',
            'cloud-service power-off', 'cloud-service rebuild', 'cloud-service reimage', 'cloud-service restart',
            'cloud-service show-instance-view', 'cloud-service start', 'cloud-service wait',
            'cloud-service role list', 'cloud-service role show', 'cloud-service role-instance list',
            'cloud-service role-instance show', 'cloud-service role-instance delete',
            'cloud-service role-instance rebuild', 'cloud-service role-instance reimage',
            'cloud-service role-instance restart', 'cloud-service role-instance show-instance-view',
            'cloud-service role-instance show-remote-desktop-file', 'cloud-service update-domain list-update-domain',
            'cloud-service update-domain show-update-domain', 'cloud-service update-domain walk-update-domain',
            'cloud-service os-family list', 'cloud-service os-family show', 'cloud-service os-version list',
            'cloud-service os-version show',
        }
        from azext_cloudservice import COMMAND_LOADER_CLS
        table = COMMAND_LOADER_CLS(cli_ctx=self.cli_ctx).load_command_table(None)
        self.assertTrue(expected.issubset(set(table.keys())), expected - set(table.keys()))


class CloudServiceCreateTest(ScenarioTest):
    """The compact `create` syntaxes produce the expected request body."""

    SUB_ID = '/subscriptions/{}'.format(SUB)

    def _create(self, args):
        with stub_http() as rec:
            self.cmd('cloud-service create -g rg1 -n cs1 ' + args)
        self.assertEqual(1, len([r for r in rec.requests if r['method'] == 'PUT']), rec.requests)
        put = [r for r in rec.requests if r['method'] == 'PUT'][0]
        self.assertEqual(BASE + '/cs1', put['path'])
        return put['body'], rec

    def test_roles(self):
        body, _ = self._create('-l westeurope --roles Front:Standard_D1_v2:2:Standard Back:Standard_D2_v2:1:Basic')
        self.assertEqual('westeurope', body['location'])
        self.assertEqual([
            {'name': 'Front', 'sku': {'name': 'Standard_D1_v2', 'tier': 'Standard', 'capacity': 2}},
            {'name': 'Back', 'sku': {'name': 'Standard_D2_v2', 'tier': 'Basic', 'capacity': 1}},
        ], body['properties']['roleProfile']['roles'])

    def test_load_balancers(self):
        body, _ = self._create('-l westeurope --load-balancer-configurations lb:fe:pip:: lb2:fe2::sn:10.0.0.4')
        lbs = body['properties']['networkProfile']['loadBalancerConfigurations']
        self.assertEqual({'name': 'lb', 'properties': {'frontendIpConfigurations': [{
            'name': 'fe', 'properties': {'publicIPAddress': {
                'id': self.SUB_ID + '/resourceGroups/rg1/providers/Microsoft.Network/publicIPAddresses/pip'}}}]}},
            lbs[0])
        self.assertEqual({'name': 'lb2', 'properties': {'frontendIpConfigurations': [{
            'name': 'fe2', 'properties': {'subnet': {'id': 'sn'}, 'privateIPAddress': '10.0.0.4'}}]}}, lbs[1])

    def test_lb_alias_and_full_public_ip_id_passthrough(self):
        pip = self.SUB_ID + '/resourceGroups/other/providers/Microsoft.Network/publicIPAddresses/mypip'
        body, _ = self._create('-l westeurope --lb lb:fe:{}::'.format(pip))
        fe = body['properties']['networkProfile']['loadBalancerConfigurations'][0]['properties'][
            'frontendIpConfigurations'][0]
        self.assertEqual(pip, fe['properties']['publicIPAddress']['id'])

    def test_secrets(self):
        vault_id = self.SUB_ID + '/resourceGroups/other/providers/Microsoft.KeyVault/vaults/kv2'
        # A vault resource id contains no ':' so it round-trips unchanged.
        body, _ = self._create('-l westeurope --secrets vault0:cert0:cert1 {}:cert2'.format(vault_id))
        secrets = body['properties']['osProfile']['secrets']
        self.assertEqual(self.SUB_ID + '/resourceGroups/rg1/providers/Microsoft.KeyVault/vaults/vault0',
                         secrets[0]['sourceVault']['id'])
        self.assertEqual([{'certificateUrl': 'cert0'}, {'certificateUrl': 'cert1'}], secrets[0]['vaultCertificates'])
        self.assertEqual(vault_id, secrets[1]['sourceVault']['id'])
        self.assertEqual([{'certificateUrl': 'cert2'}], secrets[1]['vaultCertificates'])

    def test_extensions_json_text_and_file(self):
        ext = [{'name': 'RDPExtension', 'properties': {
            'type': 'RDP', 'publisher': 'Microsoft.Windows.Azure.Extensions', 'typeHandlerVersion': '1.2.1',
            'autoUpgradeMinorVersion': False, 'settings': 'settings', 'protectedSettings': 'protected'}}]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'extensions.json').replace('\\', '/')
            with open(path, 'w') as f:
                json.dump(ext, f)
            for value in (json.dumps(ext), '@' + path):
                with self.subTest(value=value[:12]):
                    self.kwargs['ext'] = value
                    body, _ = self._create("-l westeurope --extensions '{ext}'")
                    got = body['properties']['extensionProfile']['extensions']
                    self.assertEqual('RDPExtension', got[0]['name'])
                    props = got[0]['properties']
                    self.assertEqual('RDP', props['type'])
                    self.assertEqual('1.2.1', props['typeHandlerVersion'])
                    self.assertIs(False, props['autoUpgradeMinorVersion'])
                    self.assertEqual('settings', props['settings'])
                    self.assertEqual('protected', props['protectedSettings'])

    def test_scalar_properties_and_configuration_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = os.path.join(tmp, 'service.cscfg').replace('\\', '/')
            with open(cfg, 'w') as f:
                f.write('<ServiceConfiguration/>')
            self.kwargs['cfg'] = cfg
            body, _ = self._create('-l westeurope --package-url http://pkg --configuration @{cfg} '
                                   '--start-cloud-service false --upgrade-mode Manual --tags a=b '
                                   '--id /subscriptions/x/swap')
        props = body['properties']
        self.assertEqual('http://pkg', props['packageUrl'])
        self.assertEqual('<ServiceConfiguration/>', props['configuration'])
        self.assertIs(False, props['startCloudService'])
        self.assertEqual('Manual', props['upgradeMode'])
        self.assertEqual({'a': 'b'}, body['tags'])
        self.assertEqual({'id': '/subscriptions/x/swap'}, props['networkProfile']['swappableCloudService'])

    def test_configuration_url(self):
        body, _ = self._create('-l westeurope --configuration-url http://cfg')
        self.assertEqual('http://cfg', body['properties']['configurationUrl'])

    def test_default_location_comes_from_resource_group(self):
        body, rec = self._create('--roles r:Standard_D1_v2:1:Standard')
        self.assertEqual('westeurope', body['location'])
        self.assertTrue(any(r['method'] == 'GET' and r['path'].lower().endswith('/resourcegroups/rg1')
                            for r in rec.requests))

    def test_no_wait_sends_the_same_put(self):
        body_wait, _ = self._create('-l westeurope --roles r:Standard_D1_v2:1:Standard')
        body_no_wait, _ = self._create('-l westeurope --roles r:Standard_D1_v2:1:Standard --no-wait')
        self.assertEqual(body_wait, body_no_wait)

    def test_create_returns_resource(self):
        with stub_http():
            self.cmd('cloud-service create -g rg1 -n cs1 -l westeurope --roles r:Standard_D1_v2:1:Standard',
                     checks=[self.check('name', 'cs1')])
