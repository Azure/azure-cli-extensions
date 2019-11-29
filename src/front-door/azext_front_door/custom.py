# pylint: disable=C0200, R1702
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines

import sys

from azure.cli.core.commands import cached_get, cached_put
from azure.cli.core.util import sdk_no_wait

from knack.log import get_logger

from ._client_factory import cf_frontdoor, cf_waf_policies, cf_waf_managed_rules, cf_fd_frontend_endpoints


logger = get_logger(__name__)


class UpdateContext(object):

    def __init__(self, instance):
        self.instance = instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def update_param(self, prop, value, allow_clear):
        if value == '' and allow_clear:
            setattr(self.instance, prop, None)
        elif value is not None:
            setattr(self.instance, prop, value)


def _upsert_frontdoor_subresource(cmd, resource_group_name, front_door_name, collection_name, obj_to_add, key_name):
    client = cf_frontdoor(cmd.cli_ctx, None)
    frontdoor = client.get(resource_group_name, front_door_name)
    if not getattr(frontdoor, collection_name, None):
        setattr(frontdoor, collection_name, [])
    collection = getattr(frontdoor, collection_name, None)

    item_name = getattr(obj_to_add, key_name)
    if item_name is None:
        from knack.util import CLIError
        raise CLIError(
            "Unable to resolve a value for key '{}' with which to match.".format(key_name))
    match = next((x for x in collection if getattr(x, key_name, None) == item_name), None)
    if match:
        logger.warning("Item '%s' already exists. Replacing with new values.", item_name)
        collection.remove(match)
    collection.append(obj_to_add)
    result = client.create_or_update(resource_group_name, front_door_name, frontdoor).result()
    collection = getattr(result, collection_name)
    item = next(x for x in collection if getattr(x, key_name) == item_name)
    return item


def list_frontdoor_resource_property(resource, prop):
    """ Factory method for creating list functions. """

    def list_func(cmd, resource_group_name, resource_name):
        client = cf_frontdoor(cmd.cli_ctx, None)
        return client.get(resource_group_name, resource_name).__getattribute__(prop)

    func_name = 'list_fd_{}_{}'.format(resource, prop)
    setattr(sys.modules[__name__], func_name, list_func)
    return func_name


def get_frontdoor_resource_property_entry(resource, prop):
    """ Factory method for creating get functions. """

    def get_func(cmd, resource_group_name, resource_name, item_name):
        client = cf_frontdoor(cmd.cli_ctx, None)
        items = getattr(client.get(resource_group_name, resource_name), prop)

        result = next((x for x in items if x.name.lower() == item_name.lower()), None)
        if not result:
            from knack.util import CLIError
            raise CLIError("Item '{}' does not exist on {} '{}'".format(
                item_name, resource, resource_name))

        return result

    func_name = 'get_fd_{}_{}'.format(resource, prop)
    setattr(sys.modules[__name__], func_name, get_func)
    return func_name


def delete_frontdoor_resource_property_entry(resource, prop):
    """ Factory method for creating delete functions. """

    def delete_func(cmd, resource_group_name, resource_name, item_name, no_wait=False):  # pylint: disable=unused-argument

        client = cf_frontdoor(cmd.cli_ctx, None)
        item = client.get(resource_group_name, resource_name)
        keep_items = \
            [x for x in item.__getattribute__(prop) if x.name.lower() != item_name.lower()]
        with UpdateContext(item) as c:
            c.update_param(prop, keep_items, False)
        if no_wait:
            sdk_no_wait(no_wait, client.create_or_update, resource_group_name, resource_name, item)
        else:
            result = sdk_no_wait(no_wait, client.create_or_update, resource_group_name, resource_name, item).result()
            if next((x for x in getattr(result, prop) if x.name.lower() == item_name.lower()), None):
                from knack.util import CLIError
                raise CLIError("Failed to delete '{}' on '{}'".format(item_name, resource_name))

    func_name = 'delete_fd_{}_{}'.format(resource, prop)
    setattr(sys.modules[__name__], func_name, delete_func)
    return func_name


# region Frontdoor
def _front_door_subresource_id(cmd, resource_group, front_door_name, child_type, child_name):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import resource_id

    subscription_id = get_subscription_id(cmd.cli_ctx)

    return resource_id(
        subscription=subscription_id,
        resource_group=resource_group,
        namespace='Microsoft.Network',
        type='frontdoors',
        name=front_door_name,
        child_type_1=child_type,
        child_name_1=child_name)


# pylint: disable=too-many-locals
def create_front_door(cmd, resource_group_name, front_door_name, backend_address,
                      friendly_name=None, tags=None, disabled=None, no_wait=False,
                      backend_host_header=None, frontend_host_name=None,
                      probe_path='/', probe_protocol='Https', probe_interval=30, probe_method='HEAD',
                      accepted_protocols=None, patterns_to_match=None, forwarding_protocol='MatchRequest',
                      enforce_certificate_name_check='Enabled', send_recv_timeout=None):
    from azext_front_door.vendored_sdks.models import (
        FrontDoor, FrontendEndpoint, BackendPool, Backend, HealthProbeSettingsModel, LoadBalancingSettingsModel,
        RoutingRule, ForwardingConfiguration, BackendPoolsSettings)

    # set the default names (consider making user-settable)
    backend_pool_name = 'DefaultBackendPool'
    frontend_endpoint_name = 'DefaultFrontendEndpoint'
    probe_setting_name = 'DefaultProbeSettings'
    load_balancing_settings_name = 'DefaultLoadBalancingSettings'
    routing_rule_name = 'DefaultRoutingRule'

    # get the IDs to fill the references
    backend_pool_id = _front_door_subresource_id(
        cmd, resource_group_name, front_door_name, 'backendPools', backend_pool_name)
    frontend_endpoint_id = _front_door_subresource_id(
        cmd, resource_group_name, front_door_name, 'frontendEndpoints', frontend_endpoint_name)
    probe_settings_id = _front_door_subresource_id(
        cmd, resource_group_name, front_door_name, 'healthProbeSettings', probe_setting_name)
    load_balancing_settings_id = _front_door_subresource_id(
        cmd, resource_group_name, front_door_name, 'loadBalancingSettings', load_balancing_settings_name)

    front_door = FrontDoor(
        tags=tags,
        location='global',
        friendly_name=friendly_name or front_door_name,
        enabled_state='Enabled' if not disabled else 'Disabled',
        backend_pools=[
            BackendPool(
                name=backend_pool_name,
                backends=[
                    Backend(
                        address=backend_address,
                        http_port=80,
                        https_port=443,
                        priority=1,
                        weight=50,
                        backend_host_header=backend_host_header or backend_address,
                        enabled_state='Enabled')
                ],
                health_probe_settings={'id': probe_settings_id},
                load_balancing_settings={'id': load_balancing_settings_id},
                resource_state='Enabled'
            )
        ],
        health_probe_settings=[
            HealthProbeSettingsModel(
                name=probe_setting_name,
                interval_in_seconds=probe_interval,
                health_probe_method=probe_method,
                path=probe_path,
                protocol=probe_protocol,
                resource_state='Enabled'
            )
        ],
        frontend_endpoints=[
            FrontendEndpoint(
                name=frontend_endpoint_name,
                host_name=frontend_host_name if frontend_host_name else '{}.azurefd.net'.format(front_door_name),
                session_affinity_enabled_state='Disabled',
                resource_state='Enabled'
            )
        ],
        load_balancing_settings=[
            LoadBalancingSettingsModel(
                name=load_balancing_settings_name,
                additional_latency_milliseconds=0,
                sample_size=4,
                successful_samples_required=2,
                resource_state='Enabled'
            )
        ],
        routing_rules=[
            RoutingRule(
                name=routing_rule_name,
                frontend_endpoints=[{'id': frontend_endpoint_id}],
                accepted_protocols=accepted_protocols or ['Http'],
                patterns_to_match=patterns_to_match or ['/*'],
                route_configuration=ForwardingConfiguration(forwarding_protocol=forwarding_protocol,
                                                            backend_pool={'id': backend_pool_id}),
                enabled_state='Enabled',
                resource_state='Enabled'
            )
        ],
        backend_pools_settings=BackendPoolsSettings(enforce_certificate_name_check=enforce_certificate_name_check,
                                                    send_recv_timeout_seconds=send_recv_timeout)
    )
    return sdk_no_wait(no_wait, cf_frontdoor(cmd.cli_ctx, None).create_or_update,
                       resource_group_name, front_door_name, front_door)


def update_front_door(instance, tags=None, enforce_certificate_name_check=None,
                      send_recv_timeout=None):
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)
    with UpdateContext(instance.backend_pools_settings) as c:
        c.update_param('enforce_certificate_name_check', enforce_certificate_name_check, False)
        c.update_param('send_recv_timeout_seconds', send_recv_timeout, False)
    return instance


def list_front_doors(cmd, resource_group_name=None):
    client = cf_frontdoor(cmd.cli_ctx, None)
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list()


def list_fd_frontend_endpoints(cmd, resource_group_name, resource_name):
    client = cf_fd_frontend_endpoints(cmd.cli_ctx, None)
    return client.list_by_front_door(resource_group_name, resource_name)


def get_fd_frontend_endpoints(cmd, resource_group_name, resource_name, item_name):
    client = cf_fd_frontend_endpoints(cmd.cli_ctx, None)
    return client.get(resource_group_name, resource_name, item_name)


def create_fd_frontend_endpoints(cmd, resource_group_name, front_door_name, item_name, host_name,
                                 session_affinity_enabled=None, session_affinity_ttl=None,
                                 waf_policy=None):
    from azext_front_door.vendored_sdks.models import FrontendEndpoint, SubResource
    endpoint = FrontendEndpoint(
        name=item_name,
        host_name=host_name,
        session_affinity_enabled_state=session_affinity_enabled,
        session_affinity_ttl_seconds=session_affinity_ttl,
        web_application_firewall_policy_link=SubResource(id=waf_policy) if waf_policy else None
    )
    return _upsert_frontdoor_subresource(cmd, resource_group_name, front_door_name, 'frontend_endpoints',
                                         endpoint, 'name')


def update_fd_frontend_endpoints(instance, host_name=None, session_affinity_enabled=None,
                                 session_affinity_ttl=None, waf_policy=None):
    from azext_front_door.vendored_sdks.models import SubResource
    with UpdateContext(instance) as c:
        c.update_param('hostName', host_name, False)
        c.update_param('sessionAffinityEnabledState', session_affinity_enabled, False)
        c.update_param('sessionAffinityTtlSeconds', session_affinity_ttl, False)
        c.update_param('webApplicationFirewallPolicyLink', SubResource(id=waf_policy) if waf_policy else None, False)
    return instance


def configure_fd_frontend_endpoint_disable_https(cmd, resource_group_name, front_door_name, item_name):
    return cf_fd_frontend_endpoints(cmd.cli_ctx, None).disable_https(resource_group_name, front_door_name,
                                                                     item_name)


def configure_fd_frontend_endpoint_enable_https(cmd, resource_group_name, front_door_name, item_name,
                                                secret_name=None, secret_version=None,
                                                certificate_source='FrontDoor', vault_id=None,
                                                minimum_tls_version='1.2'):
    keyvault_usage = ('usage error: --certificate-source AzureKeyVault --vault-id ID '
                      '--secret-name NAME --secret-version VERSION')
    if certificate_source != 'AzureKeyVault' and any([vault_id, secret_name, secret_version]):
        from knack.util import CLIError
        raise CLIError(keyvault_usage)
    if certificate_source == 'AzureKeyVault' and not all([vault_id, secret_name, secret_version]):
        from knack.util import CLIError
        raise CLIError(keyvault_usage)

    # if not being disabled, then must be enabled
    if certificate_source == 'FrontDoor':
        return configure_fd_frontend_endpoint_https_frontdoor(cmd, resource_group_name,
                                                              front_door_name, item_name, minimum_tls_version)
    if certificate_source == 'AzureKeyVault':
        return configure_fd_frontend_endpoint_https_keyvault(cmd, resource_group_name, front_door_name,
                                                             item_name, vault_id, secret_name,
                                                             secret_version, minimum_tls_version)
    return None


def configure_fd_frontend_endpoint_https_frontdoor(cmd, resource_group_name, front_door_name,
                                                   item_name, minimum_tls_version):
    from azext_front_door.vendored_sdks.models import CustomHttpsConfiguration
    config = CustomHttpsConfiguration(
        certificate_source="FrontDoor",
        protocol_type="ServerNameIndication",
        vault=None,
        secret_name=None,
        secret_version=None,
        certificate_type="Dedicated",
        minimum_tls_version=minimum_tls_version
    )
    cf_fd_frontend_endpoints(cmd.cli_ctx, None).enable_https(resource_group_name, front_door_name,
                                                             item_name, config)
    return get_fd_frontend_endpoints(cmd, resource_group_name, front_door_name, item_name)


def configure_fd_frontend_endpoint_https_keyvault(cmd, resource_group_name, front_door_name, item_name,
                                                  vault_id, secret_name, secret_version, minimum_tls_version):
    from azext_front_door.vendored_sdks.models import CustomHttpsConfiguration, SubResource
    config = CustomHttpsConfiguration(
        certificate_source="AzureKeyVault",
        protocol_type="ServerNameIndication",
        vault=SubResource(id=vault_id),
        secret_name=secret_name,
        secret_version=secret_version,
        certificate_type=None,
        minimum_tls_version=minimum_tls_version
    )
    cf_fd_frontend_endpoints(cmd.cli_ctx, None).enable_https(resource_group_name, front_door_name,
                                                             item_name, config)
    return get_fd_frontend_endpoints(cmd, resource_group_name, front_door_name, item_name)


def create_fd_backend_pools(cmd, resource_group_name, front_door_name, item_name,
                            load_balancing_settings, probe_settings,
                            address, http_port=80, https_port=443, disabled=None, priority=1, weight=50,
                            backend_host_header=None):
    from azext_front_door.vendored_sdks.models import BackendPool, SubResource
    pool = BackendPool(
        name=item_name,
        load_balancing_settings=SubResource(id=load_balancing_settings) if load_balancing_settings else None,
        health_probe_settings=SubResource(id=probe_settings) if probe_settings else None,
        resource_state='Disabled' if disabled else 'Enabled',
        backends=[
            {
                'address': address,
                'http_port': http_port,
                'https_port': https_port,
                'enabled_state': 'Disabled' if disabled else 'Enabled',
                'priority': priority,
                'weight': weight,
                'backend_host_header': backend_host_header or address
            }
        ]
    )
    return _upsert_frontdoor_subresource(cmd, resource_group_name, front_door_name, 'backend_pools', pool, 'name')


def update_fd_backend_pools(instance, load_balancing_settings=None, probe_settings=None):
    from azext_front_door.vendored_sdks.models import SubResource
    with UpdateContext(instance) as c:
        c.update_param('loadBalancingSettings', SubResource(id=load_balancing_settings)
                       if load_balancing_settings else None, False)
        c.update_param('healthProbeSettings', SubResource(id=probe_settings) if probe_settings else None, False)
    return instance


def add_fd_backend(cmd, resource_group_name, front_door_name, backend_pool_name, address,
                   http_port=80, https_port=443, disabled=None, priority=1, weight=50,
                   backend_host_header=None):
    from azext_front_door.vendored_sdks.models import Backend
    backend = Backend(
        address=address,
        http_port=http_port,
        https_port=https_port,
        enabled_state='Disabled' if disabled else 'Enabled',
        priority=priority,
        weight=weight,
        backend_host_header=backend_host_header or address
    )
    client = cf_frontdoor(cmd.cli_ctx, None)
    frontdoor = client.get(resource_group_name, front_door_name)
    backend_pool = next((x for x in frontdoor.backend_pools if x.name == backend_pool_name), None)
    if not backend_pool:
        from knack.util import CLIError
        raise CLIError("Backend pool '{}' could not be found on frontdoor '{}'".format(
            backend_pool_name, front_door_name))
    backend_pool.backends.append(backend)
    client.create_or_update(resource_group_name, front_door_name, frontdoor).result()
    return backend


def list_fd_backends(cmd, resource_group_name, front_door_name, backend_pool_name):
    client = cf_frontdoor(cmd.cli_ctx, None)
    frontdoor = client.get(resource_group_name, front_door_name)
    backend_pool = next((x for x in frontdoor.backend_pools if x.name == backend_pool_name), None)
    if not backend_pool:
        from knack.util import CLIError
        raise CLIError("Backend pool '{}' could not be found on frontdoor '{}'".format(
            backend_pool_name, front_door_name))
    return backend_pool.backends


def remove_fd_backend(cmd, resource_group_name, front_door_name, backend_pool_name, index):
    client = cf_frontdoor(cmd.cli_ctx, None)
    frontdoor = client.get(resource_group_name, front_door_name)
    backend_pool = next((x for x in frontdoor.backend_pools if x.name == backend_pool_name), None)
    if not backend_pool:
        from knack.util import CLIError
        raise CLIError("Backend pool '{}' could not be found on frontdoor '{}'".format(
            backend_pool_name, front_door_name))
    try:
        backend_pool.backends.pop(index - 1)
    except IndexError:
        from knack.util import CLIError
        raise CLIError('invalid index. Index can range from 1 to {}'.format(len(backend_pool.backends)))
    client.create_or_update(resource_group_name, front_door_name, frontdoor).result()


def create_fd_health_probe_settings(cmd, resource_group_name, front_door_name, item_name, probe_path, probe_interval,
                                    protocol=None, probe_method='HEAD', enabled='Enabled'):
    from azext_front_door.vendored_sdks.models import HealthProbeSettingsModel
    probe = HealthProbeSettingsModel(
        name=item_name,
        path=probe_path,
        protocol=protocol,
        interval_in_seconds=probe_interval,
        health_probe_method=probe_method,
        enabled_state=enabled
    )
    return _upsert_frontdoor_subresource(cmd, resource_group_name, front_door_name,
                                         'health_probe_settings', probe, 'name')


def update_fd_health_probe_settings(cmd, resource_group_name, front_door_name, item_name,
                                    probe_path=None, probe_protocol=None, probe_interval=None,
                                    enabled=None, probe_method=None):
    client = cf_frontdoor(cmd.cli_ctx, None)
    frontdoor = client.get(resource_group_name, front_door_name)
    probe_setting = next((x for x in frontdoor.health_probe_settings if x.name == item_name), None)
    if not probe_setting:
        from knack.util import CLIError
        raise CLIError("Health probe setting '{}' could not be found on frontdoor '{}'".format(
            item_name, front_door_name))
    if probe_method:
        probe_setting.health_probe_method = probe_method
    if probe_path:
        probe_setting.path = probe_path
    if probe_protocol:
        probe_setting.protocol = probe_protocol
    if probe_interval:
        probe_setting.interval_in_seconds = probe_interval
    if enabled:
        probe_setting.enabled_state = enabled

    client.create_or_update(resource_group_name, front_door_name, frontdoor).result()
    return probe_setting


def create_fd_load_balancing_settings(cmd, resource_group_name, front_door_name, item_name, sample_size,
                                      successful_samples_required, additional_latency=None):
    from azext_front_door.vendored_sdks.models import LoadBalancingSettingsModel
    settings = LoadBalancingSettingsModel(
        name=item_name,
        sample_size=sample_size,
        successful_samples_required=successful_samples_required,
        additional_latency_milliseconds=additional_latency
    )
    return _upsert_frontdoor_subresource(cmd, resource_group_name, front_door_name, 'load_balancing_settings',
                                         settings, 'name')


def update_fd_load_balancing_settings(instance, sample_size=None, successful_samples_required=None,
                                      additional_latency=None):
    with UpdateContext(instance) as c:
        c.update_param('sample_size', sample_size, False)
        c.update_param('successful_samples_required', successful_samples_required, False)
        c.update_param('additional_latency_milliseconds', additional_latency, False)
    return instance


def create_fd_routing_rules(cmd, resource_group_name, front_door_name, item_name, frontend_endpoints, route_type,
                            backend_pool=None, accepted_protocols=None, patterns_to_match=None,
                            custom_forwarding_path=None, forwarding_protocol=None, disabled=None,
                            caching=None, dynamic_compression=None, query_parameter_strip_directive=None,
                            redirect_type='Moved', redirect_protocol='MatchRequest', custom_host=None, custom_path=None,
                            custom_fragment=None, custom_query_string=None):
    from azext_front_door.vendored_sdks.models import (CacheConfiguration, RoutingRule, SubResource,
                                                       ForwardingConfiguration, RedirectConfiguration)

    forwarding_usage = ('usage error: [--backend-pool BACKEND_POOL] '
                        '[--custom-forwarding-path CUSTOM_FORWARDING_PATH] '
                        '[--forwarding-protocol FORWARDING_PROTOCOL] '
                        '[--caching {Enabled,Disbaled}]'
                        '[--query-parameter-strip-directive {StripNone,StripAll}] '
                        '[--dynamic-compression [{Enabled,Disabled}]]')
    redirect_usage = ('usage error: [--redirect-type {Moved,Found,TemporaryRedirect,PermanentRedirect}]'
                      '[--redirect-protocol {HttpOnly,HttpsOnly,MatchRequest}] '
                      '[--custom-host CUSTOM_HOST] [--custom-path CUSTOM_PATH] '
                      '[--custom-fragment CUSTOM_FRAGMENT] [--custom-query-string CUSTOM_QUERY_STRING]')

    # pylint: disable=line-too-long
    if (route_type == 'Forward' and any([custom_host, custom_path, custom_fragment, custom_query_string]) and getattr(redirect_type, 'is_default', None) and getattr(redirect_protocol, 'is_default', None)):
        from knack.util import CLIError
        raise CLIError(forwarding_usage)
    if route_type == 'Redirect' and any([custom_forwarding_path, forwarding_protocol, backend_pool,
                                         query_parameter_strip_directive, dynamic_compression]):
        from knack.util import CLIError
        raise CLIError(redirect_usage)

    if route_type == 'Forward':
        rule = RoutingRule(
            name=item_name,
            enabled_state='Disabled' if disabled else 'Enabled',
            frontend_endpoints=[SubResource(id=x) for x in frontend_endpoints] if frontend_endpoints else None,
            accepted_protocols=accepted_protocols or ['Http'],
            patterns_to_match=patterns_to_match or ['/*'],
            route_configuration=ForwardingConfiguration(
                custom_forwarding_path=custom_forwarding_path,
                forwarding_protocol=forwarding_protocol,
                backend_pool=SubResource(id=backend_pool) if backend_pool else None,
                cache_configuration=CacheConfiguration(
                    query_parameter_strip_directive=query_parameter_strip_directive,
                    dynamic_compression=dynamic_compression
                ) if caching else None
            )
        )
    elif route_type == 'Redirect':
        rule = RoutingRule(
            name=item_name,
            enabled_state='Disabled' if disabled else 'Enabled',
            frontend_endpoints=[SubResource(id=x) for x in frontend_endpoints] if frontend_endpoints else None,
            accepted_protocols=accepted_protocols or ['Http'],
            patterns_to_match=patterns_to_match or ['/*'],
            route_configuration=RedirectConfiguration(
                redirect_type=redirect_type,
                redirect_protocol=redirect_protocol,
                custom_host=custom_host,
                custom_path=custom_path,
                custom_fragment=custom_fragment,
                custom_query_string=custom_query_string
            )
        )
    return _upsert_frontdoor_subresource(cmd, resource_group_name, front_door_name, 'routing_rules', rule, 'name')


def update_fd_routing_rules(instance, frontend_endpoints=None, accepted_protocols=None, patterns_to_match=None,
                            custom_forwarding_path=None, forwarding_protocol=None, backend_pool=None, enabled=None,
                            dynamic_compression=None, query_parameter_strip_directive=None):
    from azext_front_door.vendored_sdks.models import SubResource
    with UpdateContext(instance) as c:
        c.update_param('frontend_endpoints', [SubResource(id=x) for x in frontend_endpoints]
                       if frontend_endpoints else None, False)
        c.update_param('accepted_protocols', accepted_protocols, False)
        c.update_param('patterns_to_match', patterns_to_match, False)
        c.update_param('custom_forwarding_path', custom_forwarding_path, False)
        c.update_param('forwarding_protocol', forwarding_protocol, False)
        c.update_param('backend_pool', SubResource(id=backend_pool) if backend_pool else None, False)
        c.update_param('enabled_state', enabled, False)
    with UpdateContext(instance.cache_configuration) as c:
        c.update_param('dynamic_compression', dynamic_compression, False)
        c.update_param('query_parameter_strip_directive', query_parameter_strip_directive, False)
    return instance
# endregion


# region WafPolicy
def create_waf_policy(cmd, resource_group_name, policy_name,
                      disabled=False, mode=None, redirect_url=None,
                      custom_block_response_status_code=None,
                      custom_block_response_body=None, tags=None):
    client = cf_waf_policies(cmd.cli_ctx, None)
    from azext_front_door.vendored_sdks.models import (
        WebApplicationFirewallPolicy, ManagedRuleSetList, PolicySettings, CustomRuleList)
    policy = WebApplicationFirewallPolicy(
        location='global',
        tags=tags,
        policy_settings=PolicySettings(
            enabled_state='Enabled' if not disabled else 'Disabled',
            mode=mode,
            redirect_url=redirect_url,
            custom_block_response_status_code=custom_block_response_status_code,
            custom_block_response_body=custom_block_response_body
        ),
        custom_rules=CustomRuleList(rules=[]),
        managed_rules=ManagedRuleSetList(rule_sets=[])
    )
    return client.create_or_update(resource_group_name, policy_name, policy)


def update_waf_policy(instance, tags=None, mode=None, redirect_url=None,
                      custom_block_response_status_code=None, custom_block_response_body=None,
                      disabled=False):
    with UpdateContext(instance) as c:
        c.update_param('tags', tags, True)

    with UpdateContext(instance.policy_settings) as c:
        c.update_param('enabled_state', 'Enabled' if not disabled else 'Disabled', 'Disabled')
        c.update_param('mode', mode, False)
        c.update_param('redirect_url', redirect_url, None)
        c.update_param('custom_block_response_status_code', custom_block_response_status_code, None)
        c.update_param('custom_block_response_body', custom_block_response_body, None)
    return instance


def add_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type, version):
    from azext_front_door.vendored_sdks.models import ManagedRuleSet
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)
    rule_set = ManagedRuleSet(
        rule_set_type=rule_set_type,
        rule_set_version=version
    )

    policy_rule_sets = policy.managed_rules.managed_rule_sets
    if policy_rule_sets is None:
        policy.managed_rules.managed_rule_sets = [rule_set]
    else:
        found = False
        for i in range(len(policy_rule_sets)):
            if policy_rule_sets[i].rule_set_type.upper() == rule_set_type.upper():
                policy_rule_sets[i] = rule_set
                found = True
                break
        if not found:
            policy_rule_sets.append(rule_set)

    return client.create_or_update(resource_group_name, policy_name, policy)


def list_azure_managed_rule_set(cmd, resource_group_name, policy_name):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)
    return policy.managed_rules.managed_rule_sets


def remove_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)

    policy.managed_rules.managed_rule_sets = [x for x in policy.managed_rules.managed_rule_sets
                                              if x.rule_set_type.upper() != rule_set_type.upper()]

    return client.create_or_update(resource_group_name, policy_name, policy)


def add_override_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type,
                                        rule_group_id, rule_id, action=None, disabled=None):
    from azext_front_door.vendored_sdks.models import ManagedRuleOverride, ManagedRuleGroupOverride
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)
    override = ManagedRuleOverride(
        rule_id=rule_id,
        action=action,
        enabled_state='Enabled' if not disabled else 'Disabled',
    )

    setRule = False
    # Find the matching rule_set to put the override in, or fail
    if policy.managed_rules.managed_rule_sets is None:
        policy.managed_rules.managed_rule_sets = []
    for rule_set in policy.managed_rules.managed_rule_sets:
        if rule_set.rule_set_type.upper() == rule_set_type.upper():
            if rule_set.rule_group_overrides is None:
                rule_set.rule_group_overrides = []
            for rg in rule_set.rule_group_overrides:
                if rg.rule_group_name.upper() == rule_group_id.upper():
                    if rg.rules is None:
                        rg.rules = []
                    for j, rule in enumerate(rg.rules):
                        if rule.rule_id.upper() == rule_id.upper():
                            rg.rules[j] = override
                            setRule = True
                    if not setRule:
                        rg.rules.append(override)
                        setRule = True
            if not setRule:
                rule_set.rule_group_overrides.append(ManagedRuleGroupOverride(
                    rule_group_name=rule_group_id,
                    rules=[override]
                ))
                setRule = True

    if not setRule:
        from knack.util import CLIError
        raise CLIError("type '{}' not found".format(rule_set_type))
    return client.create_or_update(resource_group_name, policy_name, policy)


def remove_override_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type,
                                           rule_group_id, rule_id):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)

    removedRule = False
    # Find the matching rule_set to put the override in, or fail
    if policy.managed_rules.managed_rule_sets is None:
        policy.managed_rules.managed_rule_sets = []
    for rule_set in policy.managed_rules.managed_rule_sets:
        if rule_set.rule_set_type.upper() == rule_set_type.upper():
            if rule_set.rule_group_overrides is None:
                rule_set.rule_group_overrides = []
            for i, rg in enumerate(rule_set.rule_group_overrides):
                if rg.rule_group_name.upper() == rule_group_id.upper():
                    if rg.rules is None:
                        rg.rules = []
                    for j, rule in enumerate(rg.rules):
                        if rule.rule_id.upper() == rule_id.upper():
                            del rg.rules[j]
                            if not rg.rules:
                                del rule_set.rule_group_overrides[i]
                            removedRule = True

    if not removedRule:
        from knack.util import CLIError
        raise CLIError("rule '{}' not found".format(rule_id))
    return client.create_or_update(resource_group_name, policy_name, policy)


def list_override_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)

    # Find the matching rule_set, or fail
    if policy.managed_rules.managed_rule_sets is None:
        policy.managed_rules.managed_rule_sets = []
    for rule_set in policy.managed_rules.managed_rule_sets:
        if rule_set.rule_set_type.upper() == rule_set_type.upper():
            return rule_set.rule_group_overrides

    from knack.util import CLIError
    raise CLIError("rule set '{}' not found".format(rule_set_type))


def add_exclusion_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type,
                                         match_variable, operator, value,
                                         rule_group_id=None, rule_id=None):
    from azext_front_door.vendored_sdks.models import ManagedRuleOverride, ManagedRuleGroupOverride
    from azext_front_door.vendored_sdks.models import ManagedRuleExclusion
    from knack.util import CLIError

    if rule_id and not rule_group_id:
        raise CLIError("Must specify rule-group-id of the rule when you specify rule-id")

    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)
    exclusion = ManagedRuleExclusion(
        match_variable=match_variable,
        selector_match_operator=operator,
        selector=value
    )

    rule_set_obj = None
    exclusion_holder = None

    # Find the matching rule_set to put the exclusion in, or fail
    policy.managed_rules.managed_rule_sets = policy.managed_rules.managed_rule_sets or []

    for rule_set in policy.managed_rules.managed_rule_sets:
        if rule_set.rule_set_type.upper() == rule_set_type.upper():
            rule_set_obj = rule_set
            break

    if rule_set_obj is None:
        raise CLIError("type '{}' not found".format(rule_set_type))

    rule_group_override = None
    if rule_group_id is None:
        exclusion_holder = rule_set_obj
    else:
        rule_set_obj.rule_group_overrides = rule_set_obj.rule_group_overrides or []
        for rg in rule_set_obj.rule_group_overrides:
            if rg.rule_group_name.upper() == rule_group_id.upper():
                rule_group_override = rg
                break
        if rule_group_override is None:
            rule_group_override = ManagedRuleGroupOverride(
                rule_group_name=rule_group_id)
            rule_set_obj.rule_group_overrides.append(rule_group_override)

    if rule_group_override is not None:
        if rule_id is None:
            exclusion_holder = rule_group_override
        else:
            rule_group_override.rules = rule_group_override.rules or []
            for rule in rule_group_override.rules:
                if rule.rule_id.upper() == rule_id.upper():
                    exclusion_holder = rule
            if not exclusion_holder:
                exclusion_holder = ManagedRuleOverride(
                    rule_id=rule_id
                )
                rule_group_override.rules.append(exclusion_holder)

    if exclusion_holder:
        if not exclusion_holder.exclusions:
            exclusion_holder.exclusions = []
        exclusion_holder.exclusions.append(exclusion)
    else:
        if rule_id:
            raise CLIError("rule {} within group {} within type '{}' not found"
                           .format(rule_id, rule_group_id, rule_set_type))
        raise CLIError("group {} within type '{}' not found".format(rule_group_id, rule_set_type))

    return client.create_or_update(resource_group_name, policy_name, policy)


def remove_exclusion_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type,
                                            match_variable, operator, value,
                                            rule_group_id=None, rule_id=None):
    from knack.util import CLIError

    if rule_id and not rule_group_id:
        raise CLIError("Must specify rule-group-id of the rule when you specify rule-id")

    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)

    exclusions = None

    if not policy.managed_rules.managed_rule_sets:
        raise CLIError("Exclusion not found")

    rule_set_obj = None
    for rule_set in policy.managed_rules.managed_rule_sets:
        if rule_set.rule_set_type.upper() == rule_set_type.upper():
            rule_set_obj = rule_set
            break

    rule_group_override = None
    if rule_set_obj is not None:
        if rule_group_id is None:
            exclusions = rule_set_obj.exclusions
        else:
            if not rule_set_obj.rule_group_overrides:
                raise CLIError("Exclusion not found")
            for rg in rule_set_obj.rule_group_overrides:
                if rg.rule_group_name.upper() == rule_group_id.upper():
                    rule_group_override = rg
                    break

    if rule_group_override is not None:
        if rule_id is None:
            exclusions = rule_group_override.exclusions
        else:
            if rule_group_override.rules is None:
                raise CLIError("Exclusion not found")
            for rule in rule_group_override.rules:
                if rule.rule_id.upper() == rule_id.upper():
                    exclusions = rule.exclusions
                    break

    if exclusions is None:
        raise CLIError("Exclusion not found")

    for i, exclusion in enumerate(exclusions):
        if (exclusion.match_variable == match_variable and
                exclusion.selector_match_operator == operator and exclusion.selector == value):
            del exclusions[i]

    return client.create_or_update(resource_group_name, policy_name, policy)


def list_exclusion_azure_managed_rule_set(cmd, resource_group_name, policy_name, rule_set_type,
                                          rule_group_id=None, rule_id=None):
    from knack.util import CLIError

    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)

    if rule_id and not rule_group_id:
        raise CLIError("Must specify rule-group-id of the rule when you specify rule-id")

    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)

    if policy.managed_rules.managed_rule_sets is None:
        raise CLIError("rule set '{}' not found".format(rule_set_type))

    rule_set_obj = None
    for rule_set in policy.managed_rules.managed_rule_sets:
        if rule_set.rule_set_type.upper() == rule_set_type.upper():
            if rule_group_id is None:
                return rule_set.exclusions or []
            rule_set_obj = rule_set
            break

    if rule_set_obj is None:
        raise CLIError("rule set '{}' not found".format(rule_set_type))

    if rule_set_obj.rule_group_overrides is None:
        raise CLIError("rule set '{}' has no overrides".format(rule_set_type))

    rule_group_override = None
    for rg in rule_set_obj.rule_group_overrides:
        if rg.rule_group_name.upper() == rule_group_id.upper():
            if rule_id is None:
                return rg.exclusions or []

            rule_group_override = rg
            break

    if rule_group_override is None:
        raise CLIError("rule group '{}' not found".format(rule_group_id))

    if rule_group_override.rules is None:
        raise CLIError("rule '{}' not found".format(rule_id))

    for rule in rule_group_override.rules:
        if rule.rule_id.upper() == rule_id.upper():
            return rule.exclusions or []

    raise CLIError("rule '{}' not found".format(rule_id))


def list_managed_rules_definitions(cmd):
    client = cf_waf_managed_rules(cmd.cli_ctx, None)
    definitions = client.list()
    return definitions


def create_wp_custom_rule(cmd, resource_group_name, policy_name, rule_name, priority, rule_type, action,
                          rate_limit_duration=None, rate_limit_threshold=None, disabled=None):
    if rule_type.lower() == "ratelimitrule" and (rate_limit_duration is None or rate_limit_threshold is None):
        from knack.util import CLIError
        raise CLIError("rate_limit_duration and rate_limit_threshold are required for a RateLimitRule")

    from azext_front_door.vendored_sdks.models import CustomRule
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)
    rule = CustomRule(
        name=rule_name,
        priority=priority,
        rule_type=rule_type,
        action=action,
        match_conditions=[],
        rate_limit_duration_in_minutes=rate_limit_duration,
        rate_limit_threshold=rate_limit_threshold,
        enabled_state='Enabled' if not disabled else 'Disabled'
    )
    policy.custom_rules.rules.append(rule)
    return cached_put(cmd, client.create_or_update, policy, resource_group_name, policy_name).result()


def update_wp_custom_rule(cmd, resource_group_name, policy_name, rule_name, priority=None, action=None,
                          rate_limit_duration=None, rate_limit_threshold=None, disabled=None):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)

    foundRule = False
    for rule in policy.custom_rules.rules:
        if rule.name.lower() == rule_name.lower():
            foundRule = True
            with UpdateContext(rule) as c:
                c.update_param('priority', priority, None)
                c.update_param('action', action, None)
                c.update_param('rate_limit_duration', rate_limit_duration, None)
                c.update_param('rate_limit_threshold', rate_limit_threshold, None)
                c.update_param('enabled_state', 'Enabled' if not disabled else 'Disabled', 'Disabled')

    if not foundRule:
        from knack.util import CLIError
        raise CLIError("rule '{}' not found".format(rule_name))

    return cached_put(cmd, client.create_or_update, policy, resource_group_name, policy_name).result()


def delete_wp_custom_rule(cmd, resource_group_name, policy_name, rule_name):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = client.get(resource_group_name, policy_name)
    policy.custom_rules.rules = [x for x in policy.custom_rules.rules if x.name.lower() != rule_name.lower()]
    return client.create_or_update(resource_group_name, policy_name, policy)


def list_wp_custom_rules(cmd, resource_group_name, policy_name):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)
    return policy.custom_rules.rules


def show_wp_custom_rule(cmd, resource_group_name, policy_name, rule_name):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)
    try:
        return next(x for x in policy.custom_rules.rules if x.name.lower() == rule_name.lower())
    except StopIteration:
        from knack.util import CLIError
        raise CLIError("rule '{}' not found".format(rule_name))


def remove_custom_rule_match_condition(cmd, resource_group_name, policy_name, rule_name,
                                       index):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)

    foundRule = False
    for rule in policy.custom_rules.rules:
        if rule.name.upper() == rule_name.upper():
            foundRule = True

            if index >= len(rule.match_conditions):
                from knack.util import CLIError
                raise CLIError("Index out of bounds")

            rule.match_conditions = [v for (i, v) in enumerate(rule.match_conditions) if i != index]

    if not foundRule:
        from knack.util import CLIError
        raise CLIError("rule '{}' not found".format(rule_name))

    return cached_put(cmd, client.create_or_update, policy, resource_group_name, policy_name).result()


def add_custom_rule_match_condition(cmd, resource_group_name, policy_name, rule_name,
                                    match_variable, operator, values, negate=None, transforms=None):
    from azext_front_door.vendored_sdks.models import MatchCondition
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)

    foundRule = False
    for rule in policy.custom_rules.rules:
        if rule.name.upper() == rule_name.upper():
            foundRule = True

            selector = None
            variable_parts = match_variable.split('.')
            if len(variable_parts) == 2:
                match_variable = variable_parts[0]
                selector = variable_parts[1]

            rule.match_conditions.append(MatchCondition(
                match_variable=match_variable,
                selector=selector,
                operator=operator,
                negate_condition=negate,
                match_value=values,
                transforms=transforms
            ))

    if not foundRule:
        from knack.util import CLIError
        raise CLIError("rule '{}' not found".format(rule_name))

    return cached_put(cmd, client.create_or_update, policy, resource_group_name, policy_name).result()


def list_custom_rule_match_conditions(cmd, resource_group_name, policy_name, rule_name):
    client = cf_waf_policies(cmd.cli_ctx, None)
    policy = cached_get(cmd, client.get, resource_group_name, policy_name)

    for rule in policy.custom_rules.rules:
        if rule.name.upper() == rule_name.upper():
            return rule.match_conditions

    from knack.util import CLIError
    raise CLIError("rule '{}' not found".format(rule_name))
# endregion
