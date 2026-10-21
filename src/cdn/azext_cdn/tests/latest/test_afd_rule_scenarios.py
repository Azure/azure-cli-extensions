# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ResourceGroupPreparer, JMESPathCheck
from azure.cli.testsdk import ScenarioTest, record_only
from .afdx_scenario_mixin import CdnAfdScenarioMixin
import json

from azure.cli.core.azclierror import (InvalidArgumentValueError)

from azext_cdn.vendored_sdks.models import SkuName

from collections import namedtuple
from azure.core.exceptions import HttpResponseError


def _json_arg(value):
    return "'{}'".format(json.dumps(value, separators=(',', ':')))


def _camel_to_kebab(value):
    return ''.join(['-' + c.lower() if c.isupper() and idx else c.lower() for idx, c in enumerate(value)])


def _condition_json(condition):
    parameters = {
        'match-values': condition.MatchValues,
        'operator': condition.Operator,
        'negate-condition': condition.IsNegative,
    }
    if condition.Transforms:
        parameters['transforms'] = condition.Transforms
    if condition.Selector:
        parameters['selector'] = condition.Selector
    return {_camel_to_kebab(condition.MatchVariable): {'parameters': parameters}}


def _conditions_option(condition):
    return f'--conditions {_json_arg([_condition_json(condition)])}'


def _route_override_actions_option():
    return "--actions '[{\"route-configuration-override\":{\"parameters\":{\"cache-configuration\":{\"cache-behavior\":\"HonorOrigin\",\"query-string-caching-behavior\":\"UseQueryString\",\"is-compression-enabled\":\"Disabled\"}}}}]'"

class CdnAfdRuleScenarioTest(CdnAfdScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_rule_set_crud(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_rule_set_list_cmd(resource_group, profile_name, expect_failure=True)
        self.afd_profile_create_cmd(resource_group, profile_name)

        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_set_list_cmd(resource_group, profile_name, checks=list_checks)

        rule_set_name = self.create_random_name(prefix='ruleset', length=16)
        batch_rules = [{
            'rule-name': 'r0',
            'order': 0,
            'match-processing-behavior': 'Continue',
            'conditions': [],
            'actions': [{
                'route-configuration-override': {
                    'parameters': {
                        'cache-configuration': {
                            'cache-behavior': 'HonorOrigin',
                            'query-string-caching-behavior': 'UseQueryString',
                            'is-compression-enabled': 'Disabled'
                        }
                    }
                }
            }]
        }]
        self.afd_rule_set_add_cmd(resource_group, rule_set_name, profile_name,
                                  batch_mode='true',
                                  rules=batch_rules)

        list_checks = [JMESPathCheck('length(@)', 1)]
        self.afd_rule_set_list_cmd(resource_group, profile_name, checks=list_checks)

        show_checks = [JMESPathCheck('name', rule_set_name),
                       JMESPathCheck('batchMode', True),
                       JMESPathCheck('length(rules)', 1),
                       JMESPathCheck('rules[0].ruleName', 'r0'),
                       JMESPathCheck('rules[0].order', 0),
                       JMESPathCheck('rules[0].actions[0].name', 'RouteConfigurationOverride'),
                       JMESPathCheck('rules[0].actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('provisioningState', 'Succeeded')]
        self.afd_rule_set_show_cmd(resource_group, rule_set_name, profile_name, checks=show_checks)

        self.afd_rule_set_delete_cmd(resource_group, rule_set_name, profile_name)

        self.afd_rule_set_show_cmd(resource_group, rule_set_name, profile_name, expect_failure=True)

        list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_set_list_cmd(resource_group, profile_name, checks=list_checks)

    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_rule_crud(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)

        rule_set_name = self.create_random_name(prefix='ruleset', length=16)
        self.afd_rule_set_add_cmd(resource_group, rule_set_name, profile_name)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        rule_name = 'r0'
        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('matchProcessingBehavior', "Stop"),
                       JMESPathCheck('length(conditions)', 0),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                       JMESPathCheck('actions[0].parameters.originGroupOverride', None)]

        route_override_actions = "--actions '[{\"route-configuration-override\":{\"parameters\":{\"cache-configuration\":{\"cache-behavior\":\"HonorOrigin\",\"query-string-caching-behavior\":\"UseQueryString\",\"is-compression-enabled\":\"Disabled\"}}}}]'"
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                              options=f'--match-processing-behavior Stop --order 1 '
                                      f'{route_override_actions}')

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name,
                               profile_name,
                               checks=rule_checks)

        self.afd_rule_delete_cmd(resource_group,
                                 rule_set_name,
                                 rule_name,
                                 profile_name)

        rule_name = 'r1'
        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('matchProcessingBehavior', "Stop"),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "RemoteAddress"),
                       JMESPathCheck('conditions[0].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "RouteConfigurationOverride"),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                       JMESPathCheck('actions[0].parameters.originGroupOverride', None)]

        remote_address_th_conditions = "--conditions '[{\"remote-address\":{\"parameters\":{\"match-values\":[\"TH\"],\"operator\":\"GeoMatch\"}}}]'"
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                      options=f'--match-processing-behavior Stop --order 1 '
                  f'{remote_address_th_conditions} '
                  f'{route_override_actions}')

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name,
                               profile_name,
                               checks=rule_checks)

        rule_name1 = 'r2'
        rule_checks = [JMESPathCheck('order', 2),
                       JMESPathCheck('name', rule_name1),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "RequestScheme"),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'HTTP'),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "UrlRedirect"),
                       JMESPathCheck('actions[0].parameters.redirectType', "Moved"),
                       JMESPathCheck('actions[0].parameters.destinationProtocol', 'Https')]
        request_scheme_http_conditions = "--conditions '[{\"request-scheme\":{\"parameters\":{\"match-values\":[\"HTTP\"],\"operator\":\"Equal\"}}}]'"
        url_redirect_actions = "--actions '[{\"url-redirect\":{\"parameters\":{\"redirect-type\":\"Moved\",\"destination-protocol\":\"Https\"}}}]'"
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name1,
                              profile_name,
                      options=f'--order 2 {request_scheme_http_conditions} '
                          f'{url_redirect_actions}')

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name1,
                               profile_name,
                               checks=rule_checks)

        rule_list_checks = [JMESPathCheck('length(@)', 2)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        self.afd_rule_delete_cmd(resource_group, rule_set_name, rule_name1, profile_name)
        rule_list_checks = [JMESPathCheck('length(@)', 1)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 2),
                       JMESPathCheck('conditions[1].name', "RemoteAddress"),
                       JMESPathCheck('conditions[1].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[1].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('conditions[1].parameters.matchValues[1]', 'US'),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "RouteConfigurationOverride"),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                       JMESPathCheck('actions[0].parameters.originGroupOverride', None)]
        remote_address_th_us_condition = "--condition-name RemoteAddress --remote-address '{\"parameters\":{\"match-values\":[\"TH\",\"US\"],\"operator\":\"GeoMatch\"}}'"
        self.afd_rule_add_condition_cmd(resource_group,
                                        rule_set_name,
                                        rule_name,
                                        profile_name,
                        options=remote_address_th_us_condition)

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name,
                               profile_name,
                               checks=rule_checks)

        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 2),
                       JMESPathCheck('conditions[1].name', "RemoteAddress"),
                       JMESPathCheck('conditions[1].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[1].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('conditions[1].parameters.matchValues[1]', 'US'),
                       JMESPathCheck('length(actions)', 2),
                       JMESPathCheck('actions[0].name', "RouteConfigurationOverride"),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                       JMESPathCheck('actions[0].parameters.originGroupOverride', None),
                       JMESPathCheck('actions[1].name', "UrlRewrite"),
                       JMESPathCheck('actions[1].parameters.sourcePattern', '/abc'),
                       JMESPathCheck('actions[1].parameters.destination', '/def')]
        url_rewrite_action = "--action-name UrlRewrite --url-rewrite '{\"parameters\":{\"source-pattern\":\"/abc\",\"destination\":\"/def\"}}'"
        self.afd_rule_add_action_cmd(resource_group,
                                     rule_set_name,
                                     rule_name,
                                     profile_name,
                         options=url_rewrite_action)

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name,
                               profile_name,
                               checks=rule_checks)

        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "RemoteAddress"),
                       JMESPathCheck('conditions[0].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('conditions[0].parameters.matchValues[1]', 'US'),
                       JMESPathCheck('length(actions)', 2),
                       JMESPathCheck('actions[0].name', "RouteConfigurationOverride"),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                       JMESPathCheck('actions[0].parameters.originGroupOverride', None),
                       JMESPathCheck('actions[1].name', "UrlRewrite"),
                       JMESPathCheck('actions[1].parameters.sourcePattern', '/abc'),
                       JMESPathCheck('actions[1].parameters.destination', '/def')]
        self.afd_rule_remove_condition_cmd(resource_group,
                                           rule_set_name,
                                           rule_name,
                                           profile_name,
                                           0)

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name,
                               profile_name,
                               checks=rule_checks)

        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "RemoteAddress"),
                       JMESPathCheck('conditions[0].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('conditions[0].parameters.matchValues[1]', 'US'),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "UrlRewrite"),
                       JMESPathCheck('actions[0].parameters.sourcePattern', '/abc'),
                       JMESPathCheck('actions[0].parameters.destination', '/def')]
        self.afd_rule_remove_action_cmd(resource_group,
                                        rule_set_name,
                                        rule_name,
                                        profile_name,
                                        0)        

        origin_group_name = self.create_random_name(prefix='og', length=16)
        origin_group_id = f'/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.Cdn/profiles/{profile_name}/originGroups/{origin_group_name}'
        self.afd_origin_group_create_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         "--probe-request-type GET --probe-protocol Http --probe-interval-in-seconds 120 --probe-path /test1/azure.txt "
                                         "--sample-size 4 --successful-samples-required 3 --additional-latency-in-milliseconds 50")

        origin_name1 = self.create_random_name(prefix='origin', length=16)
        create_options = "--host-name huaiyiztesthost1.blob.core.chinacloudapi.cn " \
                         + "--origin-host-header huaiyiztesthost1.blob.core.chinacloudapi.cn " \
                         + "--priority 1 --weight 666 --http-port 8080 --https-port 443 --enabled-state Enabled"

        self.afd_origin_create_cmd(resource_group,
                                   profile_name,
                                   origin_group_name,
                                   origin_name1,
                                   create_options)

        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "RemoteAddress"),
                       JMESPathCheck('conditions[0].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('conditions[0].parameters.matchValues[1]', 'US'),
                       JMESPathCheck('length(actions)', 2),
                       JMESPathCheck('actions[1].name', "RouteConfigurationOverride"),
                       JMESPathCheck('actions[1].parameters.cacheConfiguration.queryStringCachingBehavior', 'IncludeSpecifiedQueryStrings'),
                       JMESPathCheck('actions[1].parameters.cacheConfiguration.cacheBehavior', 'OverrideAlways'),
                       JMESPathCheck('actions[1].parameters.cacheConfiguration.cacheDuration', '01:00:00'),
                       JMESPathCheck('actions[1].parameters.cacheConfiguration.isCompressionEnabled', 'Enabled'),
                       JMESPathCheck('actions[1].parameters.originGroupOverride.originGroup.id', origin_group_id, False),
                       JMESPathCheck('actions[1].parameters.originGroupOverride.forwardingProtocol', "MatchRequest"),
                       JMESPathCheck('actions[0].name', "UrlRewrite"),
                       JMESPathCheck('actions[0].parameters.sourcePattern', '/abc'),
                       JMESPathCheck('actions[0].parameters.destination', '/def')]
        route_override_action = f"--action-name RouteConfigurationOverride --route-configuration-override '{{\"parameters\":{{\"cache-configuration\":{{\"cache-behavior\":\"OverrideAlways\",\"cache-duration\":\"01:00:00\",\"query-string-caching-behavior\":\"IncludeSpecifiedQueryStrings\",\"query-parameters\":\"x,y,z\",\"is-compression-enabled\":\"Enabled\"}},\"origin-group-override\":{{\"origin-group\":{{\"id\":\"{origin_group_id}\"}},\"forwarding-protocol\":\"MatchRequest\"}}}}}}'"
        self.afd_rule_add_action_cmd(resource_group,
                                     rule_set_name,
                                     rule_name,
                                     profile_name,
                         options=route_override_action)

        self.afd_rule_show_cmd(resource_group,
                               rule_set_name,
                               rule_name,
                               profile_name,
                               checks=rule_checks)

        self.afd_rule_delete_cmd(resource_group,
                                 rule_set_name,
                                 rule_name,
                                 profile_name)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        self.afd_rule_set_delete_cmd(resource_group, rule_set_name, profile_name)

    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_rule_complex_condition_creation(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)

        rule_set_name = self.create_random_name(prefix='ruleset', length=16)
        self.afd_rule_set_add_cmd(resource_group, rule_set_name, profile_name)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        Condition = namedtuple('Condition', 'MatchVariable Operator MatchValues IsNegative Transforms Selector')
        conditions = [Condition("RemoteAddress", "GeoMatch", ["TH", "CN"], True, [], None),
                      Condition("RequestMethod", "Equal", ["HEAD"], False, [], None),
                      Condition("QueryString", "Contains", ["abc"], False, ["Lowercase", "UrlDecode"], None),
                      Condition("PostArgs", "RegEx", ["abc[0-9]+"], False, ["Lowercase"], "Arg1"),
                      Condition("RequestUri", "Equal", ["/test1/submit"], False, ["Lowercase", "UrlDecode"], None),
                      Condition("RequestHeader", "BeginsWith", ["head1", "header2"], False, ["Lowercase", "UrlDecode"], "Header1"),
                      Condition("RequestBody", "Contains", ["b1", "b2"], False, ["Lowercase", "UrlDecode"], None),
                      #Condition("RequestScheme", "Equal", ["HTTPS"], False, [], None),
                      Condition("UrlPath", "Contains", ["url1"], True, ["Lowercase"], None),
                      Condition("UrlFileExtension", "Equal", ["exe", "apk", "msi"], True, ["Lowercase"], None),
                      Condition("UrlFileName", "RegEx", ["[a-z1-9]+"], True, ["Lowercase"], None),
                      Condition("HttpVersion", "Equal", ["1.0", "1.1"], True, None, None),
                      Condition("Cookies", "Equal", ["exe", "apk", "msi"], True, ["Lowercase"], "cookie1"),
                      Condition("IsDevice", "Equal", ["Mobile"], False, [], None),
                      Condition("SocketAddr", "IPMatch", ["127.0.0.1"], True, [], None),
                      Condition("ClientPort", "Equal", ["8000"], True, [], None),
                      Condition("ServerPort", "Equal", ["80", "443"], False, [], None),
                      Condition("HostName", "Equal", ["www.contoso.com"], False, ["Lowercase"], None),
                      Condition("SslProtocol", "Equal", ["TLSv1", "TLSv1.1"], True, [], None)]

        for idx, condition in enumerate(conditions):           
            rule_name = self.create_random_name(prefix='rule', length=16)
            rule_checks = [JMESPathCheck('order', idx),
                        JMESPathCheck('name', rule_name),
                        JMESPathCheck('length(conditions)', 1),
                        JMESPathCheck(f'conditions[0].name', condition.MatchVariable),
                        JMESPathCheck(f'conditions[0].parameters.operator', condition.Operator),
                        JMESPathCheck(f'conditions[0].parameters.negateCondition', condition.IsNegative),                        
                        JMESPathCheck('length(actions)', 1),
                        JMESPathCheck('actions[0].name', "RouteConfigurationOverride"),
                        JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                        JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                        JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                        JMESPathCheck('actions[0].parameters.originGroupOverride', None)]
            
            if condition.MatchValues is not None:
                for ii, matchValue in enumerate(condition.MatchValues):
                    rule_checks.append(JMESPathCheck(f'conditions[0].parameters.matchValues[{ii}]', matchValue))

            if condition.Transforms is not None:
                for ii, transform in enumerate(condition.Transforms):
                    rule_checks.append(JMESPathCheck(f'conditions[0].parameters.transforms[{ii}]', transform))

            options = f'--order {idx} ' \
                      f'{_conditions_option(condition)} ' \
                      f'{_route_override_actions_option()}'

            self.afd_rule_add_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                options=options)

            self.afd_rule_show_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                checks=rule_checks)

        rule_list_checks = [JMESPathCheck('length(@)', len(conditions))]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        self.afd_rule_set_delete_cmd(resource_group, rule_set_name, profile_name)

    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_rule_creation_invalid_operator(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)

        rule_set_name = self.create_random_name(prefix='ruleset', length=16)
        self.afd_rule_set_add_cmd(resource_group, rule_set_name, profile_name)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        Condition = namedtuple('Condition', 'MatchVariable Operator MatchValues IsNegative Transforms Selector')
        conditions = [Condition("RemoteAddress", "GeoMatch1", ["TH", "CN"], True, [], None),
                      Condition("RequestMethod", "Equal1", ["HEAD"], False, [], None),
                      Condition("QueryString", "Contains1", ["abc"], False, ["Lowercase", "UrlDecode"], None),
                      Condition("PostArgs", "RegEx1", ["abc[0-9]+"], False, ["Lowercase"], "Arg1"),
                      Condition("RequestUri", "Equal1", ["/test1/submit"], False, ["Lowercase", "UrlDecode"], None),
                      Condition("RequestHeader", "BeginsWith1", ["head1", "header2"], False, ["Lowercase", "UrlDecode"], "Header1"),
                      Condition("RequestBody", "Contains1", ["b1", "b2"], False, ["Lowercase", "UrlDecode"], None),
                      Condition("RequestScheme", "Equal1", ["HTTPS"], False, [], None),
                      Condition("UrlPath", "Contains1", ["url1"], True, ["Lowercase"], None),
                      Condition("UrlFileExtension", "Equal1", ["exe", "apk", "msi"], True, ["Lowercase"], None),
                      Condition("UrlFileName", "RegEx1", ["[a-z1-9]+"], True, ["Lowercase"], None),
                      Condition("HttpVersion", "Equal1", ["1.0", "1.1"], True, None, None),
                      Condition("Cookies", "Equal1", ["exe", "apk", "msi"], True, ["Lowercase"], "cookie1"),
                      Condition("IsDevice", "Equal1", ["Mobile"], False, [], None),
                      Condition("SocketAddr", "IPMatch1", ["127.0.0.1"], True, [], None),
                      Condition("ClientPort", "Equal1", ["8000"], True, [], None),
                      Condition("ServerPort", "Equal1", ["80", "443"], False, [], None),
                      Condition("HostName", "Equal1", ["www.contoso.com"], False, ["Lowercase"], None),
                      Condition("SslProtocol", "Equal1", ["TLSv1", "TLSv1.1"], True, [], None)]

        for idx, condition in enumerate(conditions):           
            rule_name = self.create_random_name(prefix='rule', length=16)

            options = f'--order {idx} ' \
                      f'{_conditions_option(condition)} ' \
                      f'{_route_override_actions_option()}'

            with self.assertRaises(HttpResponseError):
                self.afd_rule_add_cmd(resource_group,
                                    rule_set_name,
                                    rule_name,
                                    profile_name,
                                    options=options)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        self.afd_rule_set_delete_cmd(resource_group, rule_set_name, profile_name)

    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_rule_creation_invalid_match_values(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)

        rule_set_name = self.create_random_name(prefix='ruleset', length=16)
        self.afd_rule_set_add_cmd(resource_group, rule_set_name, profile_name)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        Condition = namedtuple('Condition', 'MatchVariable Operator MatchValues IsNegative Transforms Selector')
        conditions = [#Condition("HttpVersion", "Equal", ["1.8", "1.1"], True, None, None),
                      Condition("RequestMethod", "Equal", ["HEAD1"], False, [], None),
                      Condition("RequestScheme", "Equal", ["HTTPS1"], False, [], None),
                      Condition("IsDevice", "Equal", ["Mobile1"], False, [], None),
                      Condition("SslProtocol", "Equal", ["TLSv11", "TLSv1.1"], True, [], None)]

        for idx, condition in enumerate(conditions):           
            rule_name = self.create_random_name(prefix='rule', length=16)

            options = f'--order {idx} ' \
                      f'{_conditions_option(condition)} ' \
                      f'{_route_override_actions_option()}'

            with self.assertRaises(HttpResponseError):
                self.afd_rule_add_cmd(resource_group,
                                    rule_set_name,
                                    rule_name,
                                    profile_name,
                                    options=options)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        self.afd_rule_set_delete_cmd(resource_group, rule_set_name, profile_name)

    @ResourceGroupPreparer(additional_tags={'owner': 'jingnanxu'})
    def test_afd_rule_actions(self, resource_group):
        profile_name = self.create_random_name(prefix='profile', length=16)
        self.afd_profile_create_cmd(resource_group, profile_name)

        rule_set_name = self.create_random_name(prefix='ruleset', length=16)
        self.afd_rule_set_add_cmd(resource_group, rule_set_name, profile_name)

        rule_list_checks = [JMESPathCheck('length(@)', 0)]
        self.afd_rule_list_cmd(resource_group, rule_set_name, profile_name, checks=rule_list_checks)

        rule_name = 'r1'
        origin_group_name = self.create_random_name(prefix='og', length=16)
        origin_group_id = f'/subscriptions/{self.get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.Cdn/profiles/{profile_name}/originGroups/{origin_group_name}'
        self.afd_origin_group_create_cmd(resource_group,
                                         profile_name,
                                         origin_group_name,
                                         "--probe-request-type GET --probe-protocol Http --probe-interval-in-seconds 120 --probe-path /test1/azure.txt "
                                         "--sample-size 4 --successful-samples-required 3 --additional-latency-in-milliseconds 50")

        origin_name1 = self.create_random_name(prefix='origin', length=16)
        create_options = "--host-name huaiyiztesthost1.blob.core.chinacloudapi.cn " \
                         + "--origin-host-header huaiyiztesthost1.blob.core.chinacloudapi.cn " \
                         + "--priority 1 --weight 666 --http-port 8080 --https-port 443 --enabled-state Enabled"

        self.afd_origin_create_cmd(resource_group,
                                   profile_name,
                                   origin_group_name,
                                   origin_name1,
                                   create_options)

        # RouteConfigurationOverride
        rule_checks = [JMESPathCheck('order', 1),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('matchProcessingBehavior', "Stop"),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "RemoteAddress"),
                       JMESPathCheck('conditions[0].parameters.operator', 'GeoMatch'),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'TH'),
                       JMESPathCheck('conditions[0].parameters.matchValues[1]', 'US'),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "RouteConfigurationOverride"),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.queryStringCachingBehavior', 'UseQueryString'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.cacheBehavior', 'HonorOrigin'),
                       JMESPathCheck('actions[0].parameters.cacheConfiguration.isCompressionEnabled', 'Disabled'),
                       JMESPathCheck('actions[0].parameters.originGroupOverride.originGroup.id', origin_group_id, False),
                       JMESPathCheck('actions[0].parameters.originGroupOverride.forwardingProtocol', "MatchRequest")]
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                      options=f'--match-processing-behavior Stop --order 1 '
                              f'--conditions \'[{{"remote-address":{{"parameters":{{"match-values":["TH","US"],"operator":"GeoMatch"}}}}}}]\' '
                              f'--actions \'[{{"route-configuration-override":{{"parameters":{{"cache-configuration":{{"cache-behavior":"HonorOrigin","query-string-caching-behavior":"UseQueryString","is-compression-enabled":"Disabled"}},"origin-group-override":{{"origin-group":{{"id":"{origin_group_id}"}},"forwarding-protocol":"MatchRequest"}}}}}}}}]\'')
        self.afd_rule_show_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                checks=rule_checks)

        # URL Redirect
        rule_name = 'r2'
        rule_checks = [JMESPathCheck('order', 2),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('conditions[0].name', "UrlFileExtension"),
                       JMESPathCheck('conditions[0].parameters.operator', 'Contains'),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'exe'),
                       JMESPathCheck('conditions[0].parameters.matchValues[1]', 'apk'),
                       JMESPathCheck('matchProcessingBehavior', "Continue"),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "UrlRedirect"),
                       JMESPathCheck('actions[0].parameters.redirectType', "Moved"),
                       JMESPathCheck('actions[0].parameters.destinationProtocol', 'Https'),
                       JMESPathCheck('actions[0].parameters.customHostname', "www.contoso.com"),
                       JMESPathCheck('actions[0].parameters.customPath', '/path1'),
                       JMESPathCheck('actions[0].parameters.customQueryString', "a=b"),
                       JMESPathCheck('actions[0].parameters.customFragment', 'fg1')]
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                      options=f'--order 2 '
                              f'--conditions \'[{{"url-file-extension":{{"parameters":{{"match-values":["exe","apk"],"operator":"Contains"}}}}}}]\' '
                              f'--actions \'[{{"url-redirect":{{"parameters":{{"redirect-type":"Moved","destination-protocol":"Https","custom-hostname":"www.contoso.com","custom-path":"/path1","custom-querystring":"a=b","custom-fragment":"fg1"}}}}}}]\'')
        self.afd_rule_show_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                checks=rule_checks)
        
        # URL Rewrite
        rule_name = 'r3'
        rule_checks = [JMESPathCheck('order', 3),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('matchProcessingBehavior', "Continue"),
                       JMESPathCheck('conditions[0].name', "RequestScheme"),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 'HTTP'),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "UrlRewrite"),
                       JMESPathCheck('actions[0].parameters.sourcePattern', "/abc"),
                       JMESPathCheck('actions[0].parameters.destination', '/def'),
                       JMESPathCheck('actions[0].parameters.preserveUnmatchedPath', True)]
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                      options=f'--order 3 '
                              f'--conditions \'[{{"request-scheme":{{"parameters":{{"match-values":["HTTP"],"operator":"Equal"}}}}}}]\' '
                              f'--actions \'[{{"url-rewrite":{{"parameters":{{"source-pattern":"/abc","destination":"/def","preserve-unmatched-path":true}}}}}}]\'')
        self.afd_rule_show_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                checks=rule_checks)
        
        # ModifyRequestHeader
        rule_name = 'r4'
        rule_checks = [JMESPathCheck('order', 4),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('matchProcessingBehavior', "Continue"),
                       JMESPathCheck('conditions[0].name', "ServerPort"),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 443),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "ModifyRequestHeader"),
                       JMESPathCheck('actions[0].parameters.headerAction', "Append"),
                       JMESPathCheck('actions[0].parameters.headerName', 'header1'),
                       JMESPathCheck('actions[0].parameters.value', 'value1')]
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                      options=f'--order 4 '
                              f'--conditions \'[{{"server-port":{{"parameters":{{"match-values":["443"],"operator":"Equal"}}}}}}]\' '
                              f'--actions \'[{{"modify-request-header":{{"parameters":{{"header-action":"Append","header-name":"header1","value":"value1"}}}}}}]\'')
        self.afd_rule_show_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                checks=rule_checks)

        # ModifyResponseHeader
        rule_name = 'r5'
        rule_checks = [JMESPathCheck('order', 5),
                       JMESPathCheck('name', rule_name),
                       JMESPathCheck('length(conditions)', 1),
                       JMESPathCheck('matchProcessingBehavior', "Continue"),
                       JMESPathCheck('conditions[0].name', "ClientPort"),
                       JMESPathCheck('conditions[0].parameters.matchValues[0]', 8888),
                       JMESPathCheck('length(actions)', 1),
                       JMESPathCheck('actions[0].name', "ModifyResponseHeader"),
                       JMESPathCheck('actions[0].parameters.headerAction', "Overwrite"),
                       JMESPathCheck('actions[0].parameters.headerName', 'header1'),
                       JMESPathCheck('actions[0].parameters.value', 'value1')]
        self.afd_rule_add_cmd(resource_group,
                              rule_set_name,
                              rule_name,
                              profile_name,
                      options=f'--order 5 '
                              f'--conditions \'[{{"client-port":{{"parameters":{{"match-values":["8888"],"operator":"Equal"}}}}}}]\' '
                              f'--actions \'[{{"modify-response-header":{{"parameters":{{"header-action":"Overwrite","header-name":"header1","value":"value1"}}}}}}]\'')
        self.afd_rule_show_cmd(resource_group,
                                rule_set_name,
                                rule_name,
                                profile_name,
                                checks=rule_checks)
       
        for rule_name in ["r1", "r2", "r3", "r4", "r5"]:
            self.afd_rule_delete_cmd(resource_group, rule_set_name, rule_name, profile_name)

        self.afd_rule_set_delete_cmd(resource_group, rule_set_name, profile_name)
