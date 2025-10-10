from azext_arcdata.core.json_serialization import jsonProperty, jsonSerializable, jsonType


class PolicyValue():
    def __init__(self, name: str = None, value: str = None):
        self.name = name
        self.value = value
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value


@jsonSerializable
class Policy():
    """
    Contains information for a single update policy
    """
    def __init__(
        self,
        name: str = None,
        enabled: bool = False,
        values: list = []
    ):
        self.name = name
        self.enabled = enabled
        self.values = values
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @jsonProperty
    @jsonType(PolicyValue, True)
    def values(self) -> list:
        return self._values
    
    @values.setter
    def values(self, value: list):
        self._values = value
    

@jsonSerializable
class Update():
    """
    Contains update information for this resource
    """
    def __init__(
        self,
        desiredVersion: str = None,
        # policies: list = [],      
        # bypassPoliciesVersion: str = None
    ):
        self.desiredVersion = desiredVersion
        # self.policies = policies
        # self.bypassPoliciesVersion = bypassPoliciesVersion

    @jsonProperty
    def desiredVersion(self) -> str:
        return self._desiredVersion

    @desiredVersion.setter
    def desiredVersion(self, value: str):
        self._desiredVersion = value

    # todo: restore for policy implementation
    # @jsonProperty
    # @jsonType(Policy, True)
    # def policies(self):
    #     return self._policies
    
    # @policies.setter
    # def policies(self, value):
    #     self._policies = value

    # @jsonProperty
    # def bypassPoliciesVersion(self):
    #     return self._bypassPoliciesVersion
    
    # @bypassPoliciesVersion.setter
    # def bypassPoliciesVersion(self, value):
    #     self._bypassPoliciesVersion = value
    