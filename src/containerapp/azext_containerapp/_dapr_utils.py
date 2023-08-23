# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any
from azure.cli.core.azclierror import ValidationError
from knack.log import get_logger
from ._clients import ContainerAppClient
from ._models import (DaprComponent as DaprComponentModel,
                      ServiceBinding as ServiceBindingModel)
from .custom import create_redis_service, safe_get

logger = get_logger(__name__)


class DaprUtils:
    """Utility class for Dapr related operations."""

    @staticmethod
    def create_redis_service_if_not_exists(cmd, resource_group_name, environment_name, service_name) -> (Any, bool):
        """Create a Redis service if it does not exist.
        Returns the service definition and a boolean indicating whether the service was created."""

        # Check if Redis service already exists
        logger.info("Looking up Redis service '%s'...", service_name)
        redis_capp_def = None
        try:
            redis_capp_def = ContainerAppClient.show(cmd, resource_group_name, service_name)
        except Exception:
            pass

        if redis_capp_def is not None:
            logger.warning("Redis service '%s' already exists, skipping creation.", service_name)
            return redis_capp_def, False

        # Create Redis service
        logger.info("Creating Redis service '%s'...", service_name)
        try:
            redis_capp_def = create_redis_service(cmd, service_name, environment_name, resource_group_name)
        except Exception as e:
            raise ValidationError(f"Failed to create Redis service, error: {e}") from e

        if redis_capp_def is None:
            raise ValidationError("Failed to create Redis service, did not receive a response.")

        logger.info("Redis service '%s' created.", service_name)
        return redis_capp_def, True

    @staticmethod
    def get_dapr_component_def_from_service(
        component_type: str,
        service_component_name: str,
        service_component_id: str,
        component_version: str = "v1",
        ignore_errors: bool = False):
        """Get a Dapr component with binding to a service.
        Returns the component definition.

        :param component_type: The type of the component, e.g. "state.redis".
        :param service_component_name: The name of the service component, e.g. "redis".
        :param service_component_id: The ARM ID of the service component, e.g. "/subscriptions/.../redis".
        :param component_version: The version of the component, e.g. "v1".
        :param ignore_errors: Whether to ignore errors while loading the component.
        """
        serviceBinding = ServiceBindingModel.copy()
        serviceBinding["name"] = service_component_name
        serviceBinding["serviceId"] = service_component_id

        component = DaprComponentModel.copy()
        component["properties"]["componentType"] = component_type
        component["properties"]["version"] = component_version
        component["properties"]["ignoreErrors"] = ignore_errors
        component["properties"]["serviceComponentBind"] = serviceBinding

        return component
