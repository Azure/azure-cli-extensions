
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest

from azure.cli.testsdk import JMESPathCheck
from azure.cli.testsdk import ScenarioTest
from .scenario_mixin import CdnScenarioMixin
from .config import fixture

from azext_cdn.vendored_sdks.models import SkuName


class CdnEndpointScenarioTest(CdnScenarioMixin, ScenarioTest):
    def test_endpoint_crud(self):
        resource_group, profile_name = self.classic_cdn_profile()

        endpoint_name = self.create_random_name(prefix='endpoint', length=24)
        
        name_exist_checks = [JMESPathCheck('reason', None),
                             JMESPathCheck('nameAvailable', True)]
        self.cmd(f"cdn name-exists --name {endpoint_name}", checks=name_exist_checks)

        origin = 'www.contoso.com'
        checks = [JMESPathCheck('name', endpoint_name),
                  JMESPathCheck('origins[0].hostName', origin),
                  JMESPathCheck('isHttpAllowed', True),
                  JMESPathCheck('isHttpsAllowed', True),
                  JMESPathCheck('isCompressionEnabled', False),
                  JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        self.endpoint_create_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 origin,
                                 checks=checks)
 
        name_exist_checks = [JMESPathCheck('reason', "Name is already in use"),
                             JMESPathCheck('nameAvailable', False)]
        self.cmd(f"cdn name-exists --name {endpoint_name}", checks=name_exist_checks)

        selected = f"[?name=='{endpoint_name}']"
        list_checks = [JMESPathCheck(f'length({selected})', 1),
                       JMESPathCheck(f'{selected} | [0].name', endpoint_name),
                       JMESPathCheck(f'{selected} | [0].origins[0].hostName', origin),
                       JMESPathCheck(f'{selected} | [0].isHttpAllowed', True),
                       JMESPathCheck(f'{selected} | [0].isHttpsAllowed', True),
                       JMESPathCheck(f'{selected} | [0].isCompressionEnabled', False),
                       JMESPathCheck(f'{selected} | [0].queryStringCachingBehavior', 'IgnoreQueryString')]
        self.endpoint_list_cmd(resource_group, profile_name, checks=list_checks)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', False),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', True),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        options = '--no-http --enable-compression'
        self.endpoint_update_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 options=options,
                                 checks=update_checks)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', False),
                         JMESPathCheck('isCompressionEnabled', False),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        options = '--no-http false --no-https --enable-compression false'
        self.endpoint_update_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 options=options,
                                 checks=update_checks)

        self.endpoint_delete_cmd(resource_group, endpoint_name, profile_name)

    def test_endpoint_compression(self):
        resource_group, profile_name = self.classic_cdn_profile()
        endpoint_name = self.create_random_name(prefix='endpoint', length=24)
        origin = 'www.contoso.com'
        create_options = '--enable-compression --content-types-to-compress text/plain text/html'
        checks = [JMESPathCheck('name', endpoint_name),
                  JMESPathCheck('origins[0].hostName', origin),
                  JMESPathCheck('isHttpAllowed', True),
                  JMESPathCheck('isHttpsAllowed', True),
                  JMESPathCheck('isCompressionEnabled', True),
                  JMESPathCheck('contentTypesToCompress[0]', "text/plain"),
                  JMESPathCheck('contentTypesToCompress[1]', "text/html"),
                  JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        self.endpoint_create_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 origin,
                                 checks=checks,
                                 options=create_options)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', True),
                         JMESPathCheck('contentTypesToCompress[0]', "application/json"),
                         JMESPathCheck('contentTypesToCompress[1]', "application/xml"),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        update_options = '--content-types-to-compress application/json application/xml'
        self.endpoint_update_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 options=update_options,
                                 checks=update_checks)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', False),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        update_options = '--enable-compression False'
        self.endpoint_update_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 options=update_options,
                                 checks=update_checks)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', True),
                         JMESPathCheck('contentTypesToCompress[0]', "text/javascript"),
                         JMESPathCheck('contentTypesToCompress[1]', "application/x-javascript"),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        update_options = '--enable-compression --content-types-to-compress text/javascript application/x-javascript'
        self.endpoint_update_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 options=update_options,
                                 checks=update_checks)

        self.endpoint_delete_cmd(resource_group, endpoint_name, profile_name)

    @unittest.skipUnless(
        os.environ.get('AZURE_TEST_RUN_LIVE'),
        'Temporary playback skip: GA recording is blocked by downstream AFD CP HTTP 409 deployment conflicts. '
        'Restore playback after successful GA re-recording.')
    def test_private_link(self):
        resource_group, profile_name = self.classic_cdn_profile()

        endpoint_name = self.create_random_name(prefix='endpoint', length=24)
        origin = 'www.contoso.com'
        private_link_id = fixture(
            'private_link_id', self.get_subscription_id() if self.is_playback_mode() else None)
        private_link_location = fixture('private_link_location')
        private_link_message = 'Please approve the request'
        checks = [JMESPathCheck('name', endpoint_name),
                  JMESPathCheck('origins[0].hostName', origin),
                  JMESPathCheck('origins[0].privateLinkResourceId', private_link_id),
                  JMESPathCheck('origins[0].privateLinkLocation', private_link_location, False),
                  JMESPathCheck('origins[0].privateLinkApprovalMessage', private_link_message)]
        self.endpoint_create_cmd(resource_group,
                                 endpoint_name,
                                 profile_name,
                                 origin,
                                 private_link_id=private_link_id,
                                 private_link_location=private_link_location,
                                 private_link_message=private_link_message,
                                 checks=checks)

        selected = f"[?name=='{endpoint_name}']"
        list_checks = [JMESPathCheck(f'length({selected})', 1),
                       JMESPathCheck(f'{selected} | [0].name', endpoint_name),
                       JMESPathCheck(f'{selected} | [0].origins[0].hostName', origin),
                       JMESPathCheck(f'{selected} | [0].origins[0].privateLinkResourceId', private_link_id),
                       JMESPathCheck(f'{selected} | [0].origins[0].privateLinkLocation', private_link_location, False),
                       JMESPathCheck(f'{selected} | [0].origins[0].privateLinkApprovalMessage', private_link_message)]
        self.endpoint_list_cmd(resource_group, profile_name, checks=list_checks)

    def test_endpoint_start_and_stop(self):
        resource_group, profile_name = self.classic_cdn_profile()

        endpoint_name = self.create_random_name(prefix='endpoint', length=24)
        origin = 'www.contoso.com'
        self.endpoint_create_cmd(resource_group, endpoint_name, profile_name, origin)

        checks = [JMESPathCheck('resourceState', 'Stopped')]
        self.endpoint_stop_cmd(resource_group, endpoint_name, profile_name)
        self.endpoint_show_cmd(resource_group, endpoint_name, profile_name, checks=checks)

        checks = [JMESPathCheck('resourceState', 'Running')]
        self.endpoint_start_cmd(resource_group, endpoint_name, profile_name)
        self.endpoint_show_cmd(resource_group, endpoint_name, profile_name, checks=checks)

    def test_rule_engine_crud(self):
        resource_group, profile_name = self.classic_cdn_profile()

        endpoint_name = self.create_random_name(prefix='endpoint', length=24)
        origin = 'www.contoso.com'
        checks = [JMESPathCheck('name', endpoint_name),
                  JMESPathCheck('origins[0].hostName', origin),
                  JMESPathCheck('isHttpAllowed', True),
                  JMESPathCheck('isHttpsAllowed', True),
                  JMESPathCheck('isCompressionEnabled', False),
                  JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString')]
        self.endpoint_create_cmd(resource_group, endpoint_name, profile_name, origin, checks=checks)

        list_checks = [JMESPathCheck(f"length([?name=='{endpoint_name}'])", 1)]
        self.endpoint_list_cmd(resource_group, profile_name, checks=list_checks)

        rulename = 'r1'
        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', False),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString'),
                         JMESPathCheck('length(deliveryPolicy.rules)', 1),
                         JMESPathCheck('deliveryPolicy.rules[0].name', rulename)]
        self.endpoint_add_rule_cmd(resource_group,
                                   endpoint_name,
                                   profile_name,
                                   order=1,
                                   rule_name=rulename,
                                   checks=update_checks)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', False),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString'),
                         JMESPathCheck('length(deliveryPolicy.rules[0].conditions)', 2)]
        self.endpoint_add_condition_cmd(resource_group,
                                        endpoint_name,
                                        profile_name,
                                        checks=update_checks,
                                        options='--rule-name r1 --match-variable RemoteAddress\
                                                 --operator GeoMatch --match-values "TH" "US"')

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('length(deliveryPolicy.rules[0].actions)', 2)]
        self.endpoint_add_action_cmd(resource_group,
                                     endpoint_name,
                                     profile_name,
                                     checks=update_checks,
                                     options='--rule-name r1 --action-name "UrlRewrite"\
                                              --source-pattern "/abc" --destination "/def"')

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('length(deliveryPolicy.rules[0].conditions)', 1)]
        self.endpoint_remove_condition_cmd(resource_group,
                                           endpoint_name,
                                           profile_name,
                                           checks=update_checks,
                                           options='--rule-name r1 --index 0')

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('length(deliveryPolicy.rules[0].actions)', 1)]
        self.endpoint_remove_action_cmd(resource_group,
                                        endpoint_name,
                                        profile_name,
                                        checks=update_checks,
                                        options='--rule-name r1 --index 0')

        rulename = 'r2'
        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', False),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString'),
                         JMESPathCheck('length(deliveryPolicy.rules)', 2),
                         JMESPathCheck('deliveryPolicy.rules[1].name', rulename)]
        self.endpoint_add_rule_cmd(resource_group,
                                   endpoint_name,
                                   profile_name,
                                   order=2,
                                   rule_name=rulename,
                                   checks=update_checks)

        rulename = 'r3'
        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('origins[0].hostName', origin),
                         JMESPathCheck('isHttpAllowed', True),
                         JMESPathCheck('isHttpsAllowed', True),
                         JMESPathCheck('isCompressionEnabled', False),
                         JMESPathCheck('queryStringCachingBehavior', 'IgnoreQueryString'),
                         JMESPathCheck('length(deliveryPolicy.rules)', 3),
                         JMESPathCheck('deliveryPolicy.rules[2].name', rulename)]
        self.endpoint_add_rule_cmd(resource_group,
                                   endpoint_name,
                                   profile_name,
                                   order=3,
                                   rule_name=rulename,
                                   checks=update_checks)

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('length(deliveryPolicy.rules)', 2)]
        self.endpoint_remove_rule_cmd(resource_group,
                                      endpoint_name,
                                      profile_name,
                                      checks=update_checks,
                                      options='--rule-name r1')

        update_checks = [JMESPathCheck('name', endpoint_name),
                         JMESPathCheck('length(deliveryPolicy.rules)', 1)]
        self.endpoint_remove_rule_cmd(resource_group,
                                      endpoint_name,
                                      profile_name,
                                      checks=update_checks,
                                      options='--rule-name r3')

        self.endpoint_delete_cmd(resource_group, endpoint_name, profile_name)
