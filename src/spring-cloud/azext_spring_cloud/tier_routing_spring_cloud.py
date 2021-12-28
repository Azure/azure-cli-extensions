# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
from ._validators import (_parse_sku_name)
from ._enterprise import (spring_cloud_create as create_enterprise)
from .custom import (spring_cloud_create as create_standard)
from knack.log import get_logger

logger = get_logger(__name__)


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
                        no_wait=False):
    """
    Because Standard/Basic tier vs. Enterprise tier creation are very different. Here routes the command to different
    implementation according to --sku parameters.
    """
    if _parse_sku_name(sku) == 'enterprise':
        return create_enterprise(cmd, client, resource_group, name,
                                 location=location,
                                 vnet=vnet,
                                 service_runtime_subnet=service_runtime_subnet,
                                 app_subnet=app_subnet,
                                 reserved_cidr_range=reserved_cidr_range,
                                 service_runtime_network_resource_group=service_runtime_network_resource_group,
                                 app_network_resource_group=app_network_resource_group,
                                 app_insights_key=app_insights_key,
                                 app_insights=app_insights,
                                 sampling_rate=sampling_rate,
                                 disable_app_insights=disable_app_insights,
                                 enable_java_agent=enable_java_agent,
                                 sku=sku,
                                 tags=tags,
                                 zone_redundant=zone_redundant,
                                 no_wait=no_wait)
    else:
        return create_standard(cmd, client, resource_group, name,
                               location=location,
                               vnet=vnet,
                               service_runtime_subnet=service_runtime_subnet,
                               app_subnet=app_subnet,
                               reserved_cidr_range=reserved_cidr_range,
                               service_runtime_network_resource_group=service_runtime_network_resource_group,
                               app_network_resource_group=app_network_resource_group,
                               app_insights_key=app_insights_key,
                               app_insights=app_insights,
                               sampling_rate=sampling_rate,
                               disable_app_insights=disable_app_insights,
                               enable_java_agent=enable_java_agent,
                               sku=sku,
                               tags=tags,
                               zone_redundant=zone_redundant,
                               no_wait=no_wait)
