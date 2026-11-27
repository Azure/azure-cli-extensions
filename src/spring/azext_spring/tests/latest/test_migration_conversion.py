# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from ...migration.converter.app_converter import AppConverter
from ...migration.converter.param_converter import ParamConverter


def _app_export():
    return {
        "resources": [
            {
                "type": "Microsoft.AppPlatform/Spring",
                "name": "spring-example",
                "sku": {"tier": "Standard"},
                "properties": {},
            },
            {
                "type": "Microsoft.AppPlatform/Spring/apps",
                "name": "spring-example/demo-app",
                "properties": {
                    "public": False,
                    "ingressSettings": {"backendProtocol": "Default", "sessionAffinity": "None"},
                },
            },
            {
                "type": "Microsoft.AppPlatform/Spring/apps/deployments",
                "name": "spring-example/demo-app/default",
                "sku": {"tier": "Standard", "capacity": 1},
                "properties": {
                    "active": True,
                    "deploymentSettings": {
                        "resourceRequests": {"cpu": "500m", "memory": "1.0Gi"},
                        "environmentVariables": {"EMPTY": "", "MODE": "normal"},
                    },
                    "source": {
                        "type": "Container",
                        "customContainer": {"server": "example.azurecr.io", "containerImage": "demo:1"},
                    },
                },
            },
        ],
    }


class TestMigrationConversion(unittest.TestCase):
    def test_java_options_and_backslash_stay_literal(self):
        source = _app_export()
        env = source["resources"][2]["properties"]["deploymentSettings"]["environmentVariables"]
        env["JAVA_OPTS"] = "-Dgreeting='hello'"
        env["PATTERN"] = r"\d+"

        output = AppConverter(source).convert()["demo-app_app.bicep"]

        self.assertIn(r"value: '-Dgreeting=\'hello\''", output)
        self.assertIn(r"value: '\\d+'", output)
        self.assertIn("value: ''", output)
        self.assertIn("value: 'normal'", output)

    def test_app_deployment_fields_are_rendered_as_data(self):
        source = _app_export()
        deployment = source["resources"][2]["properties"]
        settings = deployment["deploymentSettings"]
        settings["environmentVariables"] = {
            "GREETING'": "\\${HOME} caf\u00e9\r\n\t",
        }
        container = deployment["source"]["customContainer"]
        container.update({
            "args": ["'hello'", "${HOME}"],
            "command": [r"tools\run"],
        })
        for probe in ("livenessProbe", "readinessProbe", "startupProbe"):
            settings[probe] = {
                "probeAction": {"type": "HTTPGetAction", "scheme": "HTTP", "path": "/health?msg='hello'"},
            }

        output = AppConverter(source).convert()["demo-app_app.bicep"]

        self.assertIn(r"name: 'GREETING\''", output)
        self.assertIn(r"value: '\\\${HOME} caf" + "\u00e9" + r"\r\n\t'", output)
        self.assertIn(r"'\'hello\''", output)
        self.assertIn(r"'\${HOME}'", output)
        self.assertIn(r"'tools\\run'", output)
        self.assertEqual(3, output.count(r"path: '/health?msg=\'hello\''"))

    def test_private_image_values_are_escaped_in_both_files(self):
        source = _app_export()
        container = source["resources"][2]["properties"]["source"]["customContainer"]
        container.update({
            "imageRegistryCredential": {"username": "name'${HOME}"},
            "containerImage": "demo:${TAG}",
        })

        output = AppConverter(source).convert()["demo-app_app.bicep"]
        params = ParamConverter(source).convert()["param.bicepparam"]

        self.assertIn(r"username: 'name\'\${HOME}'", output)
        self.assertIn(r"passwordSecretRef: 'exampleazurecrio-name\'\${HOME}'", output)
        self.assertIn(r"name: 'exampleazurecrio-name\'\${HOME}'", output)
        self.assertIn(r"image: 'example.azurecr.io/demo:\${TAG}'", output)
        self.assertIn("value: containerImagePasswordOf_demo_app", output)
        self.assertIn(r'example.azurecr.io/demo:\${TAG}', params)
