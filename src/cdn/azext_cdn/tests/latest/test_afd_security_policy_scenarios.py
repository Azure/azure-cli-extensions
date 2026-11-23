# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest, record_only
from .afdx_scenario_mixin import CdnAfdScenarioMixin

from azure.core.exceptions import (HttpResponseError)


class CdnAfdSecurityPolicyScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_security_policy_crud(self, resource_group):
        profile_name = 'profilesecuritytest'
        self.afd_security_policy_list_cmd(resource_group, profile_name, expect_failure=True)

        # List get empty
        self.afd_profile_create_cmd(resource_group, profile_name)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_security_policy_list_cmd(resource_group, profile_name, checks=list_checks)

        # Create an endpoint
        endpoint1_name = self.create_random_name(prefix='endpoint1', length=24)
        endpoint2_name = self.create_random_name(prefix='endpoint2', length=24)
        enabled_state = "Enabled"
        endpoint_checks = [JMESPathCheck('enabledState', 'Enabled')]
        self.afd_endpoint_create_cmd(resource_group,
                                     profile_name,
                                     endpoint1_name,
                                     enabled_state,
                                     checks=endpoint_checks)

        self.afd_endpoint_create_cmd(resource_group,
                                     profile_name,
                                     endpoint2_name,
                                     enabled_state,
                                     checks=endpoint_checks)

        origin_group_name = self.create_random_name(prefix='og', length=16)
        self.afd_origin_group_create_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         "--probe-request-type GET --probe-protocol Http --probe-interval-in-seconds 120 --probe-path /test1/azure.txt "
                                         "--sample-size 4 --successful-samples-required 3 --additional-latency-in-milliseconds 50")

        origin_name = self.create_random_name(prefix='origin', length=16)
        create_options = (
            "--host-name huaiyiztesthost1.blob.core.chinacloudapi.cn "
            "--origin-host-header huaiyiztesthost1.blob.core.chinacloudapi.cn "
            "--priority 1 --weight 1000 --http-port 80 --https-port 443 --enabled-state Enabled"
        )
        self.afd_origin_create_cmd(resource_group,
                                   profile_name,
                                   origin_group_name,
                                   origin_name,
                                   create_options)

        route_name = self.create_random_name(prefix='route', length=16)
        route_id = (
            f'/subscriptions/{self.get_subscription_id()}/resourcegroups/{resource_group}'
            f'/providers/Microsoft.Cdn/profiles/{profile_name}/afdEndpoints/{endpoint1_name}'
            f'/routes/{route_name}'
        )
        create_options = (
            f"--origin-group {origin_group_name} "
            "--supported-protocols Https Http --link-to-default-domain Enabled "
            "--https-redirect Enabled --forwarding-protocol MatchRequest"
        )
        self.afd_route_create_cmd(resource_group,
                                  profile_name,
                                  endpoint1_name,
                                  route_name,
                                  create_options)
        
        security_policy_name = self.create_random_name(prefix='security', length=24)
        domain_ids = []
        domain_ids.append(f'/subscriptions/{self.get_subscription_id()}/resourcegroups/{resource_group}/providers/Microsoft.Cdn/profiles/{profile_name}/afdEndpoints/{endpoint1_name}')
        domain_ids.append(f'/subscriptions/{self.get_subscription_id()}/resourcegroups/{resource_group}/providers/Microsoft.Cdn/profiles/{profile_name}/afdEndpoints/{endpoint2_name}')
        
        # Create a security policy with non-exisit waf should fail
        waf_policy_id = f'/subscriptions/{self.get_subscription_id()}/resourcegroups/CliDevReservedGroup/providers/Microsoft.Network/frontdoorwebapplicationfirewallpolicies/nonexist'
        with self.assertRaisesRegex(HttpResponseError,
                                    "Web Application Firewall Policy being attached to AFDX profile does not exist|"
                                    "Waf policy not found in AFD Data store"):
            self.afd_security_policy_create_cmd(resource_group,
                                                profile_name,
                                                security_policy_name,
                                                domain_ids,
                                                waf_policy_id)
        
        # Create a security policy
        waf_policy_id = f'/subscriptions/{self.get_subscription_id()}/resourcegroups/CliDevReservedGroup/providers/Microsoft.Network/frontdoorwebapplicationfirewallpolicies/SampleStandard'
        with self.assertRaisesRegex(HttpResponseError, "Route level association is not allowed"):
            self.afd_security_policy_create_cmd(resource_group,
                                                profile_name,
                                                security_policy_name,
                                                domain_ids,
                                                waf_policy_id,
                                                is_profile_level=False,
                                                routes=[route_id])

        checks = [JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_security_policy_create_cmd(resource_group,
                                            profile_name,
                                            security_policy_name,
                                            domain_ids,
                                            waf_policy_id,
                                            checks=checks,
                                            is_profile_level=False)

        show_checks = [JMESPathCheck('name', security_policy_name),
                       JMESPathCheck('parameters.wafPolicy.id', waf_policy_id),
                       JMESPathCheck('parameters.isProfileLevel', False),
                       JMESPathCheck('length(parameters.associations[0].domains)', 2),
                       JMESPathCheck('parameters.associations[0].domains[0].id', domain_ids[0]),
                       JMESPathCheck('parameters.associations[0].domains[1].id', domain_ids[1]),
                       JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_security_policy_show_cmd(resource_group, profile_name, security_policy_name, checks=show_checks)

        list_checks = [JMESPathCheck('length(@)', 1),
                       JMESPathCheck('@[0].name', security_policy_name),
                       JMESPathCheck('@[0].provisioningState', 'Succeeded')]
        self.afd_security_policy_list_cmd(resource_group, profile_name, checks=list_checks)

        # Update the security policy
        update_checks = [JMESPathCheck('name', security_policy_name),
                         JMESPathCheck('parameters.wafPolicy.id', waf_policy_id),
                         JMESPathCheck('parameters.isProfileLevel', False),
                         JMESPathCheck('length(parameters.associations[0].domains)', 1),
                         JMESPathCheck('parameters.associations[0].domains[0].id', domain_ids[1]),
                         JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_security_policy_update_cmd(resource_group,
                                            profile_name,
                                            security_policy_name,
                                            [domain_ids[1]],
                                            waf_policy_id,
                                            checks=update_checks,
                                            is_profile_level=False)

        # Delete the security policy
        self.afd_security_policy_delete_cmd(resource_group, profile_name, security_policy_name)
        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_security_policy_list_cmd(resource_group, profile_name, checks=list_checks)
