# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Dict
from azure.cli.core.azclierror import ValidationError
from knack.log import get_logger
from ._clients import ContainerAppPreviewClient, DaprComponentPreviewClient
from ._client_factory import handle_non_404_status_code_exception
from ._models import (
    DaprComponent as DaprComponentModel,
    DaprMetadata as DaprMetadataModel,
    DaprServiceComponentBinding as DaprServiceComponentBindingModel,
)

logger = get_logger(__name__)

DAPRCOMPONENTINIT_SERVICEBIND_METADATA_CREATEDBY_KEY = "DCI_SB_CREATED_BY"
DAPRCOMPONENTINIT_SERVICEBIND_METADATA_CREATEDBY_VALUE = "azcli_azext_containerapp_daprutils"


class DaprUtils:
    supported_dapr_components = {
        # All state stores should support actors.
        "state": ["redis", "postgres"],
        "pubsub": ["kafka", "redis"],
    }

    @staticmethod
    def _get_supported_services() -> Dict:
        """
        Get the supported services for Dapr along with the create function for each service.
        """
        from .custom import (
            create_redis_service,
            create_postgres_service,
            create_kafka_service,
        )

        return {
            "redis": create_redis_service,
            "postgres": create_postgres_service,
            "kafka": create_kafka_service,
        }

    @staticmethod
    def _get_service_name(service_type: str) -> str:
        """
        Get the service name for the given service type.
        """
        return f"dapr-{service_type}"

    @staticmethod
    def _get_dapr_component_name(component_type: str) -> str:
        """
        Get the Dapr component name for the given component type.

        :param component_type: type of the Dapr component to create, e.g. state or pubsub

        :return: Dapr component name
        """
        return "statestore" if component_type == "state" else component_type

    @staticmethod
    def _get_dapr_component_model_from_service(
        component_type: str,
        service_type: str,
        service_name: str,
        service_id: str,
        component_version: str = "v1",
        component_ignore_errors: bool = False,
        component_metadata: Dict[str, str] = None,
    ):
        """
        Get the Dapr component model for the given component type and service type.

        :param component_type: type of the Dapr component to create, e.g. state or pubsub
        :param service_type: type of the service to create, e.g. redis or kafka
        :param service_name: name of the service to create, e.g. dapr-redis
        :param service_id: id of the service to create, e.g. /subscriptions/.../dapr-redis
        :param component_version: version of the Dapr component to create, e.g. v1
        :param component_ignore_errors: whether to ignore errors when Dapr loads the component
        :param component_metadata: metadata to add to the Dapr component, e.g. {"key": "value"}

        :return: Dapr component model for the component
        """
        serviceBinding = DaprServiceComponentBindingModel.copy()
        serviceBinding["name"] = service_name
        serviceBinding["serviceId"] = service_id
        serviceBinding["metadata"] = {
            DAPRCOMPONENTINIT_SERVICEBIND_METADATA_CREATEDBY_KEY: DAPRCOMPONENTINIT_SERVICEBIND_METADATA_CREATEDBY_VALUE
        }

        metadata_items = []
        if component_metadata:
            for metadata_key, metadata_value in component_metadata.items():
                metadata_item = DaprMetadataModel.copy()
                metadata_item["name"] = metadata_key
                metadata_item["value"] = metadata_value
                metadata_items.append(metadata_item)

        component = DaprComponentModel.copy()
        component["properties"]["componentType"] = f"{component_type}.{service_type}"
        component["properties"]["version"] = component_version
        component["properties"]["ignoreErrors"] = component_ignore_errors
        component["properties"]["serviceComponentBind"] = serviceBinding
        component["properties"]["metadata"] = metadata_items

        return component

    @staticmethod
    def _is_component_created_by_daprcomponentinit(component_def) -> bool:
        """
        Check if the component was created by dapr-component init.

        :param component_def: component definition to check

        :return: True if the component was created by DaprUtils, False otherwise
        """
        from azure.cli.command_modules.containerapp._utils import safe_get

        if component_def is None:
            raise ValidationError("Component definition cannot be None.")

        service_binding_metadata_created_by = safe_get(
            component_def,
            "properties",
            "serviceComponentBind",
            "metadata",
            DAPRCOMPONENTINIT_SERVICEBIND_METADATA_CREATEDBY_KEY,
        )

        # If the component was created by dapr-component init, it will have the metadata key.
        # This can be created by the CLI or another source (like portal), so we skip the check for the value.
        if service_binding_metadata_created_by is not None:
            return True

        return False

    @staticmethod
    def create_dapr_component_with_service_binding(
        cmd,
        component_name: str,
        component_type: str,
        service_type: str,
        service_name: str,
        service_id: str,
        resource_group_name: str,
        environment_name: str,
        component_metadata: Dict[str, str] = None,
    ):
        """
        Create a Dapr component with a service binding if it does not exist.

        :param component_name: name of the Dapr component to create, e.g. statestore-redis
        :param component_type: type of the Dapr component to create, e.g. state or pubsub
        :param service_type: type of the service to bind to, e.g. redis or kafka
        :param service_name: name of the service to bind to, e.g. dapr-redis
        :param service_id: id of the service to bind to, e.g. /subscriptions/.../dapr-redis
        :param component_metadata: metadata to add to the Dapr component, e.g. {"key": "value"}

        :return: Dapr component definition of the component (whether it was created or not)
        """
        if (
            component_type not in DaprUtils.supported_dapr_components
            or service_type not in DaprUtils.supported_dapr_components[component_type]
        ):
            raise ValidationError(
                f"Dapr component type {component_type} with service type {service_type} is not supported."
            )

        # Check if the component already exists.
        logger.debug("Looking up Dapr component %s", component_name)
        component_def = None
        try:
            component_def = DaprComponentPreviewClient.show(
                cmd, resource_group_name, environment_name, component_name
            )
        except Exception as e:  # pylint: disable=broad-except
            handle_non_404_status_code_exception(e)

        # Throw an error if the component already exists, and was not created by the init command.
        # This is to prevent users from accidentally overwriting components that they have created.
        if component_def and not DaprUtils._is_component_created_by_daprcomponentinit(
            component_def
        ):
            raise ValidationError(
                f"Dapr component {component_name} already exists and cannot be overwritten."
                " Please delete the component and try again."
            )

        # Create the component.
        logger.debug("Creating Dapr component %s", component_name)
        component_model = DaprUtils._get_dapr_component_model_from_service(
            component_type,
            service_type,
            service_name,
            service_id,
            component_metadata=component_metadata,
        )
        try:
            component_def = DaprComponentPreviewClient.create_or_update(
                cmd,
                resource_group_name,
                environment_name,
                component_name,
                component_model,
            )
        except Exception as e:
            raise ValidationError(
                f"Failed to create Dapr component {component_name}: {e}"
            ) from e

        if component_def is None:
            raise ValidationError(
                f"Failed to create Dapr component {component_name}, component definition is None"
            )

        logger.debug("Successfully created Dapr component %s", component_name)
        return component_def

    @staticmethod
    def _create_service(
        cmd,
        service_type: str,
        service_name: str,
        resource_group_name: str,
        environment_name: str,
    ):
        """
        Create a service if it does not exist.

        :param service_type: type of the service to create, e.g. redis
        :param service_name: name of the service to create, e.g. dapr-redis

        :return: service definition of the service (whether it was created or not)
        """
        supported_services = DaprUtils._get_supported_services()
        if service_type not in supported_services:
            raise ValidationError(f"Service type {service_type} is not supported.")

        # Look up the service, if it already exists, return it.
        logger.debug("Looking up service %s of type %s", service_name, service_type)
        service_def = None
        try:
            service_def = ContainerAppPreviewClient.show(
                cmd, resource_group_name, service_name
            )
        except Exception as e:  # pylint: disable=broad-except
            handle_non_404_status_code_exception(e)

        if service_def is not None:
            logger.warning(
                "Service %s of type %s already exists, skipping creation",
                service_name,
                service_type,
            )
            return service_def

        # Create the service.
        logger.debug("Creating service %s of type %s", service_name, service_type)
        create_service_func = supported_services[service_type]

        try:
            service_def = create_service_func(
                cmd, service_name, environment_name, resource_group_name
            )
        except Exception as e:
            raise ValidationError(
                f"Failed to create service {service_name} of type {service_type}: {e}"
            ) from e

        if service_def is None:
            raise ValidationError(
                f"Failed to create service {service_name} of type {service_type}, service definition is None"
            )

        logger.debug(
            "Successfully created service %s of type %s", service_name, service_type
        )
        return service_def

    @staticmethod
    def create_dapr_component_with_service(
        cmd,
        component_type: str,
        service_type: str,
        resource_group_name: str,
        environment_name: str,
        service_id: str = None,
        component_metadata: Dict[str, str] = None,
    ) -> [str, str, str, str]:
        """
        Create a Dapr component and an associated service if they do not exist.
        If the service id is provided, use it instead of creating a new service.

        :param component_type: type of the Dapr component to create, e.g. state or pubsub
        :param service_type: type of the service to create, e.g. redis or kafka
        :param service_id: id of an existing service to use, e.g. /subscriptions/.../dapr-redis
        :param component_metadata: metadata to add to the Dapr component, e.g. {"key": "value"}

        :return: service id, component id
        """
        from azure.cli.command_modules.containerapp._utils import safe_get

        service_name = DaprUtils._get_service_name(service_type)
        if service_id is None:
            # Create the service.
            service_def = DaprUtils._create_service(
                cmd, service_type, service_name, resource_group_name, environment_name
            )
            service_id = safe_get(service_def, "id", default=None)
            if service_id is None:
                raise ValidationError(
                    f"Failed to create service {service_name} of type {service_type}, service id is None"
                )

        # Create the Dapr component.
        component_name = DaprUtils._get_dapr_component_name(component_type)
        component_def = DaprUtils.create_dapr_component_with_service_binding(
            cmd,
            component_name,
            component_type,
            service_type,
            service_name,
            service_id,
            resource_group_name,
            environment_name,
            component_metadata=component_metadata,
        )
        component_id = safe_get(component_def, "id", default=None)
        if component_id is None:
            raise ValidationError(
                f"Failed to create Dapr component of type {component_type} with service type {service_type}"
                ", component id is None"
            )

        return service_id, component_id
