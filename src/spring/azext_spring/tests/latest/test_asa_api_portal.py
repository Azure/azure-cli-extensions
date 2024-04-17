# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import unittest
from azure.cli.testsdk import (ScenarioTest, record_only)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)
from azure.cli.testsdk.preparers import (
    RoleBasedServicePrincipalPreparer
)
from .common.test_utils import get_test_cmd
from .custom_preparers import SpringPreparer, SpringResourceGroupPreparer, SpringSubResourceWrapper
from .custom_dev_setting_constant import SpringTestEnvironmentEnum
from ...vendored_sdks.appplatform.v2024_05_01_preview import models
from ...api_portal import (api_portal_custom_domain_update, api_portal_custom_domain_unbind)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand

free_mock_client = mock.MagicMock()


# pylint: disable=line-too-long
# pylint: disable=too-many-lines

class ApiPortalWrapper(SpringSubResourceWrapper):
    def __init__(self,
                 resource_group_parameter_name='resource_group',
                 spring_parameter_name='spring'):
        super(ApiPortalWrapper, self).__init__()
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.spring_parameter_name = spring_parameter_name

    def create_resource(self, *_, **kwargs):
        self.resource_group = self._get_resource_group(**kwargs)
        self.spring = self._get_spring(**kwargs)

    def remove_resource(self, *_, **__):
        self.live_only_execute(self.cli_ctx,
                               'spring api-portal delete -g {}  -s {} --yes'.format(self.resource_group, self.spring))
        self.live_only_execute(self.cli_ctx,
                               'spring api-portal create -g {}  -s {}'.format(self.resource_group, self.spring))


@record_only()
class ApiPortalTest(ScenarioTest):

    @RoleBasedServicePrincipalPreparer()
    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.ENTERPRISE_WITH_TANZU['spring'])
    @ApiPortalWrapper()
    def test_api_portal(self, resource_group, spring, sp_name, sp_password):
        self.kwargs.update({
            'serviceName': spring,
            'rg': resource_group,
            'clientId': sp_name,
            'secret': sp_password
        })

        self.cmd('spring api-portal update -g {rg} -s {serviceName} '
                 '--assign-endpoint true --https-only true --instance-count 1 '
                 '--client-id {clientId} --client-secret {secret} --issuer-uri https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0 --scope "openid,profile,email"',
                 checks=[
                     self.check('properties.public', True),
                     self.check('properties.httpsOnly', True),
                     self.check('sku.capacity', 1),
                     self.check('properties.ssoProperties.clientId', "*"),
                     self.check('properties.ssoProperties.clientSecret', "*"),
                     self.check('properties.ssoProperties.issuerUri',
                                "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0"),
                     self.check('properties.ssoProperties.scope', ["openid", "profile", "email"]),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring api-portal show -g {rg} -s {serviceName}', checks=[
            self.check('properties.public', True),
            self.check('properties.httpsOnly', True),
            self.check('sku.capacity', 1),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring api-portal clear -g {rg} -s {serviceName}', checks=[
            self.check('properties.public', False),
            self.check('properties.httpsOnly', False),
            self.check('sku.capacity', 1),
            self.check('properties.provisioningState', "Succeeded")
        ])


def _get_basic_mock_client(*_):
    return mock.MagicMock()


class ApiPortalUnitTest(unittest.TestCase):

    def _execute(self, method, cmd, client, *kwargs):
        client = client or _get_basic_mock_client()
        method(cmd, client, *kwargs)
        self.custom_domain_request = client.api_portal_custom_domains.begin_create_or_update.call_args_list
        self.created_resource = self.created_alv_request[0][0][3] if self.created_alv_request else None
        self.dev_tool_portal_request = client.dev_tool_portals.begin_create_or_update.call_args_list
        self.dev_tool_portal = self.dev_tool_portal_request[0][0][3] if self.dev_tool_portal_request else None
        self.deleted = client.application_live_views.begin_delete.call_args_list is not None

    def test_custom_domain(self):
        client = _get_basic_mock_client()
        api_portal_custom_domain_update(get_test_cmd(),
                                        client,
                                        'rg',
                                        'asa',
                                        'my-domain.microsoft.com')
        args = client.api_portal_custom_domains.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))  # one call
        self.assertEqual(5, len(args[0][0]))  # 5 parameters
        self.assertEqual(('rg', 'asa', 'default', 'my-domain.microsoft.com'), args[0][0][0:4])
        resource = args[0][0][4]
        self.assertIsNone(resource.properties.thumbprint)

    def test_custom_domain_with_cert(self):
        def _get_cert(*_, **__):
            resp = models.CertificateResource(
                properties=models.CertificateProperties()
            )
            resp.properties.thumbprint = 'my-thumbprint'
            return resp

        client = _get_basic_mock_client()
        client.certificates.get = _get_cert
        api_portal_custom_domain_update(get_test_cmd(),
                                        client,
                                        'rg',
                                        'asa',
                                        'my-domain.microsoft.com',
                                        'my-cert')
        args = client.api_portal_custom_domains.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))  # one call
        self.assertEqual(5, len(args[0][0]))  # 5 parameters
        self.assertEqual(('rg', 'asa', 'default', 'my-domain.microsoft.com'), args[0][0][0:4])
        resource = args[0][0][4]
        self.assertEqual('my-thumbprint', resource.properties.thumbprint)

    def test_custom_domain_with_invalid_cert(self):
        def _get_cert(*_, **__):
            raise RuntimeError('error')

        client = _get_basic_mock_client()
        client.certificates.get = _get_cert
        self.assertRaises(RuntimeError,
                          api_portal_custom_domain_update,
                          get_test_cmd(),
                          client,
                          'rg',
                          'asa',
                          'my-domain.microsoft.com',
                          'my-cert')

    def test_custom_domain_unbind(self):
        client = _get_basic_mock_client()
        api_portal_custom_domain_unbind(get_test_cmd(),
                                        client,
                                        'rg',
                                        'asa',
                                        'my-domain.microsoft.com')
        args = client.api_portal_custom_domains.begin_delete.call_args_list
        self.assertEqual(1, len(args))  # one call
        self.assertEqual(4, len(args[0][0]))  # 5 parameters
        self.assertEqual(('rg', 'asa', 'default', 'my-domain.microsoft.com'), args[0][0])
