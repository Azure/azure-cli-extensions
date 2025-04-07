# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azext_containerapp._constants import (
    DEV_SERVICE_LIST,
    DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST,
    DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST,
)
from azext_containerapp._dapr_utils import DaprUtils


class DaprUtilsTest(unittest.TestCase):
    def test_supported_dapr_components(self):
        supported_dapr_components = DaprUtils.supported_dapr_components
        self.assertEqual(len(supported_dapr_components), 2)
        self.assertIn("pubsub", supported_dapr_components)
        self.assertIn("state", supported_dapr_components)

        self.assertEqual(
            set(supported_dapr_components["pubsub"]).difference(
                set(DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST)
            ),
            set(),
        )
        self.assertEqual(
            set(supported_dapr_components["state"]).difference(
                set(DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST)
            ),
            set(),
        )

    def test_get_supported_services(self):
        supported_services = DaprUtils._get_supported_services()
        for service, _ in supported_services.items():
            # Should be a supported dev service
            self.assertIn(service, DEV_SERVICE_LIST)
            # Should be either a Dapr supported pubsub or statestore service
            self.assertTrue(
                service in DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST
                or service in DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST
            )

    def test_get_service_name(self):
        testcases = [["foo", "dapr-foo"], ["foo-bar", "dapr-foo-bar"]]
        for testcase in testcases:
            self.assertEqual(DaprUtils._get_service_name(testcase[0]), testcase[1])

    def test_get_dapr_component_name(self):
        testcases = [["state", "statestore"], ["pubsub", "pubsub"], ["foo", "foo"]]
        for testcase in testcases:
            self.assertEqual(
                DaprUtils._get_dapr_component_name(testcase[0]), testcase[1]
            )

    def test_dapr_component_model_from_service(self):
        component_model = DaprUtils._get_dapr_component_model_from_service(
            "state", "redis", "dapr-redis", "redisId"
        )
        self.assertEqual(component_model["properties"]["componentType"], "state.redis")
        self.assertEqual(component_model["properties"]["version"], "v1")
        self.assertEqual(component_model["properties"]["ignoreErrors"], False)
        self.assertEqual(
            component_model["properties"]["serviceComponentBind"]["name"], "dapr-redis"
        )
        self.assertEqual(
            component_model["properties"]["serviceComponentBind"]["serviceId"],
            "redisId",
        )
        self.assertEqual(
            len(component_model["properties"]["serviceComponentBind"]["metadata"]), 1
        )
        self.assertEqual(
            component_model["properties"]["serviceComponentBind"]["metadata"][
                "DCI_SB_CREATED_BY"
            ],
            "azcli_azext_containerapp_daprutils",
        )

        component_model = DaprUtils._get_dapr_component_model_from_service(
            "pubsub",
            "kafka",
            "dapr-kafka",
            "kafkaId",
            "v2",
            True,
            {"foo": "bar", "bar": "baz"},
        )
        self.assertEqual(component_model["properties"]["componentType"], "pubsub.kafka")
        self.assertEqual(component_model["properties"]["version"], "v2")
        self.assertEqual(component_model["properties"]["ignoreErrors"], True)
        self.assertEqual(len(component_model["properties"]["metadata"]), 2)
        self.assertIn(
            {"name": "foo", "value": "bar", "secretRef": None},
            component_model["properties"]["metadata"],
        )
        self.assertIn(
            {"name": "bar", "value": "baz", "secretRef": None},
            component_model["properties"]["metadata"],
        )
        self.assertEqual(
            component_model["properties"]["serviceComponentBind"]["name"], "dapr-kafka"
        )
        self.assertEqual(
            component_model["properties"]["serviceComponentBind"]["serviceId"],
            "kafkaId",
        )

    def test_create_dapr_component_with_service_binding(self):
        testcases = [
            {
                "name": "invalid service binding",
                "component_type": "state",
                "service_type": "foo",
            },
            {
                "name": "invalid component type",
                "component_type": "foo",
                "service_type": "redis",
            },
        ]

        for testcase in testcases:
            try:
                DaprUtils.create_dapr_component_with_service_binding(
                    None,
                    "component_name",
                    testcase["component_type"],
                    testcase["service_type"],
                    "service_name",
                    "service_id",
                    "resource_group",
                    "environment",
                )
                self.fail("Should have raised an exception")
            except Exception as e:
                self.assertEqual(
                    str(e),
                    f"Dapr component type {testcase['component_type']} with service type {testcase['service_type']} is not supported.",
                )