# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from ._utils import (wait_till_end, _get_rg_location, register_provider_if_needed)
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from .custom import (_warn_enable_java_agent, _update_application_insights_asc_create)
from ._build_service import _update_default_build_agent_pool, create_build_service
from .buildpack_binding import create_default_buildpack_binding_for_application_insights
from .apm import create_default_apm_for_application_insights
from ._tanzu_component import (create_application_configuration_service,
                               create_application_live_view,
                               create_dev_tool_portal,
                               create_service_registry,
                               create_gateway,
                               create_api_portal,
                               create_application_accelerator)

from ._validators import (_parse_sku_name, validate_instance_not_existed)
from azure.cli.core.commands import LongRunningOperation
from knack.log import get_logger
from ._marketplace import _spring_list_marketplace_plan
from ._constant import (MARKETPLACE_OFFER_ID, MARKETPLACE_PUBLISHER_ID, AKS_RP)

logger = get_logger(__name__)


class DefaultSpringCloud:
    def __init__(self, cmd, client, resource_group, name, location=None, **_):
        self.cmd = cmd
        self.client = client
        self.resource_group = resource_group
        self.name = name
        self.location = location or _get_rg_location(cmd.cli_ctx, resource_group)

    def create(self, **kwargs):
        self.before_create(**kwargs)
        resource = self.create_service(**kwargs)
        self.after_create(**kwargs)
        return resource

    def before_create(self, **kwargs):
        _warn_enable_java_agent(**kwargs)
        validate_instance_not_existed(self.client,
                                      self.name,
                                      self.location)

    def after_create(self, **kwargs):
        _update_application_insights_asc_create(self.cmd,
                                                self.resource_group,
                                                self.name,
                                                self.location,
                                                **kwargs)

    def create_service(self,
                       service_runtime_subnet=None,
                       app_subnet=None,
                       reserved_cidr_range=None,
                       service_runtime_network_resource_group=None,
                       app_network_resource_group=None,
                       outbound_type=None,
                       enable_log_stream_public_endpoint=None,
                       enable_dataplane_public_endpoint=None,
                       zone_redundant=False,
                       sku=None,
                       tags=None,
                       ingress_read_timeout=None,
                       marketplace_plan_id=None,
                       managed_environment=None,
                       infra_resource_group=None,
                       **_):
        properties = models.ClusterResourceProperties(
            zone_redundant=zone_redundant
        )

        if enable_log_stream_public_endpoint is not None or enable_dataplane_public_endpoint is not None:
            val = enable_log_stream_public_endpoint if enable_log_stream_public_endpoint is not None else \
                enable_dataplane_public_endpoint
            properties.vnet_addons = models.ServiceVNetAddons(
                data_plane_public_endpoint=val,
                log_stream_public_endpoint=val
            )
        else:
            properties.vnet_addons = None

        if marketplace_plan_id:
            properties.marketplace_resource = models.MarketplaceResource(
                plan=marketplace_plan_id,
                product=MARKETPLACE_OFFER_ID,
                publisher=MARKETPLACE_PUBLISHER_ID
            )

        if service_runtime_subnet or app_subnet or reserved_cidr_range:
            properties.network_profile = models.NetworkProfile(
                service_runtime_subnet_id=service_runtime_subnet,
                app_subnet_id=app_subnet,
                service_cidr=reserved_cidr_range,
                app_network_resource_group=app_network_resource_group,
                service_runtime_network_resource_group=service_runtime_network_resource_group,
                outbound_type=outbound_type
            )

        if ingress_read_timeout:
            ingress_configuration = models.IngressConfig(read_timeout_in_seconds=ingress_read_timeout)
            if properties.network_profile:
                properties.network_profile.ingress_config = ingress_configuration
            else:
                properties.network_profile = models.NetworkProfile(ingress_config=ingress_configuration)

        if sku.tier.upper() == 'STANDARDGEN2':
            properties.managed_environment_id = managed_environment
            if infra_resource_group is not None:
                properties.infra_resource_group = infra_resource_group

        resource = models.ServiceResource(location=self.location, sku=sku, properties=properties, tags=tags)
        poller = self.client.services.begin_create_or_update(
            self.resource_group, self.name, resource)
        logger.warning(" - Creating Service ..")
        return LongRunningOperation(self.cmd.cli_ctx)(poller)


class EnterpriseSpringCloud(DefaultSpringCloud):
    def before_create(self, **_):
        validate_instance_not_existed(self.client,
                                      self.name,
                                      self.location)

    def after_create(self, no_wait=None, **kwargs):
        # should create build service before creating build agent pool and app insights
        if not no_wait and not kwargs['disable_build_service']:
            poller = create_build_service(self.cmd, self.client, self.resource_group, self.name, kwargs['disable_build_service'],
                                          kwargs['registry_server'], kwargs['registry_username'], kwargs['registry_password'])
            LongRunningOperation(self.cmd.cli_ctx)(poller)
        pollers = [
            # create sub components like Service registry, ACS, build service, etc.
            _update_default_build_agent_pool(
                self.cmd, self.client, self.resource_group, self.name, kwargs['build_pool_size']),
            _enable_app_insights(self.cmd, self.client, self.resource_group, self.name, self.location, **kwargs),
            create_application_configuration_service(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_application_live_view(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_dev_tool_portal(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_service_registry(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_gateway(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_api_portal(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_application_accelerator(self.cmd, self.client, self.resource_group, self.name, **kwargs)
        ]
        pollers = [x for x in pollers if x]
        if not no_wait:
            wait_till_end(self.cmd, *pollers)


def _get_factory(cmd, client, resource_group, name, location=None, sku=None):
    if _parse_sku_name(sku) == 'enterprise':
        return EnterpriseSpringCloud(cmd, client, resource_group, name, location)
    return DefaultSpringCloud(cmd, client, resource_group, name, location)


def spring_create(cmd, client, resource_group, name,
                  location=None,
                  vnet=None,
                  service_runtime_subnet=None,
                  app_subnet=None,
                  reserved_cidr_range=None,
                  service_runtime_network_resource_group=None,
                  app_network_resource_group=None,
                  outbound_type=None,
                  app_insights_key=None,
                  app_insights=None,
                  sampling_rate=None,
                  disable_app_insights=None,
                  enable_java_agent=None,
                  sku=None,
                  tags=None,
                  zone_redundant=False,
                  build_pool_size=None,
                  disable_build_service=False,
                  registry_server=None,
                  registry_username=None,
                  registry_password=None,
                  enable_application_configuration_service=False,
                  application_configuration_service_generation=None,
                  enable_application_live_view=False,
                  enable_service_registry=False,
                  enable_gateway=False,
                  gateway_instance_count=None,
                  enable_api_portal=False,
                  api_portal_instance_count=None,
                  enable_application_accelerator=False,
                  enable_log_stream_public_endpoint=None,
                  enable_dataplane_public_endpoint=None,
                  ingress_read_timeout=None,
                  marketplace_plan_id=None,
                  managed_environment=None,
                  infra_resource_group=None,
                  no_wait=False):
    """
    Because Standard/Basic tier vs. Enterprise tier creation are very different. Here routes the command to different
    implementation according to --sku parameters.
    """
    kwargs = {
        'vnet': vnet,
        'service_runtime_subnet': service_runtime_subnet,
        'app_subnet': app_subnet,
        'reserved_cidr_range': reserved_cidr_range,
        'service_runtime_network_resource_group': service_runtime_network_resource_group,
        'app_network_resource_group': app_network_resource_group,
        'outbound_type': outbound_type,
        'app_insights_key': app_insights_key,
        'app_insights': app_insights,
        'sampling_rate': sampling_rate,
        'disable_app_insights': disable_app_insights,
        'enable_java_agent': enable_java_agent,
        'ingress_read_timeout': ingress_read_timeout,
        'sku': sku,
        'tags': tags,
        'zone_redundant': zone_redundant,
        'build_pool_size': build_pool_size,
        'disable_build_service': disable_build_service,
        'registry_server': registry_server,
        'registry_username': registry_username,
        'registry_password': registry_password,
        'enable_application_configuration_service': enable_application_configuration_service,
        'application_configuration_service_generation': application_configuration_service_generation,
        'enable_application_live_view': enable_application_live_view,
        'enable_service_registry': enable_service_registry,
        'enable_gateway': enable_gateway,
        'gateway_instance_count': gateway_instance_count,
        'enable_api_portal': enable_api_portal,
        'api_portal_instance_count': api_portal_instance_count,
        'enable_application_accelerator': enable_application_accelerator,
        'enable_log_stream_public_endpoint': enable_log_stream_public_endpoint,
        'enable_dataplane_public_endpoint': enable_dataplane_public_endpoint,
        'marketplace_plan_id': marketplace_plan_id,
        'managed_environment': managed_environment,
        'infra_resource_group': infra_resource_group,
        'no_wait': no_wait
    }

    if vnet:
        register_provider_if_needed(cmd, AKS_RP)

    spring_factory = _get_factory(cmd, client, resource_group, name, location=location, sku=sku)
    return spring_factory.create(**kwargs)


def _enable_app_insights(cmd, client, resource_group, name, location, app_insights_key, app_insights,
                         sampling_rate, disable_app_insights, **kwargs):
    if disable_app_insights:
        return

    if kwargs['disable_build_service'] or kwargs['registry_server']:
        return create_default_apm_for_application_insights(cmd, client, resource_group, name,
                                                           location, app_insights_key, app_insights,
                                                           sampling_rate)
    else:
        return create_default_buildpack_binding_for_application_insights(cmd, client, resource_group, name,
                                                                         location, app_insights_key, app_insights,
                                                                         sampling_rate)


def spring_list_marketplace_plan(cmd, client):
    return _spring_list_marketplace_plan(cmd, client)


def spring_list_support_server_versions(cmd, client, resource_group, service):
    return client.services.list_supported_server_versions(resource_group, service)
