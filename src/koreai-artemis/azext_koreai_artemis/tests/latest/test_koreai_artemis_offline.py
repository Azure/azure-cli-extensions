# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Offline request/polling tests.

The HTTP transport is replaced with an in-memory fake, so these tests exercise request
construction, long-running-operation polling and `--no-wait` without Azure resources.
"""

import copy
import json
from unittest import mock
from urllib.parse import urlparse, parse_qs

import requests
from azure.core.pipeline.transport import RequestsTransport, RequestsTransportResponse
from azure.cli.testsdk import ScenarioTest

SUB = '00000000-0000-0000-0000-000000000000'
RG = 'contoso-rg'
ORG = 'contoso-org'
WS = 'contoso-prod'
ARM = 'https://management.azure.com'
ORG_PATH = f'/subscriptions/{SUB}/resourceGroups/{RG}/providers/Kore.AgentPlatform/organizations/{ORG}'
WS_PATH = f'{ORG_PATH}/workspaces/{WS}'
OPERATION_PATH = f'/subscriptions/{SUB}/providers/Kore.AgentPlatform/operations/op1'

ORG_BODY = {
    'id': ORG_PATH,
    'name': ORG,
    'type': 'Kore.AgentPlatform/organizations',
    'location': 'eastus2euap',
    'tags': {'environment': 'production'},
    'properties': {
        'provisioningState': 'Succeeded',
        'partnerProperties': {
            'organizationName': 'Contoso AI Platform',
            'billingEmail': 'billing@contoso.com',
            'ownerEmail': 'admin@contoso.com',
            'defaultWorkspace': {
                'name': 'Default',
                'product': 'aiforwork',
                'marketplaceDetails': [{
                    'saaSResourceId': 'saas-1',
                    'offerDetails': {'publisherId': 'kore-ai', 'offerId': 'kore-offer'},
                }],
            },
        },
        'user': {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'emailAddress': 'jane.doe@contoso.com',
            'upn': 'jane.doe@contoso.onmicrosoft.com',
            'phoneNumber': '+1-425-555-0100',
        },
        'companyDetails': {'companyName': 'Contoso Ltd.', 'country': 'US'},
    },
}

WS_BODY = {
    'id': WS_PATH,
    'name': WS,
    'type': 'Kore.AgentPlatform/organizations/workspaces',
    'properties': {
        'provisioningState': 'Succeeded',
        'partnerProperties': {'name': 'Contoso Production', 'ownerEmail': 'owner@contoso.com'},
        'product': 'aiforwork',
    },
}


class FakeArm:
    """Routes requests by (method, path) and records everything that was sent."""

    def __init__(self):
        self.calls = []
        self.routes = {}

    def route(self, method, path, status, body=None, headers=None):
        self.routes[(method, path)] = (status, body, headers or {})

    def send(self, transport_self, request, **kwargs):  # pylint: disable=unused-argument
        parsed = urlparse(request.url)
        body = json.loads(request.body) if request.body else None
        self.calls.append((request.method, parsed.path, parse_qs(parsed.query), body))
        status, payload, headers = self.routes[(request.method, parsed.path)]
        response = requests.Response()
        response.status_code = status
        response.headers.update(headers)
        response.headers['Content-Type'] = 'application/json'
        response._content = json.dumps(payload).encode() if payload is not None else b''  # pylint: disable=protected-access
        return RequestsTransportResponse(request, response)

    def methods(self):
        return [(method, path) for method, path, _, _ in self.calls]

    def body_of(self, method, path):
        return next(body for m, p, _, body in self.calls if (m, p) == (method, path))


class KoreaiArtemisOfflineScenario(ScenarioTest):
    def setUp(self):
        super().setUp()
        self.arm = FakeArm()
        patches = [
            mock.patch.object(RequestsTransport, 'send', lambda s, r, **kw: self.arm.send(s, r, **kw)),
            mock.patch('azure.cli.core.aaz._http_policy.AAZBearerTokenCredentialPolicy.on_request',
                       lambda *args, **kwargs: None),
            mock.patch('time.sleep', lambda *args, **kwargs: None),
            mock.patch('azure.cli.core._profile.Profile.get_login_credentials',
                       lambda *args, **kwargs: (mock.MagicMock(), SUB, SUB)),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def invoke(self, command):
        # Commands contain literal shorthand-syntax braces, which self.cmd would treat as format fields.
        return self.cmd(command.replace('{', '{{').replace('}', '}}'))

    def _async_put(self, path, final_body):
        poll = f'{ARM}{OPERATION_PATH}'
        self.arm.route('PUT', path, 201, dict(final_body, properties=dict(
            final_body['properties'], provisioningState='Accepted')), {'Azure-AsyncOperation': poll})
        self.arm.route('GET', OPERATION_PATH, 200, {'status': 'Succeeded'})
        self.arm.route('GET', path, 200, final_body)

    def test_organization_create_waits_for_completion(self):
        self._async_put(ORG_PATH, ORG_BODY)
        result = self.invoke(
            f'koreai artemis organization create -g {RG} -n {ORG} -l eastus2euap --subscription {SUB} '
            '--partner-properties "{organization-name:\'Contoso AI Platform\',billing-email:billing@contoso.com,'
            'owner-email:admin@contoso.com,default-workspace:{name:Default,product:aiforwork,marketplace-details:[{saas-resource-id:saas-1,offer-details:{publisher-id:kore-ai,offer-id:kore-offer}}]}}" '
            '--user "{first-name:Jane,last-name:Doe,email-address:jane.doe@contoso.com,'
            'upn:jane.doe@contoso.onmicrosoft.com,phone-number:+1-425-555-0100}"').get_output_in_json()

        self.assertEqual(result['properties']['provisioningState'], 'Succeeded')
        self.assertEqual(self.arm.methods(), [
            ('PUT', ORG_PATH), ('GET', OPERATION_PATH), ('GET', ORG_PATH)])
        sent = self.arm.body_of('PUT', ORG_PATH)
        self.assertEqual(sent['location'], 'eastus2euap')
        self.assertEqual(sent['properties']['partnerProperties']['billingEmail'], 'billing@contoso.com')
        self.assertEqual(sent['properties']['user']['upn'], 'jane.doe@contoso.onmicrosoft.com')

    def test_organization_create_no_wait_does_not_poll(self):
        self._async_put(ORG_PATH, ORG_BODY)
        self.invoke(
            f'koreai artemis organization create -g {RG} -n {ORG} -l eastus2euap --subscription {SUB} --no-wait '
            '--partner-properties "{organization-name:Contoso,billing-email:b@contoso.com,owner-email:o@contoso.com,default-workspace:{name:Default,product:aiforwork,marketplace-details:[{saas-resource-id:saas-1,offer-details:{publisher-id:kore-ai,offer-id:kore-offer}}]}}" '
            '--user "{first-name:Jane,last-name:Doe,email-address:j@contoso.com,upn:j@contoso.com,'
            'phone-number:+1-425-555-0100}"')

        self.assertEqual(self.arm.methods(), [('PUT', ORG_PATH)])

    def test_organization_show_and_list(self):
        self.arm.route('GET', ORG_PATH, 200, ORG_BODY)
        self.arm.route('GET', f'/subscriptions/{SUB}/providers/Kore.AgentPlatform/organizations',
                       200, {'value': [ORG_BODY]})
        self.arm.route('GET', f'/subscriptions/{SUB}/resourceGroups/{RG}/providers/Kore.AgentPlatform/organizations',
                       200, {'value': [ORG_BODY]})

        shown = self.invoke(f'koreai artemis organization show -g {RG} -n {ORG} --subscription {SUB}').get_output_in_json()
        self.assertEqual(shown['name'], ORG)
        self.assertEqual(len(self.invoke(f'koreai artemis organization list --subscription {SUB}').get_output_in_json()), 1)
        self.assertEqual(
            len(self.invoke(f'koreai artemis organization list -g {RG} --subscription {SUB}').get_output_in_json()), 1)
        for _, _, query, _ in self.arm.calls:
            self.assertEqual(query['api-version'], ['2026-07-01-preview'])

    def test_organization_update_preserves_existing_configuration(self):
        self._async_put(ORG_PATH, ORG_BODY)
        updated = copy.deepcopy(ORG_BODY)
        updated['properties']['partnerProperties']['billingEmail'] = 'new-billing@contoso.com'
        self.arm.route('GET', ORG_PATH, 200, ORG_BODY)

        self.invoke(f'koreai artemis organization update -g {RG} -n {ORG} --subscription {SUB} '
                 '--partner-properties billing-email=new-billing@contoso.com')

        self.assertEqual(self.arm.methods()[:2], [('GET', ORG_PATH), ('PUT', ORG_PATH)])
        sent = self.arm.body_of('PUT', ORG_PATH)
        self.assertEqual(sent['properties']['partnerProperties']['billingEmail'], 'new-billing@contoso.com')
        # Everything that was not part of the update must be sent back unchanged.
        self.assertEqual(sent['properties']['partnerProperties']['ownerEmail'], 'admin@contoso.com')
        self.assertEqual(sent['properties']['partnerProperties']['organizationName'], 'Contoso AI Platform')
        self.assertEqual(sent['properties']['user'], ORG_BODY['properties']['user'])
        self.assertEqual(sent['properties']['companyDetails'], ORG_BODY['properties']['companyDetails'])
        self.assertEqual(sent['tags'], {'environment': 'production'})
        self.assertEqual(updated['properties']['partnerProperties']['ownerEmail'], 'admin@contoso.com')

    def test_organization_delete_polls_location(self):
        poll = f'{ARM}{OPERATION_PATH}'
        self.arm.route('DELETE', ORG_PATH, 202, None, {'Location': poll})
        self.arm.route('GET', OPERATION_PATH, 204)

        self.invoke(f'koreai artemis organization delete -g {RG} -n {ORG} --subscription {SUB} -y')

        self.assertEqual(self.arm.methods(), [('DELETE', ORG_PATH), ('GET', OPERATION_PATH)])

    def test_workspace_create_show_list_delete(self):
        self._async_put(WS_PATH, WS_BODY)
        self.arm.route('GET', f'{ORG_PATH}/workspaces', 200, {'value': [WS_BODY]})
        self.invoke(
            f'koreai artemis organization workspace create -g {RG} --organization-name {ORG} -n {WS} '
            f'--subscription {SUB} --product aiforwork '
            '--partner-properties "{name:\'Contoso Production\',owner-email:owner@contoso.com}"')
        sent = self.arm.body_of('PUT', WS_PATH)
        self.assertEqual(sent['properties']['product'], 'aiforwork')
        self.assertEqual(sent['properties']['partnerProperties']['ownerEmail'], 'owner@contoso.com')

        shown = self.invoke(
            f'koreai artemis organization workspace show -g {RG} --organization-name {ORG} -n {WS} '
            f'--subscription {SUB}').get_output_in_json()
        self.assertEqual(shown['name'], WS)
        listed = self.invoke(
            f'koreai artemis organization workspace list -g {RG} --organization-name {ORG} '
            f'--subscription {SUB}').get_output_in_json()
        self.assertEqual(len(listed), 1)

        poll = f'{ARM}{OPERATION_PATH}'
        self.arm.route('DELETE', WS_PATH, 202, None, {'Location': poll})
        self.arm.route('GET', OPERATION_PATH, 204)
        self.invoke(f'koreai artemis organization workspace delete -g {RG} --organization-name {ORG} -n {WS} '
                 f'--subscription {SUB} -y')
        self.assertIn(('DELETE', WS_PATH), self.arm.methods())

    def test_activate_saas_async_and_no_wait(self):
        path = f'/subscriptions/{SUB}/providers/Kore.AgentPlatform/activateSaaS'
        poll = f'{ARM}{OPERATION_PATH}'
        self.arm.route('POST', path, 202, None, {'Location': poll})
        self.arm.route('GET', OPERATION_PATH, 200, {'status': 'Succeeded'})
        command = f'koreai artemis saas activate --subscription {SUB} --publisher-id kore-ai --saas-guid {SUB}'

        self.invoke(command)
        self.assertEqual(self.arm.methods(), [('POST', path), ('GET', OPERATION_PATH)])
        self.assertEqual(self.arm.body_of('POST', path), {'publisherId': 'kore-ai', 'saasGuid': SUB})

        self.arm.calls.clear()
        self.invoke(f'{command} --no-wait')
        self.assertEqual(self.arm.methods(), [('POST', path)])

    def test_link_saas_async_and_no_wait(self):
        path = f'{WS_PATH}/linkSaaS'
        poll = f'{ARM}{OPERATION_PATH}'
        saas_id = (f'/subscriptions/{SUB}/resourceGroups/{RG}/providers/Microsoft.SaaS/resources/kore-ai-saas-1')
        self.arm.route('POST', path, 202, None, {'Location': poll})
        self.arm.route('GET', OPERATION_PATH, 204)
        command = (f'koreai artemis organization workspace saas link -g {RG} --organization-name {ORG} '
                   f'--workspace-name {WS} --subscription {SUB} --saas-resource-ids {saas_id}')

        self.invoke(command)
        self.assertEqual(self.arm.methods(), [('POST', path), ('GET', OPERATION_PATH)])
        self.assertEqual(self.arm.body_of('POST', path), {'saaSResourceIds': [saas_id]})

        self.arm.calls.clear()
        self.invoke(f'{command} --no-wait')
        self.assertEqual(self.arm.methods(), [('POST', path)])
