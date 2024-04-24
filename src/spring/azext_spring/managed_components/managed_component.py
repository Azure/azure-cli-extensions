# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger
from knack.util import CLIError
from azure.core.exceptions import ResourceNotFoundError
from ..application_configuration_service import DEFAULT_NAME as ACS_DEFAULT_NAME
from ..gateway import DEFAULT_NAME as SCG_DEFAULT_NAME


logger = get_logger(__name__)


# Acs
ACS = "application-configuration-service"
ACS_INSTANCE_PREFIX = "application-configuration-service"


# Flux
FLUX = "flux-source-controller"
FLUX_INSTANCE_PREFIX = "fluxcd-source-controller"


# Scg
SCG = "spring-cloud-gateway"


# Scg operator
SCG_OPERATOR = "spring-cloud-gateway-operator"


class ManagedComponentInstance:  # pylint: disable=too-few-public-methods
    def __init__(self, name):
        self.name = name


class ManagedComponent:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_api_name(self):
        return self._to_camel_case(self.name)

    def match(self, name):
        return name and self.name == name

    def match_ignore_case(self, name: str):
        return name and self.name.lower() == name.lower()

    def list_instances(self, client, resource_group, service):
        raise NotImplementedError("Must be implemented by child class.")

    def _to_camel_case(self, text):
        if text is None or len(text) == 0:
            return text

        s = text.replace("-", " ").replace("_", " ")
        s = s.split()

        if len(s) == 1:
            return s[0]

        return s[0] + ''.join(i.capitalize() for i in s[1:])


class Acs(ManagedComponent):
    def __init__(self):
        super().__init__(ACS)

    def list_instances(self, client, resource_group, service):
        try:
            return self._list_instances(client, resource_group, service)
        except ResourceNotFoundError:
            raise CLIError("'{}' is a subcomponent of Application Configuration Service (ACS), "
                           "failed to perform operations when ACS is not enabled.".format(self.name))

    def _list_instances(self, client, resource_group, service):
        acs_arm_resource = client.configuration_services.get(resource_group, service, ACS_DEFAULT_NAME)
        instance_array = acs_arm_resource.properties.instances
        instances = []
        for i in instance_array:
            if i.name.startswith(ACS_INSTANCE_PREFIX):
                instances.append(ManagedComponentInstance(i.name))
        if len(instances) == 0:
            logger.warning("No instance found for component {}.".format(self.name))
        return instances


class Flux(ManagedComponent):
    def __init__(self):
        super().__init__(FLUX)

    def list_instances(self, client, resource_group, service):
        try:
            return self._list_instances(client, resource_group, service)
        except ResourceNotFoundError:
            raise CLIError("'{}' is a subcomponent of Application Configuration Service (ACS) Gen2, "
                           "failed to perform operations when ACS is not enabled.".format(self.name))

    def _list_instances(self, client, resource_group, service):
        acs_arm_resource = client.configuration_services.get(resource_group, service, ACS_DEFAULT_NAME)
        instance_array = acs_arm_resource.properties.instances
        instances = []
        for i in instance_array:
            if i.name.startswith(FLUX_INSTANCE_PREFIX):
                instances.append(ManagedComponentInstance(i.name))
        if len(instances) == 0:
            logger.warning("No instance found for component {}. "
                           "Please double check Application Configuration Service Gen2 is enabled.".format(self.name))
        return instances


class Scg(ManagedComponent):
    def __init__(self):
        super().__init__(SCG)

    def list_instances(self, client, resource_group, service):
        try:
            return self._list_instances(client, resource_group, service)
        except ResourceNotFoundError:
            raise CLIError("'{}' is a subcomponent of Spring Cloud Gateway (SCG), "
                           "failed to perform operations when SCG is not enabled.".format(self.name))

    def _list_instances(self, client, resource_group, service):
        scg_arm_resource = client.gateways.get(resource_group, service, SCG_DEFAULT_NAME)
        instance_array = scg_arm_resource.properties.instances
        instances = []
        for i in instance_array:
            instances.append(ManagedComponentInstance(i.name))
        if len(instances) == 0:
            logger.warning("No instance found for component {}.".format(self.name))
        return instances


class ScgOperator(ManagedComponent):
    def __init__(self):
        super().__init__(SCG_OPERATOR)

    def list_instances(self, client, resource_group, service):
        try:
            return self._list_instances(client, resource_group, service)
        except ResourceNotFoundError:
            raise CLIError("'{}' is a subcomponent of Spring Cloud Gateway (SCG), "
                           "failed to perform operations when SCG is not enabled.".format(self.name))

    def _list_instances(self, client, resource_group, service):
        scg_arm_resource = client.gateways.get(resource_group, service, SCG_DEFAULT_NAME)
        instance_array = scg_arm_resource.properties.operator_properties.instances
        instances = []
        for i in instance_array:
            instances.append(ManagedComponentInstance(i.name))
        if len(instances) == 0:
            logger.warning("No instance found for component {}.".format(self.name))
        return instances


supported_components = [
    Acs(),
    Flux(),
    Scg(),
    ScgOperator(),
]


def get_component(component):
    for c in supported_components:
        if c.match(component):
            return c

    return None
