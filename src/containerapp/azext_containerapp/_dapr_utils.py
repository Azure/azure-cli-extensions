# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Any
from azure.cli.core.azclierror import ValidationError
from knack.log import get_logger
from ._clients import ContainerAppClient
from ._constants import DAPR_REDIS_SECRET_NAME
from ._models import (DaprComponent as DaprComponentModel,
                      DaprMetadata as DaprMetadataModel)
from .custom import create_redis_service, _get_existing_secrets, safe_get

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
        except:
            pass

        if redis_capp_def is not None:
            logger.warning("Redis service '%s' already exists, skipping creation.", service_name)
            return redis_capp_def, False
        
        # Create Redis service
        logger.info("Creating Redis service '%s'...", service_name)
        try:
            redis_capp_def = create_redis_service(cmd, service_name, environment_name, resource_group_name)
        except Exception as e:
            raise ValidationError("Failed to create Redis service, error: {}".format(e)) from e
        
        if redis_capp_def is None:
            raise ValidationError("Failed to create Redis service, did not receive a response.")
        
        logger.info("Redis service '%s' created.", service_name)
        return redis_capp_def, True

    @staticmethod
    def get_redis_configuration(cmd, resource_group_name, service_name, redis_capp_def) -> dict:
        """Get Redis configuration from the Redis service secret."""
        # Load secrets into redis_capp_def
        _get_existing_secrets(cmd, resource_group_name, service_name, redis_capp_def)
        redis_secrets = safe_get(redis_capp_def, "properties", "configuration", "secrets", default=[])
        if len(redis_secrets) == 0:
            raise ValidationError("Failed to read redis configuration, no secrets found for Redis service.")

        redis_secret_value: str = None
        for secret in redis_secrets:
            if safe_get(secret, "name") == DAPR_REDIS_SECRET_NAME:
                redis_secret_value = safe_get(secret, "value")
                break

        if redis_secret_value is None:
            raise ValidationError(f"Failed to read redis configuration, {DAPR_REDIS_SECRET_NAME} secret not found for Redis service.")
                
        # Parse the secret value into key-value pairs. It is in the below format:
        # requirepass mypassword\ndir /mnt/data\nport 6379\nprotected-mode yes\nappendonly yes\n
        redis_config = {}
        for line in redis_secret_value.splitlines():
            idx = line.strip().find(" ")
            if idx == -1:
                continue
            redis_config[line[:idx]] = line[idx + 1:]

        return redis_config

    @staticmethod
    def get_dapr_redis_statestore_component(redis_host, redis_password):
        """Get Dapr Redis statestore component with given host and password."""
        component = DaprComponentModel.copy()
        component["properties"]["componentType"] = "state.redis"
        component["properties"]["version"] = "v1"
        component["properties"]["ignoreErrors"] = False
        component["properties"]["metadata"] = [
            DaprUtils._get_dapr_metadata_from_value("redisHost", redis_host),
            DaprUtils._get_dapr_metadata_from_value("redisPassword", redis_password)]

        return component

    @staticmethod
    def get_dapr_redis_pubsub_component(redis_host, redis_password):
        """Get Dapr Redis pubsub component with given host and password."""
        component = DaprComponentModel.copy()
        component["properties"]["componentType"] = "pubsub.redis"
        component["properties"]["version"] = "v1"
        component["properties"]["ignoreErrors"] = False
        component["properties"]["metadata"] = [
            DaprUtils._get_dapr_metadata_from_value("redisHost", redis_host),
            DaprUtils._get_dapr_metadata_from_value("redisPassword", redis_password)]

        return component

    @staticmethod
    def _get_dapr_metadata_from_value(name, value):
        """Get a Dapr metadata object with given name and value."""
        metadata = DaprMetadataModel.copy()
        metadata["name"] = name
        metadata["value"] = value
        return metadata