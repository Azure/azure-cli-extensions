# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
# pylint: disable=unused-argument, logging-format-interpolation, protected-access, wrong-import-order, too-many-lines
from ._utils import (wait_till_end, _get_rg_location)
from .vendored_sdks.appplatform.v2022_01_01_preview import models
from knack.log import get_logger
from .custom import (_warn_enable_java_agent, _update_application_insights_asc_create)
from ._build_service import _update_default_build_agent_pool
from .buildpack_binding import create_default_buildpack_binding_for_application_insights
from ._tanzu_component import (create_application_configuration_service,
                               create_service_registry,
                               create_gateway,
                               create_api_portal)


from ._validators import (_parse_sku_name)
from knack.log import get_logger

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
                       zone_redundant=False,
                       sku=None,
                       tags=None,
                       **_):
        properties = models.ClusterResourceProperties(
            zone_redundant=zone_redundant
        )

        if service_runtime_subnet or app_subnet or reserved_cidr_range:
            properties.network_profile = models.NetworkProfile(
                service_runtime_subnet_id=service_runtime_subnet,
                app_subnet_id=app_subnet,
                service_cidr=reserved_cidr_range,
                app_network_resource_group=app_network_resource_group,
                service_runtime_network_resource_group=service_runtime_network_resource_group
            )

        resource = models.ServiceResource(location=self.location, sku=sku, properties=properties, tags=tags)
        poller = self.client.services.begin_create_or_update(
            self.resource_group, self.name, resource)
        logger.warning(" - Creating Service ..")
        wait_till_end(self.cmd, poller)
        return poller


class EnterpriseSpringCloud(DefaultSpringCloud):
    def before_create(self, **_):
        pass

    def after_create(self, no_wait=None, **kwargs):
        pollers = [
            # create sub components like Service registry, ACS, build service, etc.
            _update_default_build_agent_pool(
                self.cmd, self.client, self.resource_group, self.name, kwargs['build_pool_size']),
            _enable_app_insights(self.cmd, self.client, self.resource_group, self.name, self.location, **kwargs),
            create_application_configuration_service(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_service_registry(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_gateway(self.cmd, self.client, self.resource_group, self.name, **kwargs),
            create_api_portal(self.cmd, self.client, self.resource_group, self.name, **kwargs)
        ]
        pollers = [x for x in pollers if x]
        if not no_wait:
            wait_till_end(self.cmd, *pollers)


def _get_factory(cmd, client, resource_group, name, location=None, sku=None):
    if _parse_sku_name(sku) == 'enterprise':
        return EnterpriseSpringCloud(cmd, client, resource_group, name, location)
    return DefaultSpringCloud(cmd, client, resource_group, name, location)


def spring_cloud_create(cmd, client, resource_group, name,
                        location=None,
                        vnet=None,
                        service_runtime_subnet=None,
                        app_subnet=None,
                        reserved_cidr_range=None,
                        service_runtime_network_resource_group=None,
                        app_network_resource_group=None,
                        app_insights_key=None,
                        app_insights=None,
                        sampling_rate=None,
                        disable_app_insights=None,
                        enable_java_agent=None,
                        sku=None,
                        tags=None,
                        zone_redundant=False,
                        build_pool_size=None,
                        enable_application_configuration_service=False,
                        enable_service_registry=False,
                        enable_gateway=False,
                        gateway_instance_count=None,
                        enable_api_portal=False,
                        api_portal_instance_count=None,
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
        'app_insights_key': app_insights_key,
        'app_insights': app_insights,
        'sampling_rate': sampling_rate,
        'disable_app_insights': disable_app_insights,
        'enable_java_agent': enable_java_agent,
        'sku': sku,
        'tags': tags,
        'zone_redundant': zone_redundant,
        'build_pool_size': build_pool_size,
        'enable_application_configuration_service': enable_application_configuration_service,
        'enable_service_registry': enable_service_registry,
        'enable_gateway': enable_gateway,
        'gateway_instance_count': gateway_instance_count,
        'enable_api_portal': enable_api_portal,
        'api_portal_instance_count': api_portal_instance_count,
        'no_wait': no_wait
    }

    spring_cloud_factory = _get_factory(cmd, client, resource_group, name, location=location, sku=sku)
    return spring_cloud_factory.create(**kwargs)


def _enable_app_insights(cmd, client, resource_group, name, location, app_insights_key, app_insights,
                         sampling_rate, disable_app_insights, **_):
    if disable_app_insights:
        return

    return create_default_buildpack_binding_for_application_insights(cmd, client, resource_group, name,
                                                                     location, app_insights_key, app_insights,
                                                                     sampling_rate)
