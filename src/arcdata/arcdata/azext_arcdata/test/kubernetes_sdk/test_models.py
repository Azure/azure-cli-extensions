from azext_arcdata.vendored_sdks.kubernetes_sdk.models.custom_resource_update import (
    Policy,
    PolicyValue,
    Update,
)
from azext_arcdata.core.json_serialization import jsonProperty, tags, to_json


class TestUpdateModelDeserialization:
    def test_custom_resource_update_hydration(self):
        update = {
            "desiredVersion": "1.2.3",
        }

        update_resource = Update()
        update_resource._hydrate(update)
        assert update_resource.desiredVersion == "1.2.3"
        # todo: re-enable when policies are implemented.
        # assert update_resource.policies[0].name == "MaintenanceWindow"
        # assert update_resource.policies[0].values[0].name == "start"
