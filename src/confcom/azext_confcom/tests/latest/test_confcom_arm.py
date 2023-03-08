# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import pytest
import json
import deepdiff
import docker
from unittest.mock import patch

from azext_confcom.security_policy import (
    OutputType,
    load_policy_from_str,
    load_policy_from_arm_template_str,
)
import azext_confcom.config as config
from azext_confcom.custom import acipolicygen_confcom
from azext_confcom.template_util import case_insensitive_dict_get

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


# @unittest.skip("not in use")
@pytest.mark.run(order=1)
class PolicyGeneratingArm(unittest.TestCase):
    custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [
                        {
                            "name":"PATH",
                            "value":"/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                            "strategy":"string"
                        },
                        {
                            "name":"LANG",
                            "value":"C.UTF-8",
                            "strategy":"string"
                        },
                        {
                            "name":"GPG_KEY",
                            "value":"0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_VERSION",
                            "value":"3.6.14",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_PIP_VERSION",
                            "value":"21.2.4",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_GET_PIP_URL",
                            "value":"https://github.com/pypa/get-pip/raw/c20b0cfd643cd4a19246ccf204e2997af70f6b21/public/get-pip.py",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_GET_PIP_SHA256",
                            "value":"fa6f3fb93cce234cd4e8dd2beb54a51ab9c247653b52855a48dd44e6b21ff28b",
                            "strategy":"string"
                        }
                    ],
                    "command": ["python3"],
                    "workingDir": "",
                    "mounts": [
                        {
                            "mountType": "azureFile",
                            "mountPath": "/aci/logs",
                            "readonly": false
                        },
                         {
                            "mountType": "secret",
                            "mountPath": "/aci/secret",
                            "readonly": true
                        }
                    ]
                }
            ]
        }
        """

    custom_arm_json = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "python:3.6.14-slim-buster"
        },


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"simple-container-group"
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            },
            "defaultValue":"simple-container"
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "command": [
                        "python3"
                    ],
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    },
                     "volumeMounts": [
                                {
                                    "name": "filesharevolume",
                                    "mountPath": "/aci/logs",
                                    "readOnly": false
                                },
                                {
                                    "name": "secretvolume",
                                    "mountPath": "/aci/secret",
                                    "readOnly": true
                                }
                            ]
                    }
                }
                ],
                "volumes": [
                    {
                        "name": "filesharevolume",
                        "azureFile": {
                            "shareName": "shareName1",
                            "storageAccountName": "storage-account-name",
                            "storageAccountKey": "storage-account-key"
                        }
                    },
                    {

                        "name": "secretvolume",
                        "secret": {
                            "mysecret1": "secret1",
                            "mysecret2": "secret2"
                        }
                    }

                ],
                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

        cls.aci_arm_policy = load_policy_from_arm_template_str(cls.custom_arm_json, "")[
            0
        ]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_arm_template_policy(self):
        # deep diff the output policies from the regular policy.json and the ARM template
        normalized_aci_policy = json.loads(
            self.aci_policy.get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        normalized_aci_arm_policy = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, use_json=True
            )
        )

        normalized_aci_policy[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"].pop(config.POLICY_FIELD_CONTAINERS_ID)
        normalized_aci_arm_policy[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"].pop(config.POLICY_FIELD_CONTAINERS_ID)

        self.assertEqual(
            deepdiff.DeepDiff(
                normalized_aci_policy, normalized_aci_arm_policy, ignore_order=True
            ),
            {},
        )

    def test_default_infrastructure_svn(self):
        self.assertEqual(
            config.DEFAULT_REGO_FRAGMENTS[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ],
            self.aci_arm_policy._fragments[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ],
        )


# @unittest.skip("not in use")
@pytest.mark.run(order=2)
class PolicyGeneratingArmIncorrect(unittest.TestCase):
    def test_arm_template_missing_image_name(self):
        custom_arm_json_missing_image_name = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": ""
        },

        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            }
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[variables('image')]",
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

        with self.assertRaises(SystemExit) as exc_info:
            out_policies = load_policy_from_arm_template_str(custom_arm_json_missing_image_name, "")
            for policy in out_policies:
                policy.populate_policy_content_for_all_images()

        self.assertEqual(exc_info.exception.code, 1)

    def test_arm_template_missing_resources(self):
        custom_arm_json_missing_resources = """
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",


            "parameters": {
                "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                }
                },

                "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                }
                },
                "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
                },
                "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
                },
                "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
                },
                "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
                }
            },
            "outputs": {
                "containerIPv4Address": {
                "type": "string",
                "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
                }
            }
        }
    """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_arm_template_str(custom_arm_json_missing_resources, "")
        self.assertEqual(exc_info.exception.code, 1)

    def test_arm_template_missing_aci(self):
        custom_arm_json_missing_aci = """
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",


            "parameters": {
                "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                }
                },

                "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                }
                },
                "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
                },
                "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
                },
                "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
                },
                "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
                }
            },
            "resources": [

            ],
            "outputs": {
                "containerIPv4Address": {
                "type": "string",
                "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
                }
            }
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_arm_template_str(custom_arm_json_missing_aci, "")
        self.assertEqual(exc_info.exception.code, 1)

    def test_arm_template_missing_containers(self):
        custom_arm_json_missing_containers = """
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",


            "parameters": {
                "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                }
                },

                "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                }
                },
                "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
                },
                "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
                },
                "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
                },
                "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
                }
            },
            "resources": [
                {
                "name": "[parameters('containergroupname')]",
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2022-04-01-preview",
                "location": "[parameters('location')]",
                "properties": {
                    "containers": [

                    ],

                    "osType": "Linux",
                    "restartPolicy": "OnFailure",
                    "confidentialComputeProperties": {
                    "IsolationType": "SevSnp"
                    },
                    "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                        "protocol": "Tcp",
                        "port": "[parameters( 'port' )]"
                        }
                    ]
                    }
                }
                }
            ],
            "outputs": {
                "containerIPv4Address": {
                "type": "string",
                "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
                }
            }
        }
        """
        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_arm_template_str(custom_arm_json_missing_containers, "")
        self.assertEqual(exc_info.exception.code, 1)


# @unittest.skip("not in use")
@pytest.mark.run(order=3)
class PolicyGeneratingArmParametersIncorrect(unittest.TestCase):
    def test_arm_template_missing_definition(self):
        custom_arm_json_missing_definition = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            }
             },

            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
        custom_arm_json_missing_definition_parameters = """
        {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "image": {
            "value": "python:3.6.14-slim-buster"
            },
            "containername": {
            "value": "simple-container"
            }
        }
        }"""

        with self.assertRaises(SystemExit) as exc_info:
            load_policy_from_arm_template_str(
                custom_arm_json_missing_definition,
                custom_arm_json_missing_definition_parameters,
            )
        self.assertEqual(exc_info.exception.code, 1)


# @unittest.skip("not in use")
@pytest.mark.run(order=4)
class PolicyGeneratingArmParameters(unittest.TestCase):

    parameter_file = """
        {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "image": {
        "value": "mcr.microsoft.com/azure-functions/python:4-python3.8"
        },
        "containername": {
        "value": "simple-container"
        },
        "containergroupname": {
        "value": "simple-container-group"
        }
    }
    }"""

    def test_arm_template_with_parameter_file(self):
        custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            }
             },
            "image": {
                "type": "string",
                "metadata": {
                    "description": "Name for the image"
                },
                "defaultValue": "mcr.microsoft.com/azure-functions/node:4"
            },

            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "isolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

        output = load_policy_from_arm_template_str(
            custom_arm_json_default_value, self.parameter_file
        )
        output[0].populate_policy_content_for_all_images()
        # use the rego output
        output_json = json.loads(
            output[0].get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )
        # see if we have environment variables specific to the python image in the parameter file
        python_flag = False
        for rules in output_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]:
            if "PYTHON" in rules[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE]:
                python_flag = True
        self.assertTrue(python_flag)


# @unittest.skip("not in use")
@pytest.mark.run(order=5)
class PolicyGeneratingArmParameters2(unittest.TestCase):

    parameter_file = """
        {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "image": {
        "value": "mcr.microsoft.com/azure-functions/python:4-python3.8"
        },
        "containername": {
        "value": "simple-container"
        },
        "containergroupname": {
        "value": "simple-container-group"
        }
    }
    }"""

    def test_arm_template_with_parameter_file_injected_env_vars(self):
        custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }
            },
            "image": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"mcr.microsoft.com/azure-functions/node:4"
            },
             "imagebase": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"mcr.microsoft.com"
            },
             "imagespecific": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"/azure-functions/node:4"
            },
            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            }
             },
            "testvalue": {
                "type": "string",
                "metadata": {
                    "description": "value to see if concat function doesn't break inside template"
                },
                "defaultValue": "[concat(parameters('imagebase'), parameters('imagespecific'))]"
            },

            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

        # this test adds in a parameter that uses the concat function to make sure it doesn't break with partially parsing the template's json file

        output = load_policy_from_arm_template_str(
            custom_arm_json_default_value, self.parameter_file
        )
        output[0].populate_policy_content_for_all_images()
        output_json = json.loads(
            output[0].get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        # see if we have environment variables specific to the python image in the parameter file
        python_flag = False
        for _, value in output_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ].items():
            if "PYTHON" in value[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE]:
                python_flag = True
        self.assertTrue(python_flag)


# @unittest.skip("not in use")
@pytest.mark.run(order=6)
class PolicyGeneratingArmContainerConfig(unittest.TestCase):

    parameter_file = """
        {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "image": {
        "value": "mcr.microsoft.com/azure-functions/python:4-python3.8"
        },
        "containername": {
        "value": "simple-container"
        },
        "containergroupname": {
        "value": "simple-container-group"
        }
    }
    }"""

    def test_arm_template_with_parameter_file_arm_config(self):
        custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }
            },
            "image": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"mcr.microsoft.com/azure-functions/node:4"
            },
             "imagebase": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"mcr.microsoft.com"
            },
             "imagespecific": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"/azure-functions/node:4"
            },
            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            }
             },
            "testvalue": {
                "type": "string",
                "metadata": {
                    "description": "value to see if concat function doesn't break inside template"
                },
                "defaultValue": "[concat(parameters('imagebase'), parameters('imagespecific'))]"
            },

            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "environmentVariables": [
                        {
                        "name": "PORT",
                        "value": "80"
                        }
                    ],

                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "command": [
                        "/bin/bash",
                        "-c",
                        "while sleep 5; do cat /mnt/input/access.log; done"
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

        # this test adds in a parameter that uses the concat function to make sure it doesn't break with partially parsing the template's json file

        output = load_policy_from_arm_template_str(
            custom_arm_json_default_value, self.parameter_file
        )
        output[0].populate_policy_content_for_all_images()
        # see if we have environment variables that are in the template
        output_json = json.loads(
            output[0].get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        for _, value in output_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ].items():
            if case_insensitive_dict_get(
                value, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
            ).startswith("PORT"):
                self.assertTrue(
                    case_insensitive_dict_get(
                        value, config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
                    ).endswith("80")
                )

        # check for custom startup command
        expected = [
            "/bin/bash",
            "-c",
            "while sleep 5; do cat /mnt/input/access.log; done",
        ]
        for _, value in output_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"][config.POLICY_FIELD_CONTAINERS_ELEMENTS_COMMANDS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ].items():
            self.assertTrue(value in expected)


# @unittest.skip("not in use")
@pytest.mark.run(order=7)
class PolicyGeneratingArmParametersCleanRoom(unittest.TestCase):

    parameter_file = """
        {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "image": {
        "value": "fakerepo.microsoft.com/azure-functions:fake-tag"
        }
    }
    }"""

    def test_arm_template_with_parameter_file_clean_room(self):
        custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"simple-container-group"
            },
            "image": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"mcr.microsoft.com/azure-functions/node:4"
            },
            "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
            },

            "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
            },
            "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
            },
            "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
            },
            "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "environmentVariables": [
                        {
                        "name": "PORT",
                        "value": "80"
                        }
                    ],

                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "command": [
                        "/bin/bash",
                        "-c",
                        "while sleep 5; do cat /mnt/input/access.log; done"
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
        client = docker.from_env()
        original_image = "mcr.microsoft.com/azure-functions/node:4"
        try:
            client.images.remove(original_image)
        except:
            # do nothing
            pass
        regular_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )
        regular_image[0].populate_policy_content_for_all_images()
        # create and tag same image to the new name to see if docker will error out that the image is not in a remote repo
        new_repo = "fakerepo.microsoft.com"
        new_image_name = "azure-functions"
        new_tag = "fake-tag"

        image = client.images.get(original_image)
        try:
            client.images.remove(new_repo + "/" + new_image_name + ":" + new_tag)
        except:
            # do nothing
            pass
        image.tag(new_repo + "/" + new_image_name, tag=new_tag)

        client.close()

        clean_room = load_policy_from_arm_template_str(
            custom_arm_json_default_value, self.parameter_file
        )
        clean_room[0].populate_policy_content_for_all_images()

        regular_image_json = json.loads(
            regular_image[0].get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        clean_room_json = json.loads(
            clean_room[0].get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        regular_image_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["0"].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertEqual(
            deepdiff.DeepDiff(regular_image_json, clean_room_json, ignore_order=True),
            {},
        )


# @unittest.skip("not in use")
@pytest.mark.run(order=8)
class PolicyDiff(unittest.TestCase):
    custom_json = """
      {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "variables": {
        "container1name": "aci-test",
        "container1image": "rust:1.52.1"
    },
    "resources": [
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "name": "secret-volume-demo",
            "location": "[resourceGroup().location]",
            "properties": {
                "confidentialComputeProperties": {
                    "isolationType": "SevSnp",
                    "ccePolicy": "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3N2biA6PSAiMC4xMC4wIgpmcmFtZXdvcmtfc3ZuIDo9ICIwLjEuMCIKCmZyYWdtZW50cyA6PSBbCiAgewogICAgImZlZWQiOiAibWNyLm1pY3Jvc29mdC5jb20vYWNpL2FjaS1jYy1pbmZyYS1mcmFnbWVudCIsCiAgICAiaW5jbHVkZXMiOiBbCiAgICAgICJjb250YWluZXJzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjEuMC4wIgogIH0KXQoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbImJhc2giXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vY3VzdG9taXplZC9wYXRoL3ZhbHVlIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlRFU1RfUkVHRVhQX0VOVj10ZXN0X3JlZ2V4cF9lbnYiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUlVTVFVQX0hPTUU9L3Vzci9sb2NhbC9ydXN0dXAiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiQ0FSR09fSE9NRT0vdXNyL2xvY2FsL2NhcmdvIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlJVU1RfVkVSU0lPTj0xLjUyLjEiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiIoKD9pKUZBQlJJQylfLis9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSE9TVE5BTUU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiVChFKT9NUD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJGYWJyaWNQYWNrYWdlRmlsZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSG9zdGVkU2VydmljZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfQVBJX1ZFUlNJT049LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfSEVBREVSPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX1NFUlZFUl9USFVNQlBSSU5UPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6ImF6dXJlY29udGFpbmVyaW5zdGFuY2VfcmVzdGFydGVkX2J5PS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJpZCI6InJ1c3Q6MS41Mi4xIiwibGF5ZXJzIjpbImZlODRjOWQ1YmZkZGQwN2EyNjI0ZDAwMzMzY2YxM2MxYTljOTQxZjNhMjYxZjEzZWFkNDRmYzZhOTNiYzBlN2EiLCI0ZGVkYWU0Mjg0N2M3MDRkYTg5MWEyOGMyNWQzMjIwMWExYWU0NDBiY2UyYWVjY2NmYThlNmYwM2I5N2E2YTZjIiwiNDFkNjRjZGViMzQ3YmYyMzZiNGMxM2I3NDAzYjYzM2ZmMTFmMWNmOTRkYmM3Y2Y4ODFhNDRkNmRhODhjNTE1NiIsImViMzY5MjFlMWY4MmFmNDZkZmUyNDhlZjhmMWIzYWZiNmE1MjMwYTY0MTgxZDk2MGQxMDIzN2EwOGNkNzNjNzkiLCJlNzY5ZDc0ODdjYzMxNGQzZWU3NDhhNDQ0MDgwNTMxN2MxOTI2MmM3YWNkMmZkYmRiMGQ0N2QyZTQ2MTNhMTVjIiwiMWI4MGYxMjBkYmQ4OGU0MzU1ZDYyNDFiNTE5YzNlMjUyOTAyMTVjNDY5NTE2YjQ5ZGVjZTljZjA3MTc1YTc2NiJdLCJtb3VudHMiOlt7ImRlc3RpbmF0aW9uIjoiL21vdW50L2F6dXJlZmlsZSIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvYXp1cmVGaWxlVm9sdW1lLy4rIiwidHlwZSI6ImJpbmQifSx7ImRlc3RpbmF0aW9uIjoiL2V0Yy9yZXNvbHYuY29uZiIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvcmVzb2x2Y29uZi8uKyIsInR5cGUiOiJiaW5kIn1dLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn0seyJhbGxvd19lbGV2YXRlZCI6ZmFsc2UsImFsbG93X3N0ZGlvX2FjY2VzcyI6dHJ1ZSwiY29tbWFuZCI6WyIvcGF1c2UiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vdXNyL2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4iLCJyZXF1aXJlZCI6dHJ1ZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJsYXllcnMiOlsiMTZiNTE0MDU3YTA2YWQ2NjVmOTJjMDI4NjNhY2EwNzRmZDU5NzZjNzU1ZDI2YmZmMTYzNjUyOTkxNjllODQxNSJdLCJtb3VudHMiOltdLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn1dCgphbGxvd19wcm9wZXJ0aWVzX2FjY2VzcyA6PSBmYWxzZQphbGxvd19kdW1wX3N0YWNrcyA6PSBmYWxzZQphbGxvd19ydW50aW1lX2xvZ2dpbmcgOj0gZmFsc2UKYWxsb3dfZW52aXJvbm1lbnRfdmFyaWFibGVfZHJvcHBpbmcgOj0gdHJ1ZQphbGxvd191bmVuY3J5cHRlZF9zY3JhdGNoIDo9IGZhbHNlCgoKCm1vdW50X2RldmljZSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9kZXZpY2UKdW5tb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9kZXZpY2UKbW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9vdmVybGF5CnVubW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay51bm1vdW50X292ZXJsYXkKY3JlYXRlX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5jcmVhdGVfY29udGFpbmVyCmV4ZWNfaW5fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfaW5fY29udGFpbmVyCmV4ZWNfZXh0ZXJuYWwgOj0gZGF0YS5mcmFtZXdvcmsuZXhlY19leHRlcm5hbApzaHV0ZG93bl9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuc2h1dGRvd25fY29udGFpbmVyCnNpZ25hbF9jb250YWluZXJfcHJvY2VzcyA6PSBkYXRhLmZyYW1ld29yay5zaWduYWxfY29udGFpbmVyX3Byb2Nlc3MKcGxhbjlfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfbW91bnQKcGxhbjlfdW5tb3VudCA6PSBkYXRhLmZyYW1ld29yay5wbGFuOV91bm1vdW50CmdldF9wcm9wZXJ0aWVzIDo9IGRhdGEuZnJhbWV3b3JrLmdldF9wcm9wZXJ0aWVzCmR1bXBfc3RhY2tzIDo9IGRhdGEuZnJhbWV3b3JrLmR1bXBfc3RhY2tzCnJ1bnRpbWVfbG9nZ2luZyA6PSBkYXRhLmZyYW1ld29yay5ydW50aW1lX2xvZ2dpbmcKbG9hZF9mcmFnbWVudCA6PSBkYXRhLmZyYW1ld29yay5sb2FkX2ZyYWdtZW50CnNjcmF0Y2hfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF9tb3VudApzY3JhdGNoX3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF91bm1vdW50CgpyZWFzb24gOj0geyJlcnJvcnMiOiBkYXRhLmZyYW1ld29yay5lcnJvcnN9"
                },
                "containers": [
                    {
                        "name": "[variables('container1name')]",
                        "properties": {
                            "image": "[variables('container1image')]",
                            "resources": {
                                "requests": {
                                    "cpu": 1,
                                    "memoryInGb": 1.5
                                }
                            },
                            "ports": [
                                {
                                    "port": 80
                                }
                            ],
                            "volumeMounts": [
                                {
                                    "name": "azurefile",
                                    "mountPath": "/mount/azurefile"
                                }
                            ],
                            "environmentVariables": [
                                {
                                    "name": "PATH",
                                    "value": "/customized/path/value"
                                },
                                {
                                    "name": "TEST_REGEXP_ENV",
                                    "value": "test_regexp_env"
                                }
                            ]
                        }
                    }
                ],
                "osType": "Linux",
                "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                            "protocol": "tcp",
                            "port": "80"
                        }
                    ]
                },
                "volumes": [
                    {
                        "name": "azurefile",
                        "azureFile": {
                            "key1": "key-1",
                            "key2": "key-2"
                        }
                    }
                ]
            }
        }
    ]
}
    """

    custom_json2 = """
      {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "variables": {
        "container1name": "aci-test",
        "container1image": "rust:1.52.1"
    },
    "resources": [
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "name": "secret-volume-demo",
            "location": "[resourceGroup().location]",
            "properties": {
                "confidentialComputeProperties": {
                    "isolationType": "SevSnp",
                    "ccePolicy": "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3N2biA6PSAiMC4xMC4wIgpmcmFtZXdvcmtfc3ZuIDo9ICIwLjEuMCIKCmZyYWdtZW50cyA6PSBbCiAgewogICAgImZlZWQiOiAibWNyLm1pY3Jvc29mdC5jb20vYWNpL2FjaS1jYy1pbmZyYS1mcmFnbWVudCIsCiAgICAiaW5jbHVkZXMiOiBbCiAgICAgICJjb250YWluZXJzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjEuMC4wIgogIH0KXQoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbImJhc2giXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vY3VzdG9taXplZC9wYXRoL3ZhbHVlIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlRFU1RfUkVHRVhQX0VOVj10ZXN0X3JlZ2V4cF9lbnYiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUlVTVFVQX0hPTUU9L3Vzci9sb2NhbC9ydXN0dXAiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiQ0FSR09fSE9NRT0vdXNyL2xvY2FsL2NhcmdvIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlJVU1RfVkVSU0lPTj0xLjUyLjEiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiIoKD9pKUZBQlJJQylfLis9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSE9TVE5BTUU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiVChFKT9NUD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJGYWJyaWNQYWNrYWdlRmlsZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSG9zdGVkU2VydmljZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfQVBJX1ZFUlNJT049LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfSEVBREVSPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX1NFUlZFUl9USFVNQlBSSU5UPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6ImF6dXJlY29udGFpbmVyaW5zdGFuY2VfcmVzdGFydGVkX2J5PS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJpZCI6InJ1c3Q6MS41Mi4xIiwibGF5ZXJzIjpbImZlODRjOWQ1YmZkZGQwN2EyNjI0ZDAwMzMzY2YxM2MxYTljOTQxZjNhMjYxZjEzZWFkNDRmYzZhOTNiYzBlN2EiLCI0ZGVkYWU0Mjg0N2M3MDRkYTg5MWEyOGMyNWQzMjIwMWExYWU0NDBiY2UyYWVjY2NmYThlNmYwM2I5N2E2YTZjIiwiNDFkNjRjZGViMzQ3YmYyMzZiNGMxM2I3NDAzYjYzM2ZmMTFmMWNmOTRkYmM3Y2Y4ODFhNDRkNmRhODhjNTE1NiIsImViMzY5MjFlMWY4MmFmNDZkZmUyNDhlZjhmMWIzYWZiNmE1MjMwYTY0MTgxZDk2MGQxMDIzN2EwOGNkNzNjNzkiLCJlNzY5ZDc0ODdjYzMxNGQzZWU3NDhhNDQ0MDgwNTMxN2MxOTI2MmM3YWNkMmZkYmRiMGQ0N2QyZTQ2MTNhMTVjIiwiMWI4MGYxMjBkYmQ4OGU0MzU1ZDYyNDFiNTE5YzNlMjUyOTAyMTVjNDY5NTE2YjQ5ZGVjZTljZjA3MTc1YTc2NiJdLCJtb3VudHMiOlt7ImRlc3RpbmF0aW9uIjoiL21vdW50L2F6dXJlZmlsZSIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvYXp1cmVGaWxlVm9sdW1lLy4rIiwidHlwZSI6ImJpbmQifSx7ImRlc3RpbmF0aW9uIjoiL2V0Yy9yZXNvbHYuY29uZiIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvcmVzb2x2Y29uZi8uKyIsInR5cGUiOiJiaW5kIn1dLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn0seyJhbGxvd19lbGV2YXRlZCI6ZmFsc2UsImFsbG93X3N0ZGlvX2FjY2VzcyI6dHJ1ZSwiY29tbWFuZCI6WyIvcGF1c2UiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vdXNyL2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4iLCJyZXF1aXJlZCI6dHJ1ZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJsYXllcnMiOlsiMTZiNTE0MDU3YTA2YWQ2NjVmOTJjMDI4NjNhY2EwNzRmZDU5NzZjNzU1ZDI2YmZmMTYzNjUyOTkxNjllODQxNSJdLCJtb3VudHMiOltdLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn1dCgphbGxvd19wcm9wZXJ0aWVzX2FjY2VzcyA6PSBmYWxzZQphbGxvd19kdW1wX3N0YWNrcyA6PSBmYWxzZQphbGxvd19ydW50aW1lX2xvZ2dpbmcgOj0gZmFsc2UKYWxsb3dfZW52aXJvbm1lbnRfdmFyaWFibGVfZHJvcHBpbmcgOj0gdHJ1ZQphbGxvd191bmVuY3J5cHRlZF9zY3JhdGNoIDo9IGZhbHNlCgoKCm1vdW50X2RldmljZSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9kZXZpY2UKdW5tb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9kZXZpY2UKbW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9vdmVybGF5CnVubW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay51bm1vdW50X292ZXJsYXkKY3JlYXRlX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5jcmVhdGVfY29udGFpbmVyCmV4ZWNfaW5fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfaW5fY29udGFpbmVyCmV4ZWNfZXh0ZXJuYWwgOj0gZGF0YS5mcmFtZXdvcmsuZXhlY19leHRlcm5hbApzaHV0ZG93bl9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuc2h1dGRvd25fY29udGFpbmVyCnNpZ25hbF9jb250YWluZXJfcHJvY2VzcyA6PSBkYXRhLmZyYW1ld29yay5zaWduYWxfY29udGFpbmVyX3Byb2Nlc3MKcGxhbjlfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfbW91bnQKcGxhbjlfdW5tb3VudCA6PSBkYXRhLmZyYW1ld29yay5wbGFuOV91bm1vdW50CmdldF9wcm9wZXJ0aWVzIDo9IGRhdGEuZnJhbWV3b3JrLmdldF9wcm9wZXJ0aWVzCmR1bXBfc3RhY2tzIDo9IGRhdGEuZnJhbWV3b3JrLmR1bXBfc3RhY2tzCnJ1bnRpbWVfbG9nZ2luZyA6PSBkYXRhLmZyYW1ld29yay5ydW50aW1lX2xvZ2dpbmcKbG9hZF9mcmFnbWVudCA6PSBkYXRhLmZyYW1ld29yay5sb2FkX2ZyYWdtZW50CnNjcmF0Y2hfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF9tb3VudApzY3JhdGNoX3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF91bm1vdW50CgpyZWFzb24gOj0geyJlcnJvcnMiOiBkYXRhLmZyYW1ld29yay5lcnJvcnN9"
                },
                "containers": [
                    {
                        "name": "[variables('container1name')]",
                        "properties": {
                            "image": "[variables('container1image')]",
                            "resources": {
                                "requests": {
                                    "cpu": 1,
                                    "memoryInGb": 1.5
                                }
                            },
                            "ports": [
                                {
                                    "port": 80
                                }
                            ],
                            "volumeMounts": [
                                {
                                    "name": "azurefile",
                                    "mountPath": "/mount/azure"
                                }
                            ],
                            "environmentVariables": [
                                {
                                    "name": "PATH",
                                    "value": "/customized/path/value"
                                },
                                {
                                    "name": "TEST_REGEXP_ENV",
                                    "value": "test_regexp_en"
                                },
                                {
                                    "name": "ENV_VALUE",
                                    "value": "input_value"
                                }
                            ]
                        }
                    }
                ],
                "osType": "Linux",
                "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                            "protocol": "tcp",
                            "port": "80"
                        }
                    ]
                },
                "volumes": [
                    {
                        "name": "azurefile",
                        "azureFile": {
                            "key1": "key-1",
                            "key2": "key-2"
                        }
                    }
                ]
            }
        }
    ]
}
    """

    aci_policy = None
    existing_policy = None
    aci_policy2 = None
    existing_policy2 = None

    @classmethod
    def setUpClass(cls):
        cls.aci_policy = load_policy_from_arm_template_str(cls.custom_json, "")[0]
        cls.aci_policy.populate_policy_content_for_all_images()
        cls.aci_policy2 = load_policy_from_arm_template_str(cls.custom_json2, "")[0]
        cls.aci_policy2.populate_policy_content_for_all_images()

    def test_policy_diff(self):

        is_valid, diff = self.aci_policy.validate_cce_policy()
        self.assertTrue(is_valid)
        self.assertTrue(not diff)

    def test_incorrect_policy_diff(self):

        is_valid, diff = self.aci_policy2.validate_cce_policy()
        self.assertFalse(is_valid)
        expected_diff = {
            "rust:1.52.1": {
                "values_changed": {
                    "mounts": [
                        {
                            "tested_value": "/mount/azure",
                            "policy_value": "/mount/azurefile",
                        }
                    ]
                },
                "env_rules": [
                    "environment variable with rule 'TEST_REGEXP_ENV=test_regexp_en' does not match strings or regex in policy rules",
                    "environment variable with rule 'ENV_VALUE=input_value' does not match strings or regex in policy rules",
                ],
            }
        }

        self.assertEqual(diff, expected_diff)


# @unittest.skip("not in use")
@pytest.mark.run(order=9)
class PolicyGeneratingArmInfrastructureSvn(unittest.TestCase):
    custom_arm_json = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "python:3.6.14-slim-buster"
        },


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"simple-container-group"
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            },
            "defaultValue":"simple-container"
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "command": [
                        "python3"
                    ],
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    },
                     "volumeMounts": [
                                {
                                    "name": "filesharevolume",
                                    "mountPath": "/aci/logs",
                                    "readOnly": false
                                },
                                {
                                    "name": "secretvolume",
                                    "mountPath": "/aci/secret",
                                    "readOnly": true
                                }
                            ]
                    }
                }
                ],
                "volumes": [
                    {
                        "name": "filesharevolume",
                        "azureFile": {
                            "shareName": "shareName1",
                            "storageAccountName": "storage-account-name",
                            "storageAccountKey": "storage-account-key"
                        }
                    },
                    {

                        "name": "secretvolume",
                        "secret": {
                            "mysecret1": "secret1",
                            "mysecret2": "secret2"
                        }
                    }

                ],
                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
    aci_policy = None

    @classmethod
    def setUpClass(cls):
        cls.aci_arm_policy = load_policy_from_arm_template_str(
            cls.custom_arm_json, "", infrastructure_svn="2.0.0"
        )[0]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_update_infrastructure_svn(self):
        expected_policy = "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3N2biA6PSAiMC4xMC4wIgpmcmFtZXdvcmtfc3ZuIDo9ICIwLjEuMCIKCmZyYWdtZW50cyA6PSBbCiAgewogICAgImZlZWQiOiAibWNyLm1pY3Jvc29mdC5jb20vYWNpL2FjaS1jYy1pbmZyYS1mcmFnbWVudCIsCiAgICAiaW5jbHVkZXMiOiBbCiAgICAgICJjb250YWluZXJzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjIuMC4wIgogIH0KXQoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbInB5dGhvbjMiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vdXNyL2xvY2FsL2JpbjovdXNyL2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4iLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiTEFORz1DLlVURi04IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IkdQR19LRVk9MEQ5NkRGNEQ0MTEwRTVDNDNGQkZCMTdGMkQzNDdFQTZBQTY1NDIxRCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fVkVSU0lPTj0zLjYuMTQiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUFlUSE9OX1BJUF9WRVJTSU9OPTIxLjIuNCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fR0VUX1BJUF9VUkw9aHR0cHM6Ly9naXRodWIuY29tL3B5cGEvZ2V0LXBpcC9yYXcvYzIwYjBjZmQ2NDNjZDRhMTkyNDZjY2YyMDRlMjk5N2FmNzBmNmIyMS9wdWJsaWMvZ2V0LXBpcC5weSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fR0VUX1BJUF9TSEEyNTY9ZmE2ZjNmYjkzY2NlMjM0Y2Q0ZThkZDJiZWI1NGE1MWFiOWMyNDc2NTNiNTI4NTVhNDhkZDQ0ZTZiMjFmZjI4YiIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IigoP2kpRkFCUklDKV8uKz0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJIT1NUTkFNRT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJUKEUpP01QPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IkZhYnJpY1BhY2thZ2VGaWxlTmFtZT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJIb3N0ZWRTZXJ2aWNlTmFtZT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJJREVOVElUWV9BUElfVkVSU0lPTj0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJJREVOVElUWV9IRUFERVI9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfU0VSVkVSX1RIVU1CUFJJTlQ9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiYXp1cmVjb250YWluZXJpbnN0YW5jZV9yZXN0YXJ0ZWRfYnk9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn1dLCJleGVjX3Byb2Nlc3NlcyI6W10sImlkIjoicHl0aG9uOjMuNi4xNC1zbGltLWJ1c3RlciIsImxheWVycyI6WyIyNTRjYzg1M2RhNjA4MTkwNWM5MTA5YzhiOWQ5OWM5ZmIwOTg3YmExZDg4ZjcyOTA4ODkwM2NmZmI4MGY1NWYxIiwiYTU2OGYxOTAwYmVkNjBhMDY0MWI3NmI5OTFhZDQzMTQ0NmQ5YzNhMzQ0ZDdiMjYxZjEwZGU4ZDhlNzM3NjNhYyIsImM3MGM1MzBlODQyZjY2MjE1YjBiZDk1NTg3NzE1N2JhMjRjMzc5OTMwMzU2N2MzZjU2NzNjNDU2NjNlYTRkMTUiLCIzZTg2YzNjY2YxNjQyYmY1ODRkZTMzYjQ5YzcyNDhmODdlZWNkMGY2ZDhjMDgzNTNkYWEzNmNjN2FkMGE3YjZhIiwiMWU0Njg0ZDhjN2NhYTc0YzY1MjQxNzJiNGQ1YTE1OWExMDg4NzYxM2VkNzBmMThkMGE1NWQwNWIyYWY2MWFjZCJdLCJtb3VudHMiOlt7ImRlc3RpbmF0aW9uIjoiL2FjaS9sb2dzIiwib3B0aW9ucyI6WyJyYmluZCIsInJzaGFyZWQiLCJydyJdLCJzb3VyY2UiOiJzYW5kYm94Oi8vL3RtcC9hdGxhcy9henVyZUZpbGVWb2x1bWUvLisiLCJ0eXBlIjoiYmluZCJ9LHsiZGVzdGluYXRpb24iOiIvYWNpL3NlY3JldCIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicm8iXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvc2VjcmV0c1ZvbHVtZS8uKyIsInR5cGUiOiJiaW5kIn0seyJkZXN0aW5hdGlvbiI6Ii9ldGMvcmVzb2x2LmNvbmYiLCJvcHRpb25zIjpbInJiaW5kIiwicnNoYXJlZCIsInJ3Il0sInNvdXJjZSI6InNhbmRib3g6Ly8vdG1wL2F0bGFzL3Jlc29sdmNvbmYvLisiLCJ0eXBlIjoiYmluZCJ9XSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9LHsiYWxsb3dfZWxldmF0ZWQiOmZhbHNlLCJhbGxvd19zdGRpb19hY2Nlc3MiOnRydWUsImNvbW1hbmQiOlsiL3BhdXNlIl0sImVudl9ydWxlcyI6W3sicGF0dGVybiI6IlBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluIiwicmVxdWlyZWQiOnRydWUsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifV0sImV4ZWNfcHJvY2Vzc2VzIjpbXSwibGF5ZXJzIjpbIjE2YjUxNDA1N2EwNmFkNjY1ZjkyYzAyODYzYWNhMDc0ZmQ1OTc2Yzc1NWQyNmJmZjE2MzY1Mjk5MTY5ZTg0MTUiXSwibW91bnRzIjpbXSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9XQoKYWxsb3dfcHJvcGVydGllc19hY2Nlc3MgOj0gZmFsc2UKYWxsb3dfZHVtcF9zdGFja3MgOj0gZmFsc2UKYWxsb3dfcnVudGltZV9sb2dnaW5nIDo9IGZhbHNlCmFsbG93X2Vudmlyb25tZW50X3ZhcmlhYmxlX2Ryb3BwaW5nIDo9IHRydWUKYWxsb3dfdW5lbmNyeXB0ZWRfc2NyYXRjaCA6PSBmYWxzZQoKCgptb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfZGV2aWNlCnVubW91bnRfZGV2aWNlIDo9IGRhdGEuZnJhbWV3b3JrLnVubW91bnRfZGV2aWNlCm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfb3ZlcmxheQp1bm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9vdmVybGF5CmNyZWF0ZV9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuY3JlYXRlX2NvbnRhaW5lcgpleGVjX2luX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5leGVjX2luX2NvbnRhaW5lcgpleGVjX2V4dGVybmFsIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfZXh0ZXJuYWwKc2h1dGRvd25fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLnNodXRkb3duX2NvbnRhaW5lcgpzaWduYWxfY29udGFpbmVyX3Byb2Nlc3MgOj0gZGF0YS5mcmFtZXdvcmsuc2lnbmFsX2NvbnRhaW5lcl9wcm9jZXNzCnBsYW45X21vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnBsYW45X21vdW50CnBsYW45X3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfdW5tb3VudApnZXRfcHJvcGVydGllcyA6PSBkYXRhLmZyYW1ld29yay5nZXRfcHJvcGVydGllcwpkdW1wX3N0YWNrcyA6PSBkYXRhLmZyYW1ld29yay5kdW1wX3N0YWNrcwpydW50aW1lX2xvZ2dpbmcgOj0gZGF0YS5mcmFtZXdvcmsucnVudGltZV9sb2dnaW5nCmxvYWRfZnJhZ21lbnQgOj0gZGF0YS5mcmFtZXdvcmsubG9hZF9mcmFnbWVudApzY3JhdGNoX21vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnNjcmF0Y2hfbW91bnQKc2NyYXRjaF91bm1vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnNjcmF0Y2hfdW5tb3VudAoKcmVhc29uIDo9IHsiZXJyb3JzIjogZGF0YS5mcmFtZXdvcmsuZXJyb3JzfQ=="

        self.assertEqual(expected_policy, self.aci_arm_policy.get_serialized_output())

        self.assertEqual(
            "2.0.0",
            self.aci_arm_policy._fragments[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ],
        )


# @unittest.skip("not in use")
@pytest.mark.run(order=10)
class MultiplePolicyTemplate(unittest.TestCase):
    custom_json = """
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "variables": {
        "container1name": "aci-test",
        "container1image": "rust:1.52.1",
        "container2name": "aci-test2",
        "container2image": "python:3.6.14-slim-buster"
    },
    "resources": [
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "name": "secret-volume-demo",
            "location": "[resourceGroup().location]",
            "properties": {
                "confidentialComputeProperties": {
                    "isolationType": "SevSnp",
                    "ccePolicy": ""
                },
                "containers": [
                    {
                        "name": "[variables('container1name')]",
                        "properties": {
                            "image": "[variables('container1image')]",
                            "resources": {
                                "requests": {
                                    "cpu": 1,
                                    "memoryInGb": 1.5
                                }
                            },
                            "ports": [
                                {
                                    "port": 80
                                }
                            ],
                            "volumeMounts": [
                                {
                                    "name": "azurefile",
                                    "mountPath": "/mount/azurefile"
                                }
                            ],
                            "environmentVariables": [
                                {
                                    "name": "PATH",
                                    "value": "/customized/path/value"
                                },
                                {
                                    "name": "TEST_REGEXP_ENV",
                                    "secureValue": "test_regexp_env"
                                }
                            ]
                        }
                    }
                ],
                "osType": "Linux",
                "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                            "protocol": "tcp",
                            "port": "80"
                        }
                    ]
                },
                "volumes": [
                    {
                        "name": "azurefile",
                        "azureFile": {
                            "key1": "key-1",
                            "key2": "key-2"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "name": "secret-volume-demo",
            "location": "[resourceGroup().location]",
            "properties": {
                "confidentialComputeProperties": {
                    "isolationType": "SevSnp",
                    "ccePolicy": ""
                },
                "containers": [
                    {
                        "name": "[variables('container2name')]",
                        "properties": {
                            "image": "[variables('container2image')]",
                            "resources": {
                                "requests": {
                                    "cpu": 1,
                                    "memoryInGb": 1.5
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "azurefile",
                                    "mountPath": "/mount/file"
                                }
                            ],
                            "environmentVariables": [
                                {
                                    "name": "PATH",
                                    "secureValue": "/customized/different/path/value"
                                }
                            ]
                        }
                    }
                ],
                "osType": "Linux",
                "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                            "protocol": "tcp",
                            "port": "80"
                        }
                    ]
                },
                "volumes": [
                    {
                        "name": "azurefile",
                        "azureFile": {
                            "key1": "key-3",
                            "key2": "key-4"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Compute/disks",
            "apiVersion": "2018-06-01",
            "name": "my-vm-datadisk1",
            "location": "[resourceGroup().location]",
            "sku": {
                "name": "Standard_LRS"
            },
            "properties": {
                "creationData": {
                    "createOption": "Empty"
                },
                "diskSizeGB": 1023
            }
        }

    ]
}
    """

    aci_policy = None
    aci_policy2 = None

    @classmethod
    def setUpClass(cls):
        temp_policies = load_policy_from_arm_template_str(cls.custom_json, "")
        cls.aci_policy = temp_policies[0]
        cls.aci_policy2 = temp_policies[1]
        cls.aci_policy.populate_policy_content_for_all_images()
        cls.aci_policy2.populate_policy_content_for_all_images()

    def test_multiple_policies(self):
        output1 = self.aci_policy.get_serialized_output()
        output2 = self.aci_policy2.get_serialized_output()
        self.assertTrue(output1 != output2)

        expected_output1 = "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3N2biA6PSAiMC4xMC4wIgpmcmFtZXdvcmtfc3ZuIDo9ICIwLjEuMCIKCmZyYWdtZW50cyA6PSBbCiAgewogICAgImZlZWQiOiAibWNyLm1pY3Jvc29mdC5jb20vYWNpL2FjaS1jYy1pbmZyYS1mcmFnbWVudCIsCiAgICAiaW5jbHVkZXMiOiBbCiAgICAgICJjb250YWluZXJzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjEuMC4wIgogIH0KXQoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbImJhc2giXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vY3VzdG9taXplZC9wYXRoL3ZhbHVlIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlRFU1RfUkVHRVhQX0VOVj10ZXN0X3JlZ2V4cF9lbnYiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUlVTVFVQX0hPTUU9L3Vzci9sb2NhbC9ydXN0dXAiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiQ0FSR09fSE9NRT0vdXNyL2xvY2FsL2NhcmdvIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlJVU1RfVkVSU0lPTj0xLjUyLjEiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiIoKD9pKUZBQlJJQylfLis9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSE9TVE5BTUU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiVChFKT9NUD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJGYWJyaWNQYWNrYWdlRmlsZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSG9zdGVkU2VydmljZU5hbWU9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfQVBJX1ZFUlNJT049LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfSEVBREVSPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX1NFUlZFUl9USFVNQlBSSU5UPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6ImF6dXJlY29udGFpbmVyaW5zdGFuY2VfcmVzdGFydGVkX2J5PS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJpZCI6InJ1c3Q6MS41Mi4xIiwibGF5ZXJzIjpbImZlODRjOWQ1YmZkZGQwN2EyNjI0ZDAwMzMzY2YxM2MxYTljOTQxZjNhMjYxZjEzZWFkNDRmYzZhOTNiYzBlN2EiLCI0ZGVkYWU0Mjg0N2M3MDRkYTg5MWEyOGMyNWQzMjIwMWExYWU0NDBiY2UyYWVjY2NmYThlNmYwM2I5N2E2YTZjIiwiNDFkNjRjZGViMzQ3YmYyMzZiNGMxM2I3NDAzYjYzM2ZmMTFmMWNmOTRkYmM3Y2Y4ODFhNDRkNmRhODhjNTE1NiIsImViMzY5MjFlMWY4MmFmNDZkZmUyNDhlZjhmMWIzYWZiNmE1MjMwYTY0MTgxZDk2MGQxMDIzN2EwOGNkNzNjNzkiLCJlNzY5ZDc0ODdjYzMxNGQzZWU3NDhhNDQ0MDgwNTMxN2MxOTI2MmM3YWNkMmZkYmRiMGQ0N2QyZTQ2MTNhMTVjIiwiMWI4MGYxMjBkYmQ4OGU0MzU1ZDYyNDFiNTE5YzNlMjUyOTAyMTVjNDY5NTE2YjQ5ZGVjZTljZjA3MTc1YTc2NiJdLCJtb3VudHMiOlt7ImRlc3RpbmF0aW9uIjoiL21vdW50L2F6dXJlZmlsZSIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvYXp1cmVGaWxlVm9sdW1lLy4rIiwidHlwZSI6ImJpbmQifSx7ImRlc3RpbmF0aW9uIjoiL2V0Yy9yZXNvbHYuY29uZiIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvcmVzb2x2Y29uZi8uKyIsInR5cGUiOiJiaW5kIn1dLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn0seyJhbGxvd19lbGV2YXRlZCI6ZmFsc2UsImFsbG93X3N0ZGlvX2FjY2VzcyI6dHJ1ZSwiY29tbWFuZCI6WyIvcGF1c2UiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vdXNyL2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4iLCJyZXF1aXJlZCI6dHJ1ZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJsYXllcnMiOlsiMTZiNTE0MDU3YTA2YWQ2NjVmOTJjMDI4NjNhY2EwNzRmZDU5NzZjNzU1ZDI2YmZmMTYzNjUyOTkxNjllODQxNSJdLCJtb3VudHMiOltdLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn1dCgphbGxvd19wcm9wZXJ0aWVzX2FjY2VzcyA6PSBmYWxzZQphbGxvd19kdW1wX3N0YWNrcyA6PSBmYWxzZQphbGxvd19ydW50aW1lX2xvZ2dpbmcgOj0gZmFsc2UKYWxsb3dfZW52aXJvbm1lbnRfdmFyaWFibGVfZHJvcHBpbmcgOj0gdHJ1ZQphbGxvd191bmVuY3J5cHRlZF9zY3JhdGNoIDo9IGZhbHNlCgoKCm1vdW50X2RldmljZSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9kZXZpY2UKdW5tb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9kZXZpY2UKbW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9vdmVybGF5CnVubW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay51bm1vdW50X292ZXJsYXkKY3JlYXRlX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5jcmVhdGVfY29udGFpbmVyCmV4ZWNfaW5fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfaW5fY29udGFpbmVyCmV4ZWNfZXh0ZXJuYWwgOj0gZGF0YS5mcmFtZXdvcmsuZXhlY19leHRlcm5hbApzaHV0ZG93bl9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuc2h1dGRvd25fY29udGFpbmVyCnNpZ25hbF9jb250YWluZXJfcHJvY2VzcyA6PSBkYXRhLmZyYW1ld29yay5zaWduYWxfY29udGFpbmVyX3Byb2Nlc3MKcGxhbjlfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfbW91bnQKcGxhbjlfdW5tb3VudCA6PSBkYXRhLmZyYW1ld29yay5wbGFuOV91bm1vdW50CmdldF9wcm9wZXJ0aWVzIDo9IGRhdGEuZnJhbWV3b3JrLmdldF9wcm9wZXJ0aWVzCmR1bXBfc3RhY2tzIDo9IGRhdGEuZnJhbWV3b3JrLmR1bXBfc3RhY2tzCnJ1bnRpbWVfbG9nZ2luZyA6PSBkYXRhLmZyYW1ld29yay5ydW50aW1lX2xvZ2dpbmcKbG9hZF9mcmFnbWVudCA6PSBkYXRhLmZyYW1ld29yay5sb2FkX2ZyYWdtZW50CnNjcmF0Y2hfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF9tb3VudApzY3JhdGNoX3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF91bm1vdW50CgpyZWFzb24gOj0geyJlcnJvcnMiOiBkYXRhLmZyYW1ld29yay5lcnJvcnN9"
        expected_output2 = "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3N2biA6PSAiMC4xMC4wIgpmcmFtZXdvcmtfc3ZuIDo9ICIwLjEuMCIKCmZyYWdtZW50cyA6PSBbCiAgewogICAgImZlZWQiOiAibWNyLm1pY3Jvc29mdC5jb20vYWNpL2FjaS1jYy1pbmZyYS1mcmFnbWVudCIsCiAgICAiaW5jbHVkZXMiOiBbCiAgICAgICJjb250YWluZXJzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjEuMC4wIgogIH0KXQoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbInB5dGhvbjMiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vY3VzdG9taXplZC9kaWZmZXJlbnQvcGF0aC92YWx1ZSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJMQU5HPUMuVVRGLTgiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiR1BHX0tFWT0wRDk2REY0RDQxMTBFNUM0M0ZCRkIxN0YyRDM0N0VBNkFBNjU0MjFEIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9WRVJTSU9OPTMuNi4xNCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fUElQX1ZFUlNJT049MjEuMi40IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9HRVRfUElQX1VSTD1odHRwczovL2dpdGh1Yi5jb20vcHlwYS9nZXQtcGlwL3Jhdy9jMjBiMGNmZDY0M2NkNGExOTI0NmNjZjIwNGUyOTk3YWY3MGY2YjIxL3B1YmxpYy9nZXQtcGlwLnB5IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlBZVEhPTl9HRVRfUElQX1NIQTI1Nj1mYTZmM2ZiOTNjY2UyMzRjZDRlOGRkMmJlYjU0YTUxYWI5YzI0NzY1M2I1Mjg1NWE0OGRkNDRlNmIyMWZmMjhiIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IlRFUk09eHRlcm0iLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiKCg/aSlGQUJSSUMpXy4rPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IkhPU1ROQU1FPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IlQoRSk/TVA9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiRmFicmljUGFja2FnZUZpbGVOYW1lPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6Ikhvc3RlZFNlcnZpY2VOYW1lPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX0FQSV9WRVJTSU9OPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IklERU5USVRZX0hFQURFUj0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJJREVOVElUWV9TRVJWRVJfVEhVTUJQUklOVD0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJhenVyZWNvbnRhaW5lcmluc3RhbmNlX3Jlc3RhcnRlZF9ieT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifV0sImV4ZWNfcHJvY2Vzc2VzIjpbXSwiaWQiOiJweXRob246My42LjE0LXNsaW0tYnVzdGVyIiwibGF5ZXJzIjpbIjI1NGNjODUzZGE2MDgxOTA1YzkxMDljOGI5ZDk5YzlmYjA5ODdiYTFkODhmNzI5MDg4OTAzY2ZmYjgwZjU1ZjEiLCJhNTY4ZjE5MDBiZWQ2MGEwNjQxYjc2Yjk5MWFkNDMxNDQ2ZDljM2EzNDRkN2IyNjFmMTBkZThkOGU3Mzc2M2FjIiwiYzcwYzUzMGU4NDJmNjYyMTViMGJkOTU1ODc3MTU3YmEyNGMzNzk5MzAzNTY3YzNmNTY3M2M0NTY2M2VhNGQxNSIsIjNlODZjM2NjZjE2NDJiZjU4NGRlMzNiNDljNzI0OGY4N2VlY2QwZjZkOGMwODM1M2RhYTM2Y2M3YWQwYTdiNmEiLCIxZTQ2ODRkOGM3Y2FhNzRjNjUyNDE3MmI0ZDVhMTU5YTEwODg3NjEzZWQ3MGYxOGQwYTU1ZDA1YjJhZjYxYWNkIl0sIm1vdW50cyI6W3siZGVzdGluYXRpb24iOiIvbW91bnQvZmlsZSIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvYXp1cmVGaWxlVm9sdW1lLy4rIiwidHlwZSI6ImJpbmQifSx7ImRlc3RpbmF0aW9uIjoiL2V0Yy9yZXNvbHYuY29uZiIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicnciXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvcmVzb2x2Y29uZi8uKyIsInR5cGUiOiJiaW5kIn1dLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn0seyJhbGxvd19lbGV2YXRlZCI6ZmFsc2UsImFsbG93X3N0ZGlvX2FjY2VzcyI6dHJ1ZSwiY29tbWFuZCI6WyIvcGF1c2UiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vdXNyL2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4iLCJyZXF1aXJlZCI6dHJ1ZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9XSwiZXhlY19wcm9jZXNzZXMiOltdLCJsYXllcnMiOlsiMTZiNTE0MDU3YTA2YWQ2NjVmOTJjMDI4NjNhY2EwNzRmZDU5NzZjNzU1ZDI2YmZmMTYzNjUyOTkxNjllODQxNSJdLCJtb3VudHMiOltdLCJzaWduYWxzIjpbXSwid29ya2luZ19kaXIiOiIvIn1dCgphbGxvd19wcm9wZXJ0aWVzX2FjY2VzcyA6PSBmYWxzZQphbGxvd19kdW1wX3N0YWNrcyA6PSBmYWxzZQphbGxvd19ydW50aW1lX2xvZ2dpbmcgOj0gZmFsc2UKYWxsb3dfZW52aXJvbm1lbnRfdmFyaWFibGVfZHJvcHBpbmcgOj0gdHJ1ZQphbGxvd191bmVuY3J5cHRlZF9zY3JhdGNoIDo9IGZhbHNlCgoKCm1vdW50X2RldmljZSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9kZXZpY2UKdW5tb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9kZXZpY2UKbW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay5tb3VudF9vdmVybGF5CnVubW91bnRfb3ZlcmxheSA6PSBkYXRhLmZyYW1ld29yay51bm1vdW50X292ZXJsYXkKY3JlYXRlX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5jcmVhdGVfY29udGFpbmVyCmV4ZWNfaW5fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfaW5fY29udGFpbmVyCmV4ZWNfZXh0ZXJuYWwgOj0gZGF0YS5mcmFtZXdvcmsuZXhlY19leHRlcm5hbApzaHV0ZG93bl9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuc2h1dGRvd25fY29udGFpbmVyCnNpZ25hbF9jb250YWluZXJfcHJvY2VzcyA6PSBkYXRhLmZyYW1ld29yay5zaWduYWxfY29udGFpbmVyX3Byb2Nlc3MKcGxhbjlfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfbW91bnQKcGxhbjlfdW5tb3VudCA6PSBkYXRhLmZyYW1ld29yay5wbGFuOV91bm1vdW50CmdldF9wcm9wZXJ0aWVzIDo9IGRhdGEuZnJhbWV3b3JrLmdldF9wcm9wZXJ0aWVzCmR1bXBfc3RhY2tzIDo9IGRhdGEuZnJhbWV3b3JrLmR1bXBfc3RhY2tzCnJ1bnRpbWVfbG9nZ2luZyA6PSBkYXRhLmZyYW1ld29yay5ydW50aW1lX2xvZ2dpbmcKbG9hZF9mcmFnbWVudCA6PSBkYXRhLmZyYW1ld29yay5sb2FkX2ZyYWdtZW50CnNjcmF0Y2hfbW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF9tb3VudApzY3JhdGNoX3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsuc2NyYXRjaF91bm1vdW50CgpyZWFzb24gOj0geyJlcnJvcnMiOiBkYXRhLmZyYW1ld29yay5lcnJvcnN9"

        self.assertEqual(output1, expected_output1)
        self.assertEqual(output2, expected_output2)


# @unittest.skip("not in use")
@pytest.mark.run(order=11)
class PolicyGeneratingArmInitContainer(unittest.TestCase):

    custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"simple-container-group"
            },
            "image": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"rust:1.52.1"
            },
            "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
            },

            "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
            },
            "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
            },
            "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
            },
            "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "environmentVariables": [
                        {
                        "name": "PORT",
                        "value": "80"
                        }
                    ],

                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "command": [
                        "/bin/bash",
                        "-c",
                        "while sleep 5; do cat /mnt/input/access.log; done"
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],
                "initContainers": [
                    {
                        "name": "init-container",
                        "properties": {
                            "image": "python:3.6.14-slim-buster",
                            "environmentVariables": [
                                {
                                    "name":"PATH",
                                    "value":"/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                                },
                                {
                                    "name":"LANG",
                                    "value":"C.UTF-8"
                                },
                                {
                                    "name":"GPG_KEY",
                                    "value":"0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D"
                                },
                                {
                                    "name":"PYTHON_VERSION",
                                    "value":"3.6.14"
                                },
                                {
                                    "name":"PYTHON_PIP_VERSION",
                                    "value":"21.2.4"
                                },
                                {
                                    "name":"PYTHON_GET_PIP_URL",
                                    "value":"https://github.com/pypa/get-pip/raw/c20b0cfd643cd4a19246ccf204e2997af70f6b21/public/get-pip.py"
                                },
                                {
                                    "name":"PYTHON_GET_PIP_SHA256",
                                    "value":"fa6f3fb93cce234cd4e8dd2beb54a51ab9c247653b52855a48dd44e6b21ff28b"
                                }
                            ],
                            "command": ["python3"]
                        }
                    }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

    @classmethod
    def setUpClass(cls):
        cls.aci_arm_policy = load_policy_from_arm_template_str(
            cls.custom_arm_json_default_value, ""
        )[0]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_arm_template_with_init_container(self):
        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, use_json=True
            )
        )

        python_image_name = regular_image_json[config.POLICY_FIELD_CONTAINERS][
            config.POLICY_FIELD_CONTAINERS_ELEMENTS
        ]["1"].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertTrue("python" in python_image_name)


# @unittest.skip("not in use")
@pytest.mark.run(order=12)
class PolicyGeneratingDisableStdioAccess(unittest.TestCase):

    custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"simple-container-group"
            },
            "image": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"rust:1.52.1"
            },
            "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
            },

            "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
            },
            "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
            },
            "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
            },
            "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "environmentVariables": [
                        {
                        "name": "PORT",
                        "value": "80"
                        }
                    ],

                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "command": [
                        "/bin/bash",
                        "-c",
                        "while sleep 5; do cat /mnt/input/access.log; done"
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

    @classmethod
    def setUpClass(cls):
        cls.aci_arm_policy = load_policy_from_arm_template_str(
            cls.custom_arm_json_default_value, "", disable_stdio=True
        )[0]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_arm_template_without_stdio_access(self):
        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        stdio_access = regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ALLOW_STDIO_ACCESS]

        # see if the remote image and the local one produce the same output
        self.assertFalse(stdio_access)


# @unittest.skip("not in use")
@pytest.mark.run(order=13)
class PrintExistingPolicy(unittest.TestCase):

    def test_printing_existing_policy(self):
        template = """
        {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "variables": {
                "image": "python:3.6.14-slim-buster"
            },


            "parameters": {
                "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"simple-container-group"
                },

                "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
                },
                "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
                },
                "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
                },
                "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
                },
                "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
                }
            },
            "resources": [
                {
                "name": "[parameters('containergroupname')]",
                "type": "Microsoft.ContainerInstance/containerGroups",
                "apiVersion": "2022-04-01-preview",
                "location": "[parameters('location')]",
                "properties": {
                    "containers": [
                    {
                        "name": "[parameters('containername')]",

                        "properties": {
                        "image": "[variables('image')]",
                        "command": [
                            "python3"
                        ],
                        "ports": [
                            {
                            "port": "[parameters('port')]"
                            }
                        ],
                        "resources": {
                            "requests": {
                            "cpu": "[parameters('cpuCores')]",
                            "memoryInGb": "[parameters('memoryInGb')]"
                            }
                        },
                        "volumeMounts": [
                                    {
                                        "name": "filesharevolume",
                                        "mountPath": "/aci/logs",
                                        "readOnly": false
                                    },
                                    {
                                        "name": "secretvolume",
                                        "mountPath": "/aci/secret",
                                        "readOnly": true
                                    }
                                ]
                        }
                    }
                    ],
                    "volumes": [
                        {
                            "name": "filesharevolume",
                            "azureFile": {
                                "shareName": "shareName1",
                                "storageAccountName": "storage-account-name",
                                "storageAccountKey": "storage-account-key"
                            }
                        },
                        {

                            "name": "secretvolume",
                            "secret": {
                                "mysecret1": "secret1",
                                "mysecret2": "secret2"
                            }
                        }

                    ],
                    "osType": "Linux",
                    "restartPolicy": "OnFailure",
                    "confidentialComputeProperties": {
                    "IsolationType": "SevSnp"
                    },
                    "ipAddress": {
                    "type": "Public",
                    "ports": [
                        {
                        "protocol": "Tcp",
                        "port": "[parameters( 'port' )]"
                        }
                    ]
                    }
                }
                }
            ],
            "outputs": {
                "containerIPv4Address": {
                "type": "string",
                "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
                }
            }
        }
        """
        template2 = """
        {
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "variables": {
    "image": "python:3.6.14-slim-buster"
  },
  "parameters": {
    "containergroupname": {
      "type": "string",
      "metadata": {
        "description": "Name for the container group"
      },
      "defaultValue": "simple-container-group"
    },
    "containername": {
      "type": "string",
      "metadata": {
        "description": "Name for the container"
      },
      "defaultValue": "simple-container"
    },
    "port": {
      "type": "string",
      "metadata": {
        "description": "Port to open on the container and the public IP address."
      },
      "defaultValue": "8080"
    },
    "cpuCores": {
      "type": "string",
      "metadata": {
        "description": "The number of CPU cores to allocate to the container."
      },
      "defaultValue": "1.0"
    },
    "memoryInGb": {
      "type": "string",
      "metadata": {
        "description": "The amount of memory to allocate to the container in gigabytes."
      },
      "defaultValue": "1.5"
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "Location for all resources."
      }
    }
  },
  "resources": [
    {
      "name": "[parameters('containergroupname')]",
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2022-04-01-preview",
      "location": "[parameters('location')]",
      "properties": {
        "containers": [
          {
            "name": "[parameters('containername')]",
            "properties": {
              "image": "[variables('image')]",
              "command": [
                "python3"
              ],
              "ports": [
                {
                  "port": "[parameters('port')]"
                }
              ],
              "resources": {
                "requests": {
                  "cpu": "[parameters('cpuCores')]",
                  "memoryInGb": "[parameters('memoryInGb')]"
                }
              },
              "volumeMounts": [
                {
                  "name": "filesharevolume",
                  "mountPath": "/aci/logs",
                  "readOnly": false
                },
                {
                  "name": "secretvolume",
                  "mountPath": "/aci/secret",
                  "readOnly": true
                }
              ]
            }
          }
        ],
        "volumes": [
          {
            "name": "filesharevolume",
            "azureFile": {
              "shareName": "shareName1",
              "storageAccountName": "storage-account-name",
              "storageAccountKey": "storage-account-key"
            }
          },
          {
            "name": "secretvolume",
            "secret": {
              "mysecret1": "secret1",
              "mysecret2": "secret2"
            }
          }
        ],
        "osType": "Linux",
        "restartPolicy": "OnFailure",
        "confidentialComputeProperties": {
          "IsolationType": "SevSnp",
          "ccePolicy": "cGFja2FnZSBwb2xpY3kKCmltcG9ydCBmdXR1cmUua2V5d29yZHMuZXZlcnkKaW1wb3J0IGZ1dHVyZS5rZXl3b3Jkcy5pbgoKYXBpX3N2biA6PSAiMC4xMC4wIgpmcmFtZXdvcmtfc3ZuIDo9ICIwLjEuMCIKCmZyYWdtZW50cyA6PSBbCiAgewogICAgImZlZWQiOiAibWNyLm1pY3Jvc29mdC5jb20vYWNpL2FjaS1jYy1pbmZyYS1mcmFnbWVudCIsCiAgICAiaW5jbHVkZXMiOiBbCiAgICAgICJjb250YWluZXJzIgogICAgXSwKICAgICJpc3N1ZXIiOiAiZGlkOng1MDk6MDpzaGEyNTY6SV9faXVMMjVvWEVWRmRUUF9hQkx4X2VUMVJQSGJDUV9FQ0JRZllacHQ5czo6ZWt1OjEuMy42LjEuNC4xLjMxMS43Ni41OS4xLjMiLAogICAgIm1pbmltdW1fc3ZuIjogIjEuMC4wIgogIH0KXQoKY29udGFpbmVycyA6PSBbeyJhbGxvd19lbGV2YXRlZCI6dHJ1ZSwiYWxsb3dfc3RkaW9fYWNjZXNzIjp0cnVlLCJjb21tYW5kIjpbInB5dGhvbjMiXSwiZW52X3J1bGVzIjpbeyJwYXR0ZXJuIjoiUEFUSD0vdXNyL2xvY2FsL2JpbjovdXNyL2xvY2FsL3NiaW46L3Vzci9sb2NhbC9iaW46L3Vzci9zYmluOi91c3IvYmluOi9zYmluOi9iaW4iLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiTEFORz1DLlVURi04IiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IkdQR19LRVk9MEQ5NkRGNEQ0MTEwRTVDNDNGQkZCMTdGMkQzNDdFQTZBQTY1NDIxRCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fVkVSU0lPTj0zLjYuMTQiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiUFlUSE9OX1BJUF9WRVJTSU9OPTIxLjIuNCIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fR0VUX1BJUF9VUkw9aHR0cHM6Ly9naXRodWIuY29tL3B5cGEvZ2V0LXBpcC9yYXcvYzIwYjBjZmQ2NDNjZDRhMTkyNDZjY2YyMDRlMjk5N2FmNzBmNmIyMS9wdWJsaWMvZ2V0LXBpcC5weSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJQWVRIT05fR0VUX1BJUF9TSEEyNTY9ZmE2ZjNmYjkzY2NlMjM0Y2Q0ZThkZDJiZWI1NGE1MWFiOWMyNDc2NTNiNTI4NTVhNDhkZDQ0ZTZiMjFmZjI4YiIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifSx7InBhdHRlcm4iOiJURVJNPXh0ZXJtIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InN0cmluZyJ9LHsicGF0dGVybiI6IigoP2kpRkFCUklDKV8uKz0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJIT1NUTkFNRT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJUKEUpP01QPS4rIiwicmVxdWlyZWQiOmZhbHNlLCJzdHJhdGVneSI6InJlMiJ9LHsicGF0dGVybiI6IkZhYnJpY1BhY2thZ2VGaWxlTmFtZT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJIb3N0ZWRTZXJ2aWNlTmFtZT0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJJREVOVElUWV9BUElfVkVSU0lPTj0uKyIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJyZTIifSx7InBhdHRlcm4iOiJJREVOVElUWV9IRUFERVI9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiSURFTlRJVFlfU0VSVkVSX1RIVU1CUFJJTlQ9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn0seyJwYXR0ZXJuIjoiYXp1cmVjb250YWluZXJpbnN0YW5jZV9yZXN0YXJ0ZWRfYnk9LisiLCJyZXF1aXJlZCI6ZmFsc2UsInN0cmF0ZWd5IjoicmUyIn1dLCJleGVjX3Byb2Nlc3NlcyI6W10sImlkIjoicHl0aG9uOjMuNi4xNC1zbGltLWJ1c3RlciIsImxheWVycyI6WyIyNTRjYzg1M2RhNjA4MTkwNWM5MTA5YzhiOWQ5OWM5ZmIwOTg3YmExZDg4ZjcyOTA4ODkwM2NmZmI4MGY1NWYxIiwiYTU2OGYxOTAwYmVkNjBhMDY0MWI3NmI5OTFhZDQzMTQ0NmQ5YzNhMzQ0ZDdiMjYxZjEwZGU4ZDhlNzM3NjNhYyIsImM3MGM1MzBlODQyZjY2MjE1YjBiZDk1NTg3NzE1N2JhMjRjMzc5OTMwMzU2N2MzZjU2NzNjNDU2NjNlYTRkMTUiLCIzZTg2YzNjY2YxNjQyYmY1ODRkZTMzYjQ5YzcyNDhmODdlZWNkMGY2ZDhjMDgzNTNkYWEzNmNjN2FkMGE3YjZhIiwiMWU0Njg0ZDhjN2NhYTc0YzY1MjQxNzJiNGQ1YTE1OWExMDg4NzYxM2VkNzBmMThkMGE1NWQwNWIyYWY2MWFjZCJdLCJtb3VudHMiOlt7ImRlc3RpbmF0aW9uIjoiL2FjaS9sb2dzIiwib3B0aW9ucyI6WyJyYmluZCIsInJzaGFyZWQiLCJydyJdLCJzb3VyY2UiOiJzYW5kYm94Oi8vL3RtcC9hdGxhcy9henVyZUZpbGVWb2x1bWUvLisiLCJ0eXBlIjoiYmluZCJ9LHsiZGVzdGluYXRpb24iOiIvYWNpL3NlY3JldCIsIm9wdGlvbnMiOlsicmJpbmQiLCJyc2hhcmVkIiwicm8iXSwic291cmNlIjoic2FuZGJveDovLy90bXAvYXRsYXMvc2VjcmV0c1ZvbHVtZS8uKyIsInR5cGUiOiJiaW5kIn0seyJkZXN0aW5hdGlvbiI6Ii9ldGMvcmVzb2x2LmNvbmYiLCJvcHRpb25zIjpbInJiaW5kIiwicnNoYXJlZCIsInJ3Il0sInNvdXJjZSI6InNhbmRib3g6Ly8vdG1wL2F0bGFzL3Jlc29sdmNvbmYvLisiLCJ0eXBlIjoiYmluZCJ9XSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9LHsiYWxsb3dfZWxldmF0ZWQiOmZhbHNlLCJhbGxvd19zdGRpb19hY2Nlc3MiOnRydWUsImNvbW1hbmQiOlsiL3BhdXNlIl0sImVudl9ydWxlcyI6W3sicGF0dGVybiI6IlBBVEg9L3Vzci9sb2NhbC9zYmluOi91c3IvbG9jYWwvYmluOi91c3Ivc2JpbjovdXNyL2Jpbjovc2JpbjovYmluIiwicmVxdWlyZWQiOnRydWUsInN0cmF0ZWd5Ijoic3RyaW5nIn0seyJwYXR0ZXJuIjoiVEVSTT14dGVybSIsInJlcXVpcmVkIjpmYWxzZSwic3RyYXRlZ3kiOiJzdHJpbmcifV0sImV4ZWNfcHJvY2Vzc2VzIjpbXSwibGF5ZXJzIjpbIjE2YjUxNDA1N2EwNmFkNjY1ZjkyYzAyODYzYWNhMDc0ZmQ1OTc2Yzc1NWQyNmJmZjE2MzY1Mjk5MTY5ZTg0MTUiXSwibW91bnRzIjpbXSwic2lnbmFscyI6W10sIndvcmtpbmdfZGlyIjoiLyJ9XQoKYWxsb3dfcHJvcGVydGllc19hY2Nlc3MgOj0gZmFsc2UKYWxsb3dfZHVtcF9zdGFja3MgOj0gZmFsc2UKYWxsb3dfcnVudGltZV9sb2dnaW5nIDo9IGZhbHNlCmFsbG93X2Vudmlyb25tZW50X3ZhcmlhYmxlX2Ryb3BwaW5nIDo9IHRydWUKYWxsb3dfdW5lbmNyeXB0ZWRfc2NyYXRjaCA6PSBmYWxzZQoKCgptb3VudF9kZXZpY2UgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfZGV2aWNlCnVubW91bnRfZGV2aWNlIDo9IGRhdGEuZnJhbWV3b3JrLnVubW91bnRfZGV2aWNlCm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsubW91bnRfb3ZlcmxheQp1bm1vdW50X292ZXJsYXkgOj0gZGF0YS5mcmFtZXdvcmsudW5tb3VudF9vdmVybGF5CmNyZWF0ZV9jb250YWluZXIgOj0gZGF0YS5mcmFtZXdvcmsuY3JlYXRlX2NvbnRhaW5lcgpleGVjX2luX2NvbnRhaW5lciA6PSBkYXRhLmZyYW1ld29yay5leGVjX2luX2NvbnRhaW5lcgpleGVjX2V4dGVybmFsIDo9IGRhdGEuZnJhbWV3b3JrLmV4ZWNfZXh0ZXJuYWwKc2h1dGRvd25fY29udGFpbmVyIDo9IGRhdGEuZnJhbWV3b3JrLnNodXRkb3duX2NvbnRhaW5lcgpzaWduYWxfY29udGFpbmVyX3Byb2Nlc3MgOj0gZGF0YS5mcmFtZXdvcmsuc2lnbmFsX2NvbnRhaW5lcl9wcm9jZXNzCnBsYW45X21vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnBsYW45X21vdW50CnBsYW45X3VubW91bnQgOj0gZGF0YS5mcmFtZXdvcmsucGxhbjlfdW5tb3VudApnZXRfcHJvcGVydGllcyA6PSBkYXRhLmZyYW1ld29yay5nZXRfcHJvcGVydGllcwpkdW1wX3N0YWNrcyA6PSBkYXRhLmZyYW1ld29yay5kdW1wX3N0YWNrcwpydW50aW1lX2xvZ2dpbmcgOj0gZGF0YS5mcmFtZXdvcmsucnVudGltZV9sb2dnaW5nCmxvYWRfZnJhZ21lbnQgOj0gZGF0YS5mcmFtZXdvcmsubG9hZF9mcmFnbWVudApzY3JhdGNoX21vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnNjcmF0Y2hfbW91bnQKc2NyYXRjaF91bm1vdW50IDo9IGRhdGEuZnJhbWV3b3JrLnNjcmF0Y2hfdW5tb3VudAoKcmVhc29uIDo9IHsiZXJyb3JzIjogZGF0YS5mcmFtZXdvcmsuZXJyb3JzfQ=="
        },
        "ipAddress": {
          "type": "Public",
          "ports": [
            {
              "protocol": "Tcp",
              "port": "[parameters( 'port' )]"
            }
          ]
        }
      }
    }
  ],
  "outputs": {
    "containerIPv4Address": {
      "type": "string",
      "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
    }
  }
}
"""
        # write template to file for testing
        with open("test_template.json", "w") as f:
            f.write(template)

        with open("test_template2.json", "w") as f:
            f.write(template2)
        try:
            with self.assertRaises(SystemExit) as exc_info:
                acipolicygen_confcom(None, "test_template.json", None, None, None, None, print_existing_policy=True)

            self.assertEqual(exc_info.exception.code, 1)

            with self.assertRaises(SystemExit) as exc_info:
                acipolicygen_confcom(None, "test_template2.json", None, None, None, None, print_existing_policy=True)

            self.assertEqual(exc_info.exception.code, 0)
        finally:
            # delete test file
            os.remove("test_template.json")
            os.remove("test_template2.json")

# @unittest.skip("not in use")
@pytest.mark.run(order=14)
class PolicyGeneratingArmWildcardEnvs(unittest.TestCase):
    custom_json = """
        {
            "version": "1.0",
            "containers": [
                {
                    "containerImage": "python:3.6.14-slim-buster",
                    "environmentVariables": [
                        {
                            "name":"PATH",
                            "value":"/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                            "strategy":"string"
                        },
                        {
                            "name":"LANG",
                            "value":"C.UTF-8",
                            "strategy":"string"
                        },
                        {
                            "name":"GPG_KEY",
                            "value":"0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_VERSION",
                            "value":"3.6.14",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_PIP_VERSION",
                            "value":"21.2.4",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_GET_PIP_URL",
                            "value":"https://github.com/pypa/get-pip/raw/c20b0cfd643cd4a19246ccf204e2997af70f6b21/public/get-pip.py",
                            "strategy":"string"
                        },
                        {
                            "name":"PYTHON_GET_PIP_SHA256",
                            "value":"fa6f3fb93cce234cd4e8dd2beb54a51ab9c247653b52855a48dd44e6b21ff28b",
                            "strategy":"string"
                        },
                        {
                            "name":"TEST_WILDCARD_ENV",
                            "value":".*",
                            "strategy":"re2"
                        }
                    ],
                    "command": ["python3"],
                    "workingDir": "",
                    "mounts": []
                }
            ]
        }
        """

    custom_arm_json_error = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "python:3.6.14-slim-buster"
        },


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"simple-container-group"
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            },
            "defaultValue":"simple-container"
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "command": [
                        "python3"
                    ],
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    },
                    "environmentVariables": [
                        {
                            "name": "PATH",
                            "value": "/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                        },
                        {
                            "name": "TEST_WILDCARD_ENV"
                        }
                    ]
                    }
                }
                ],
                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
    custom_arm_json_error2 = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "python:3.6.14-slim-buster"
        },


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"simple-container-group"
            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            },
            "defaultValue":"simple-container"
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "command": [
                        "python3"
                    ],
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    },
                    "environmentVariables": [
                        {
                            "name": "[parameters('fake_parameter')]",
                            "value": "/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                        }

                    ]
                    }
                }
                ],
                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
    custom_arm_json = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "python:3.6.14-slim-buster"
        },


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"simple-container-group"
            },
            "wildcardParamName": {
            "defaultValue": "TEST_WILDCARD_ENV",
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }

            },
            "wildcardParamValue": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }

            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            },
            "defaultValue":"simple-container"
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "command": [
                        "python3"
                    ],
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    },
                    "environmentVariables": [
                        {
                            "name": "PATH",
                            "value": "/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                        },
                        {
                            "name": "[parameters('wildcardParamName')]",
                            "value": "[parameters('wildcardParamValue')]"
                        }
                    ]
                    }
                }
                ],
                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
    custom_arm_json2 = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "python:3.6.14-slim-buster"
        },


        "parameters": {
            "containergroupname": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            },
            "defaultValue":"simple-container-group"
            },
            "wildcardParamName": {
            "defaultValue": "TEST_WILDCARD_ENV",
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }

            },
            "wildcardParamValue": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group"
            }

            },
            "wildcardParamValue2": {
            "type": "string",
            "metadata": {
                "description": "Name for the container group2"
            }

            },

            "containername": {
            "type": "string",
            "metadata": {
                "description": "Name for the container"
            },
            "defaultValue":"simple-container"
            },
            "port": {
            "type": "string",
            "metadata": {
                "description": "Port to open on the container and the public IP address."
            },
            "defaultValue": "8080"
            },
            "cpuCores": {
            "type": "string",
            "metadata": {
                "description": "The number of CPU cores to allocate to the container."
            },
            "defaultValue": "1.0"
            },
            "memoryInGb": {
            "type": "string",
            "metadata": {
                "description": "The amount of memory to allocate to the container in gigabytes."
            },
            "defaultValue": "1.5"
            },
            "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources."
            }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "command": [
                        "python3"
                    ],
                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    },
                    "environmentVariables": [
                        {
                            "name": "PATH",
                            "value": "/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                        },
                        {
                            "name": "[parameters('wildcardParamName')]",
                            "value": "[parameters('wildcardParamValue')]"
                        },
                        {
                            "name": "WILDCARD2",
                            "value": "[parameters('wildcardParamValue2')]"
                        }
                    ]
                    }
                }
                ],
                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """
    aci_policy = None
    aci_policy2 = None

    @classmethod
    def setUpClass(cls):
        with load_policy_from_str(cls.custom_json) as aci_policy:
            aci_policy.populate_policy_content_for_all_images()
            cls.aci_policy = aci_policy

        with patch('builtins.input', return_value='y'):
            cls.aci_arm_policy = load_policy_from_arm_template_str(cls.custom_arm_json, "")[
                0
            ]
            cls.aci_arm_policy.populate_policy_content_for_all_images()

        with patch('builtins.input', side_effect=['y', 'n']):
            cls.aci_arm_policy2 = load_policy_from_arm_template_str(cls.custom_arm_json2, "")[
                0
            ]
            cls.aci_arm_policy2.populate_policy_content_for_all_images()

    def test_arm_template_policy_regex(self):
        # deep diff the output policies from the regular policy.json and the ARM template
        normalized_aci_policy = json.loads(
            self.aci_policy.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        normalized_aci_arm_policy = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW,rego_boilerplate=False
            )
        )

        normalized_aci_policy[0].pop(config.POLICY_FIELD_CONTAINERS_ID)

        normalized_aci_arm_policy[0].pop(config.POLICY_FIELD_CONTAINERS_ID)

        self.assertEqual(
            deepdiff.DeepDiff(
                normalized_aci_policy, normalized_aci_arm_policy, ignore_order=True
            ),
            {},
        )

    def test_wildcard_env_var(self):
        normalized_aci_arm_policy = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(
            normalized_aci_arm_policy[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS
                ][1][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY],
            "re2"
        )

        self.assertEqual(
            normalized_aci_arm_policy[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS
                ][1][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE],
            "TEST_WILDCARD_ENV=.*"
        )

        normalized_aci_arm_policy2 = json.loads(
            self.aci_arm_policy2.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertFalse(
            any([item.get("name") == "WILDCARD2" for item in normalized_aci_arm_policy2[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]])
        )

        self.assertEqual(
            normalized_aci_arm_policy2[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS
                ][1][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE],
            "TEST_WILDCARD_ENV=.*"
        )

    def test_wildcard_env_var_invalid(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            load_policy_from_arm_template_str(self.custom_arm_json_error, "")
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            out = load_policy_from_arm_template_str(self.custom_arm_json_error2, "")
            for policy in out:
                policy.populate_policy_content_for_all_images()

        self.assertEqual(wrapped_exit.exception.code, 1)


# @unittest.skip("not in use")
@pytest.mark.run(order=15)
class PolicyGeneratingEdgeCases(unittest.TestCase):

    custom_arm_json_default_value = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",


        "parameters": {
            "containergroupname": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"simple-container-group"
            },
            "image": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"rust:1.52.1"
            },
            "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
            },

            "port": {
                "type": "string",
                "metadata": {
                    "description": "Port to open on the container and the public IP address."
                },
                "defaultValue": "8080"
            },
            "cpuCores": {
                "type": "string",
                "metadata": {
                    "description": "The number of CPU cores to allocate to the container."
                },
                "defaultValue": "1.0"
            },
            "memoryInGb": {
                "type": "string",
                "metadata": {
                    "description": "The amount of memory to allocate to the container in gigabytes."
                },
                "defaultValue": "1.5"
            },
            "location": {
                "type": "string",
                "defaultValue": "[resourceGroup().location]",
                "metadata": {
                    "description": "Location for all resources."
                }
            }
        },
        "resources": [
            {
            "name": "[parameters('containergroupname')]",
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2022-04-01-preview",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "image": "[parameters('image')]",
                    "environmentVariables": [
                        {
                        "name": "PORT",
                        "value": "parameters('abc')"
                        }
                    ],

                    "ports": [
                        {
                        "port": "[parameters('port')]"
                        }
                    ],
                    "command": [
                        "/bin/bash",
                        "-c",
                        "while sleep 5; do cat /mnt/input/access.log; done"
                    ],
                    "resources": {
                        "requests": {
                        "cpu": "[parameters('cpuCores')]",
                        "memoryInGb": "[parameters('memoryInGb')]"
                        }
                    }
                    }
                }
                ],

                "osType": "Linux",
                "restartPolicy": "OnFailure",
                "confidentialComputeProperties": {
                "IsolationType": "SevSnp"
                },
                "ipAddress": {
                "type": "Public",
                "ports": [
                    {
                    "protocol": "Tcp",
                    "port": "[parameters( 'port' )]"
                    }
                ]
                }
            }
            }
        ],
        "outputs": {
            "containerIPv4Address": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.ContainerInstance/containerGroups/', parameters('containergroupname'))).ipAddress.ip]"
            }
        }
    }
    """

    @classmethod
    def setUpClass(cls):
        cls.aci_arm_policy = load_policy_from_arm_template_str(
            cls.custom_arm_json_default_value, ""
        )[0]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_arm_template_with_env_var(self):
        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        env_var = regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS][0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE]

        # see if the remote image and the local one produce the same output
        self.assertEquals(env_var, "PORT=parameters('abc')")
        self.assertEquals(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ID], "rust:1.52.1")