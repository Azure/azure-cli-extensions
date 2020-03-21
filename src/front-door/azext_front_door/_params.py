# pylint: disable=W0611
# ^^ pylint gives spurious "unused imports" for the models classes
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from enum import Enum

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, tags_type, get_location_type, get_three_state_flag, get_enum_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._completers import get_fd_subresource_completion_list
from ._validators import (
    validate_waf_policy, validate_load_balancing_settings, validate_probe_settings,
    validate_frontend_endpoints, validate_backend_pool)


class RouteType(str, Enum):
    forward = "Forward"
    redirect = "Redirect"


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    from azext_front_door.vendored_sdks.models import (
        PolicyMode, FrontDoorProtocol, FrontDoorHealthProbeMethod, FrontDoorCertificateSource, FrontDoorQuery, ActionType, RuleType, TransformType,
        FrontDoorRedirectType, FrontDoorRedirectProtocol, MinimumTLSVersion
    )

    frontdoor_name_type = CLIArgumentType(options_list=['--front-door-name', '-f'], help='Name of the Front Door.', completer=get_resource_name_completion_list('Microsoft.Network/frontdoors'), id_part='name')
    waf_policy_name_type = CLIArgumentType(options_list='--policy-name', help='Name of the WAF policy.', completer=get_resource_name_completion_list('Microsoft.Network/frontDoorWebApplicationFirewallPolicies'), id_part='name')

    # region FrontDoors
    fd_subresources = [
        {'name': 'backend-pool', 'display': 'backend pool', 'ref': 'backend_pools'},
        {'name': 'frontend-endpoint', 'display': 'frontend endpoint', 'ref': 'frontend_endpoints'},
        {'name': 'load-balancing', 'display': 'load balancing settings', 'ref': 'load_balancing_settings'},
        {'name': 'probe', 'display': 'health probe', 'ref': 'health_probe_settings'},
        {'name': 'routing-rule', 'display': 'routing rule', 'ref': 'routing_rules'}
    ]
    for item in fd_subresources:
        with self.argument_context('network front-door {}'.format(item['name'])) as c:
            c.argument('item_name', options_list=['--name', '-n'], help='Name of the {}'.format(item['display']), completer=get_fd_subresource_completion_list(item['ref']), id_part='child_name_1')
            c.argument('front_door_name', frontdoor_name_type, id_part=None)
            c.argument('resource_name', frontdoor_name_type, id_part=None)

    with self.argument_context('network front-door') as c:
        c.argument('front_door_name', frontdoor_name_type, options_list=['--name', '-n'])
        c.argument('friendly_name', help='Friendly name of the Front Door.')
        c.argument('tags', tags_type)
        c.argument('disabled', arg_type=get_three_state_flag(), help='Create in a disabled state.')
        c.argument('enabled', arg_type=get_three_state_flag(positive_label='Enabled', negative_label='Disabled', return_label=True), help='Enabled status.')

    with self.argument_context('network front-door', arg_group='Frontend Endpoint') as c:
        c.argument('frontend_host_name', help='Domain name of the frontend endpoint.')

    with self.argument_context('network front-door', arg_group='HTTPS') as c:
        c.argument('certificate_source', arg_type=get_enum_type(FrontDoorCertificateSource), help='Certificate source to enable HTTPS.')
        c.argument('secret_name', help='The name of the Key Vault secret representing the full certificate PFX')
        c.argument('secret_version', help='The version of the Key Vault secret representing the full certificate PFX')
        c.argument('vault_id', help='The resource id of the Key Vault containing the SSL certificate')
        c.argument('minimum_tls_version', arg_type=get_enum_type(MinimumTLSVersion), help='The minimum TLS version required from the clients to establish an SSL handshake with Front Door.')

    with self.argument_context('network front-door', arg_group='BackendPools Settings') as c:
        c.argument('enforce_certificate_name_check', arg_type=get_three_state_flag(positive_label='Enabled', negative_label='Disabled', return_label=True), help='Whether to disable certificate name check on HTTPS requests to all backend pools. No effect on non-HTTPS requests.')
        c.argument('send_recv_timeout', type=int, help='Send and receive timeout in seconds on forwarding request to the backend. When timeout is reached, the request fails and returns.')

    with self.argument_context('network front-door', arg_group='Backend') as c:
        c.argument('backend_address', help='FQDN of the backend endpoint.')
        c.argument('backend_host_header', help='Host header sent to the backend.')

    with self.argument_context('network front-door', arg_group='Probe Setting') as c:
        c.argument('probe_path', options_list='--path', help='Path to probe.')
        c.argument('probe_protocol', options_list='--protocol', arg_type=get_enum_type(FrontDoorProtocol), help='Protocol to use for sending probes.')
        c.argument('probe_interval', options_list='--interval', type=int, help='Interval in seconds between probes.')
        c.argument('enabled', arg_type=get_three_state_flag(positive_label='Enabled', negative_label='Disabled', return_label=True), help='Enabled status.')
        c.argument('probe_method', options_list='--probeMethod', arg_type=get_enum_type(FrontDoorHealthProbeMethod), help='Configures which HTTP method to use to probe the backends defined under backendPools.')

    with self.argument_context('network front-door', arg_group='Routing Rule') as c:
        c.argument('accepted_protocols', nargs='+', help='Space-separated list of protocols to accept. Default: Http')
        c.argument('patterns_to_match', options_list='--patterns', nargs='+', help='Space-separated list of patterns to match. Default: \'/*\'.')
        c.argument('forwarding_protocol', help='Protocol to use for forwarding traffic.')
        c.argument('route_type', arg_type=get_enum_type(RouteType), help='Route type to define how Front Door should handle requests for this route i.e. forward them to a backend or redirect the users to a different URL.')

    with self.argument_context('network front-door purge-endpoint') as c:
        c.argument('content_paths', nargs='+')

    with self.argument_context('network front-door backend-pool') as c:
        c.argument('load_balancing_settings', options_list='--load-balancing', help='Name or ID of the load balancing settings.', validator=validate_load_balancing_settings)
        c.argument('probe_settings', options_list='--probe', help='Name or ID of the probe settings.', validator=validate_probe_settings)

    with self.argument_context('network front-door frontend-endpoint') as c:
        c.argument('host_name', help='Domain name of the frontend endpoint.')
        c.argument('session_affinity_enabled', arg_type=get_three_state_flag(), help='Whether to allow session affinity on this host.')
        c.argument('session_affinity_ttl', help='The TTL to use in seconds for session affinity.', type=int)
        c.argument('waf_policy', help='Name or ID of a web application firewall policy.', validator=validate_waf_policy)

    with self.argument_context('network front-door load-balancing') as c:
        c.argument('additional_latency', type=int, help='The additional latency in milliseconds for probes to fall in the lowest latency bucket.')
        c.argument('sample_size', type=int, help='The number of samples to consider for load balancing decisions.')
        c.argument('successful_samples_required', type=int, help='The number of samples within the sample period that must succeed.')

    with self.argument_context('network front-door probe') as c:
        c.argument('path', help='Path to probe.')
        c.argument('protocol', arg_type=get_enum_type(FrontDoorProtocol), help='Protocol to use for sending probes.')
        c.argument('interval', help='Interval in seconds between probes.')

    for scope in ['backend-pool', 'backend-pool backend']:
        arg_group = 'Backend' if scope == 'backend-pool' else None
        with self.argument_context('network front-door {}'.format(scope), arg_group=arg_group) as c:
            c.argument('address', help='FQDN of the backend endpoint.')
            c.argument('host_header', help='Host header sent to the backend.')
            c.argument('priority', type=int, help='Priority to use for load balancing. Higher priorities will not be used for load balancing if any lower priority backend is healthy.')
            c.argument('http_port', type=int, help='HTTP TCP port number.')
            c.argument('https_port', type=int, help='HTTPS TCP port number.')
            c.argument('weight', type=int, help='Weight of this endpoint for load balancing purposes.')
            c.argument('backend_host_header', help='Host header sent to the backend.')
            c.argument('backend_pool_name', options_list='--pool-name', help='Name of the backend pool.')
            c.argument('index', type=int, help='Index of the backend to remove (starting with 1).')

    with self.argument_context('network front-door routing-rule', arg_group=None) as c:
        c.argument('accepted_protocols', nargs='+', help='Space-separated list of protocols to accept. Default: Http')
        c.argument('patterns_to_match', options_list='--patterns', nargs='+', help='Space-separated list of patterns to match. Default: \'/*\'.')
        c.argument('forwarding_protocol', help='Protocol to use for forwarding traffic.')
        c.argument('backend_pool', help='Name or ID of a backend pool.', validator=validate_backend_pool)
        c.argument('frontend_endpoints', help='Space-separated list of frontend endpoint names or IDs.', nargs='+', validator=validate_frontend_endpoints)
    with self.argument_context('network front-door routing-rule', arg_group='Forward Routing Rule') as c:
        c.argument('custom_forwarding_path', help='Custom path used to rewrite resource paths matched by this rule. Leave empty to use incoming path.')
        c.argument('caching', arg_type=get_three_state_flag(positive_label='Enabled', negative_label='Disabled', return_label=False), help='Whether to enable caching for this route.')
        c.argument('dynamic_compression', arg_type=get_three_state_flag(positive_label='Enabled', negative_label='Disabled', return_label=True), help='Use dynamic compression for cached content.')
        c.argument('query_parameter_strip_directive', arg_type=get_enum_type(FrontDoorQuery), help='Treatment of URL query terms when forming the cache key.')
    with self.argument_context('network front-door routing-rule', arg_group='Redirect Routing Rule') as c:
        c.argument('redirect_type', arg_type=get_enum_type(FrontDoorRedirectType), help='The redirect type the rule will use when redirecting traffic.')
        c.argument('redirect_protocol', arg_type=get_enum_type(FrontDoorRedirectProtocol), help='The protocol of the destination to where the traffic is redirected.')
        c.argument('custom_host', help='Host to redirect. Leave empty to use use the incoming host as the destination host.')
        c.argument('custom_path', help='The full path to redirect. Path cannot be empty and must start with /. Leave empty to use the incoming path as destination path.')
        c.argument('custom_fragment', help='Fragment to add to the redirect URL. Fragment is the part of the URL that comes after #. Do not include the #.')
        c.argument('custom_query_string', help='The set of query strings to be placed in the redirect URL. Setting this value would replace any existing query string; leave empty to preserve the incoming query string. Query string must be in <key>=<value> format. The first ? and & will be added automatically so do not include them in the front, but do separate multiple query strings with &.')
    # endregion

    # region WafPolicy
    with self.argument_context('network front-door waf-policy') as c:
        c.argument('tags', tags_type)
        c.argument('disabled', arg_type=get_three_state_flag(), help='Create in a disabled state.')
        c.argument('enabled', arg_type=get_three_state_flag(positive_label='Enabled', negative_label='Disabled', return_label=True), help='Enabled status.')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('mode', arg_type=get_enum_type(PolicyMode), help='Firewall policy mode.')
        c.argument('policy_name', waf_policy_name_type, options_list=['--name', '-n'])
        c.argument('redirect_url', help='URL used for redirect rule action.')
        c.argument('custom_block_response_status_code', help='HTTP status to return for blocked requests.')
        c.argument('custom_block_response_body', help='Body to return for blocked requests.')

    with self.argument_context('network front-door waf-policy managed-rules add') as c:
        c.argument('policy_name', waf_policy_name_type)
        c.argument('action', arg_type=get_enum_type(ActionType), help='Action for applied rulesets.')
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset to apply.')
        c.argument('version', help='Rule set version.')

    with self.argument_context('network front-door waf-policy managed-rules list') as c:
        c.argument('policy_name', waf_policy_name_type, id_part=None)

    with self.argument_context('network front-door waf-policy managed-rules override add') as c:
        c.argument('policy_name', waf_policy_name_type)
        c.argument('action', arg_type=get_enum_type(ActionType), help='Action for applied rulesets.')
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset to override.')
        c.argument('rule_group_id', help='ID of the rule group containing the rule to override.')
        c.argument('rule_id', help='ID of the rule to override.')
        c.argument('disabled', help='Whether to disable the rule.')

    with self.argument_context('network front-door waf-policy managed-rules override remove') as c:
        c.argument('policy_name', waf_policy_name_type)
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset with the override to remove.')
        c.argument('rule_group_id', help='ID of the rule group containing the override to remove.')
        c.argument('rule_id', help='ID of the rule override to remove.')

    with self.argument_context('network front-door waf-policy managed-rules override list') as c:
        c.argument('policy_name', waf_policy_name_type, id_part=None)
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset with the overrides to list.')

    with self.argument_context('network front-door waf-policy managed-rules exclusion add') as c:
        c.argument('policy_name', waf_policy_name_type)
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset to exclusion.')
        c.argument('rule_group_id', help='ID of the rule group containing the rule to exclusion.')
        c.argument('rule_id', help='ID of the rule to apply exclusion.')
        c.argument('match_variable', help='Which kind of variable\'s content will be ignored, e.g. RequestHeaderNames, RequestCookieNames, QueryStringArgNames, RequestBodyPostArgNames.')
        c.argument('operator', help='Operator used to compare the variable name to the value, e.g. Equals, Contains, StartsWith, EndsWith, EqualsAny.')
        c.argument('value', help='Values to match the variable name against.')

    with self.argument_context('network front-door waf-policy managed-rules exclusion remove') as c:
        c.argument('policy_name', waf_policy_name_type)
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset with the exclusion to remove.')
        c.argument('rule_group_id', help='ID of the rule group containing the exclusion to remove.')
        c.argument('rule_id', help='ID of the rule to remove from exclusion.')
        c.argument('match_variable', help='Which kind of variable\'s content will be ignored, e.g. RequestHeaderNames, RequestCookieNames, QueryStringArgNames, RequestBodyPostArgNames.')
        c.argument('operator', help='Operator used to compare the variable name to the value, e.g. Equals, Contains, StartsWith, EndsWith, EqualsAny.')
        c.argument('value', help='Values to match the variable name against.')

    with self.argument_context('network front-door waf-policy managed-rules exclusion list') as c:
        c.argument('policy_name', waf_policy_name_type, id_part=None)
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset with the exclusions to list.')
        c.argument('rule_group_id', help='ID of the rule group containing the exclusions to list.')
        c.argument('rule_id', help='ID of the rule to list exclusion for.')

    with self.argument_context('network front-door waf-policy managed-rules remove') as c:
        c.argument('policy_name', waf_policy_name_type)
        c.argument('rule_set_type', options_list=['--type'], help='ID of the ruleset to remove.')

    with self.argument_context('network front-door waf-policy managed-rule-definition list') as c:
        c.argument('policy_name', waf_policy_name_type)

    with self.argument_context('network front-door waf-policy rule create') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.', id_part='child_name_1')
        c.argument('policy_name', waf_policy_name_type)
        c.argument('priority', type=int, help='Priority of the rule.')
        c.argument('rate_limit_duration', type=int, help='Rate limit duration in minutes.')
        c.argument('rate_limit_threshold', type=int, help='Rate limit threshold.')
        c.argument('rule_type', arg_type=get_enum_type(RuleType), help='Type of rule.')
        c.argument('action', arg_type=get_enum_type(ActionType), help='Rule action.')
        c.argument('disabled', help='Whether to disable the rule.')

    with self.argument_context('network front-door waf-policy rule delete') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.', id_part='child_name_1')
        c.argument('policy_name', waf_policy_name_type)

    with self.argument_context('network front-door waf-policy rule show') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.', id_part='child_name_1')
        c.argument('policy_name', waf_policy_name_type)

    with self.argument_context('network front-door waf-policy rule update') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.', id_part='child_name_1')
        c.argument('policy_name', waf_policy_name_type)
        c.argument('priority', type=int, help='Priority of the rule.')
        c.argument('rate_limit_duration', type=int, help='Rate limit duration in minutes.')
        c.argument('rate_limit_threshold', type=int, help='Rate limit threshold.')
        c.argument('rule_type', arg_type=get_enum_type(RuleType), help='Type of rule.')
        c.argument('action', arg_type=get_enum_type(ActionType), help='Rule action.')
        c.argument('disabled', help='Whether to disable the rule.')

    with self.argument_context('network front-door waf-policy rule list') as c:
        c.argument('policy_name', waf_policy_name_type, id_part=None)

    with self.argument_context('network front-door waf-policy rule match-condition add') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.', id_part='child_name_1')
        c.argument('policy_name', waf_policy_name_type)
        c.argument('match_variable', help='Variable[.Selector] Request variable to test with optional selector.')
        c.argument('operator', help='Operator used to compare the variable to the values.')
        c.argument('values', nargs='+', help='Space-separated list of values to match against.')
        c.argument('negate', arg_type=get_three_state_flag(), help='Applies "Not" to the operator.')
        c.argument('transforms', nargs='+', arg_type=get_enum_type(TransformType), help='Space-separated list of transforms to apply.')

    with self.argument_context('network front-door waf-policy rule match-condition remove') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.', id_part='child_name_1')
        c.argument('policy_name', waf_policy_name_type)
        c.argument('index', type=int, help='0-based index of the match condition to remove')

    with self.argument_context('network front-door waf-policy rule match-condition list') as c:
        c.argument('rule_name', options_list=['--name', '-n'], help='Name of the custom rule.')
        c.argument('policy_name', waf_policy_name_type, id_part=None)
    # endregion
