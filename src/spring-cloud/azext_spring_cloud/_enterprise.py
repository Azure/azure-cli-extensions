# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order

from knack.log import get_logger
from .custom import (_create_service)


logger = get_logger(__name__)


def spring_cloud_create(cmd, client, resource_group, name, location=None,
                        vnet=None, service_runtime_subnet=None, app_subnet=None, reserved_cidr_range=None,
                        service_runtime_network_resource_group=None, app_network_resource_group=None,
                        app_insights_key=None, app_insights=None, sampling_rate=None,
                        disable_app_insights=None, enable_java_agent=None,
                        sku=None, tags=None, no_wait=False):
    poller = _create_service(cmd, client, resource_group, name,
                             location=location,
                             service_runtime_subnet=service_runtime_subnet,
                             app_subnet=app_subnet,
                             reserved_cidr_range=reserved_cidr_range,
                             service_runtime_network_resource_group=service_runtime_network_resource_group,
                             app_network_resource_group=app_network_resource_group,
                             sku=sku,
                             tags=tags)
    return poller
