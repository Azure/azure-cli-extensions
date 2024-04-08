# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
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
from azext_confcom.template_util import case_insensitive_dict_get, extract_confidential_properties, extract_containers_from_text, DockerClient

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


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
            "apiVersion": "2023-05-01",
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
            self.aci_policy.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        normalized_aci_arm_policy = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
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

    def test_default_infrastructure_svn(self):
        self.assertEqual(
            config.DEFAULT_REGO_FRAGMENTS[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ],
            self.aci_arm_policy._fragments[0][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
            ],
        )

    def test_default_pause_container(self):
        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )
        # check default pause container
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_CONTAINERS[0], regular_image_json[1], ignore_order=True), {})


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
            "apiVersion": "2023-05-01",
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
                "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
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
                "defaultValue": "python:3.6.14-slim-buster"
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
            "apiVersion": "2023-05-01",
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
            "defaultValue":"python:3.6.14-slim-buster"
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
            "apiVersion": "2023-05-01",
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
            output[0].get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        # see if we have environment variables specific to the python image in the parameter file
        python_flag = False
        for value in output_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]:
            if "PYTHON" in value[config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE]:
                python_flag = True
        self.assertTrue(python_flag)


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
            "defaultValue":"python:3.6.14-slim-buster"
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
            "apiVersion": "2023-05-01",
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
        output_json = json.loads(output[0].get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False))

        for value in output_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS]:
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
        for value in output_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_COMMANDS]:
            self.assertTrue(value in expected)


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
                "defaultValue":"alpine:3.16"
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
            "apiVersion": "2023-05-01",
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
        with DockerClient() as client:
            # client = docker.from_env()
            original_image = "alpine:3.16"
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

            # client.close()

        clean_room = load_policy_from_arm_template_str(
            custom_arm_json_default_value, self.parameter_file
        )
        clean_room[0].populate_policy_content_for_all_images()

        regular_image_json = json.loads(
            regular_image[0].get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        clean_room_json = json.loads(
            clean_room[0].get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        regular_image_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertEqual(
            deepdiff.DeepDiff(regular_image_json, clean_room_json, ignore_order=True),
            {},
        )


class PolicyDiff(unittest.TestCase):
    custom_json = """
      {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "variables": {
        "container1name": "aci-test",
        "container1image": "alpine:3.16"
    },
    "resources": [
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2023-05-01",
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
        "container1image": "alpine:3.16"
    },
    "resources": [
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2023-05-01",
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
                            "securityContext": {
                                "allowPrivilegeEscalation": false
                            },
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
                            "allow_elevated": true,
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
        container_start = "containers := "
        cls.containers = json.loads(extract_containers_from_text(cls.aci_policy.get_serialized_output(OutputType.PRETTY_PRINT), container_start))

    def test_policy_diff(self):
        self.aci_policy._existing_cce_policy = self.containers
        is_valid, diff = self.aci_policy.validate_cce_policy()
        self.assertTrue(is_valid)
        self.assertTrue(not diff)

    def test_incorrect_policy_diff(self):
        self.aci_policy2._existing_cce_policy = self.containers
        is_valid, diff = self.aci_policy2.validate_cce_policy()
        self.assertFalse(is_valid)
        expected_diff = {
            "alpine:3.16": {
                "values_changed": {
                    "mounts": [
                        {
                            "tested_value": "/mount/azure",
                            "policy_value": "/mount/azurefile",
                        }
                    ],
                    "no_new_privileges": [{"tested_value": True, "policy_value": False}]
                },
                "env_rules": [
                    "environment variable with rule 'TEST_REGEXP_ENV=test_regexp_en' does not match strings or regex in policy rules",
                    "environment variable with rule 'ENV_VALUE=input_value' does not match strings or regex in policy rules",
                ],
            }
        }

        self.assertEqual(diff, expected_diff)


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
            "apiVersion": "2023-05-01",
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
        cls.minimum_svn = "2"
        cls.aci_arm_policy = load_policy_from_arm_template_str(
            cls.custom_arm_json, "", infrastructure_svn=cls.minimum_svn
        )[0]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_update_infrastructure_svn(self):
        fragment_start = "fragments := "
        fragments = json.loads(extract_containers_from_text(self.aci_arm_policy.get_serialized_output(OutputType.PRETTY_PRINT), fragment_start))

        for fragment in fragments:
            if fragment["feed"] == 'mcr.microsoft.com/aci/aci-cc-infra-fragment':
                self.assertEqual(
                    self.minimum_svn,
                    fragment[
                        config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
                    ],
                )
                return
        self.fail("aci-cc-infra-fragment not found")


class MultiplePolicyTemplate(unittest.TestCase):
    custom_json = """
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "variables": {
        "container1name": "aci-test",
        "container1image": "alpine:3.16",
        "container2name": "aci-test2",
        "container2image": "python:3.6.14-slim-buster"
    },
    "resources": [
        {
            "type": "Microsoft.ContainerInstance/containerGroups",
            "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
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
        cls.aci_policy.populate_policy_content_for_all_images(faster_hashing=True)
        cls.aci_policy2.populate_policy_content_for_all_images(faster_hashing=True)

    def test_multiple_policies(self):
        container_start = "containers := "
        policy2_containers = json.loads(extract_containers_from_text(self.aci_policy2.get_serialized_output(OutputType.PRETTY_PRINT), container_start))

        self.aci_policy._existing_cce_policy = policy2_containers
        is_valid, diff = self.aci_policy.validate_cce_policy()
        self.assertFalse(is_valid)
        # just check to make sure the containers in both policies are different
        expected_diff = {"alpine:3.16": "alpine:3.16 not found in policy"}
        self.assertEqual(diff, expected_diff)


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
                "defaultValue":"alpine:3.16"
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
            "apiVersion": "2023-05-01",
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
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        python_image_name = regular_image_json[1].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertTrue("python" in python_image_name)


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
                "defaultValue":"alpine:3.16"
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
            "apiVersion": "2023-05-01",
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

        stdio_access = regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_STDIO_ACCESS]

        # see if the remote image and the local one produce the same output
        self.assertFalse(stdio_access)


class PolicyGeneratingAllowElevated(unittest.TestCase):

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
                "defaultValue":"alpine:3.16"
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",

            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",
                    "properties": {
                    "securityContext":{
                        "privileged":"false"
                    },
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

    def test_arm_template_allow_elevated_false(self):
        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        allow_elevated = regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ALLOW_ELEVATED]

        # see if the remote image and the local one produce the same output
        self.assertFalse(allow_elevated)


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
                "apiVersion": "2023-05-01",
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
      "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
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
                output_type=OutputType.RAW, rego_boilerplate=False
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
            normalized_aci_arm_policy[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS][1][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_STRATEGY
            ],
            "re2",
        )

        self.assertEqual(
            normalized_aci_arm_policy[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS][1][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
            ],
            "TEST_WILDCARD_ENV=.*",
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
            normalized_aci_arm_policy2[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS][1][
                config.POLICY_FIELD_CONTAINERS_ELEMENTS_ENVS_RULE
            ],
            "TEST_WILDCARD_ENV=.*",
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
                "defaultValue":"alpine:3.16"
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
            "apiVersion": "2023-05-01",
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
        self.assertEqual(env_var, "PORT=parameters('abc')")
        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ID], "alpine:3.16")


class PolicyGeneratingSecurityContext(unittest.TestCase):
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
            "apiVersion": "2023-05-01",
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext": {
                        "privileged": "true",
                        "capabilities":{
                            "add": ["CAP_SYS_TIME","CAP_DAC_READ_SEARCH"],
                            "drop": ["CAP_CHOWN","CAP_KILL"]
                        },
                        "runAsGroup": 123,
                        "runAsUser": 456,
                        "seccompProfile": "seccompStr"
                    },
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

    custom_arm_json3 = """
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext":{
                        "privileged": true,
                        "allowPrivilegeEscalation": true,
                        "runAsGroup":123,
                        "runAsUser":456
                    },
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

    custom_arm_json4 = """
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext": {
                        "privileged": "false",
                        "capabilities":{
                            "add": ["CAP_SYS_TIME","CAP_DAC_READ_SEARCH"],
                            "drop": ["CAP_CHOWN","CAP_KILL"]
                        },
                        "runAsGroup": 123,
                        "runAsUser": 456
                    },
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

    @classmethod
    def setUpClass(cls):
        seccomp_profile_contents = "ewoJImNvbW1lbnQiOiAiRGVmYXVsdCBtb2J5IHNlY2NvbXAgcG9saWN5IGNvbmZpZyBmaWxlIGF0OiBodHRwczovL2dpdGh1Yi5jb20vbW9ieS9tb2J5L2Jsb2IvbWFzdGVyL3Byb2ZpbGVzL3NlY2NvbXAvZGVmYXVsdC5qc29uIiwKCSJkZWZhdWx0QWN0aW9uIjogIlNDTVBfQUNUX0VSUk5PIiwKCSJkZWZhdWx0RXJybm9SZXQiOiAxLAoJImFyY2hNYXAiOiBbCgkJewoJCQkiYXJjaGl0ZWN0dXJlIjogIlNDTVBfQVJDSF9YODZfNjQiLAoJCQkic3ViQXJjaGl0ZWN0dXJlcyI6IFsKCQkJCSJTQ01QX0FSQ0hfWDg2IiwKCQkJCSJTQ01QX0FSQ0hfWDMyIgoJCQldCgkJfSwKCQl7CgkJCSJhcmNoaXRlY3R1cmUiOiAiU0NNUF9BUkNIX0FBUkNINjQiLAoJCQkic3ViQXJjaGl0ZWN0dXJlcyI6IFsKCQkJCSJTQ01QX0FSQ0hfQVJNIgoJCQldCgkJfSwKCQl7CgkJCSJhcmNoaXRlY3R1cmUiOiAiU0NNUF9BUkNIX01JUFM2NCIsCgkJCSJzdWJBcmNoaXRlY3R1cmVzIjogWwoJCQkJIlNDTVBfQVJDSF9NSVBTIiwKCQkJCSJTQ01QX0FSQ0hfTUlQUzY0TjMyIgoJCQldCgkJfSwKCQl7CgkJCSJhcmNoaXRlY3R1cmUiOiAiU0NNUF9BUkNIX01JUFM2NE4zMiIsCgkJCSJzdWJBcmNoaXRlY3R1cmVzIjogWwoJCQkJIlNDTVBfQVJDSF9NSVBTIiwKCQkJCSJTQ01QX0FSQ0hfTUlQUzY0IgoJCQldCgkJfSwKCQl7CgkJCSJhcmNoaXRlY3R1cmUiOiAiU0NNUF9BUkNIX01JUFNFTDY0IiwKCQkJInN1YkFyY2hpdGVjdHVyZXMiOiBbCgkJCQkiU0NNUF9BUkNIX01JUFNFTCIsCgkJCQkiU0NNUF9BUkNIX01JUFNFTDY0TjMyIgoJCQldCgkJfSwKCQl7CgkJCSJhcmNoaXRlY3R1cmUiOiAiU0NNUF9BUkNIX01JUFNFTDY0TjMyIiwKCQkJInN1YkFyY2hpdGVjdHVyZXMiOiBbCgkJCQkiU0NNUF9BUkNIX01JUFNFTCIsCgkJCQkiU0NNUF9BUkNIX01JUFNFTDY0IgoJCQldCgkJfSwKCQl7CgkJCSJhcmNoaXRlY3R1cmUiOiAiU0NNUF9BUkNIX1MzOTBYIiwKCQkJInN1YkFyY2hpdGVjdHVyZXMiOiBbCgkJCQkiU0NNUF9BUkNIX1MzOTAiCgkJCV0KCQl9CgldLAoJInN5c2NhbGxzIjogWwoJCXsKCQkJIm5hbWVzIjogWwoJCQkJImFjY2VwdCIsCgkJCQkiYWNjZXB0NCIsCgkJCQkiYWNjZXNzIiwKCQkJCSJhZGp0aW1leCIsCgkJCQkiYWxhcm0iLAoJCQkJImJpbmQiLAoJCQkJImJyayIsCgkJCQkiY2FwZ2V0IiwKCQkJCSJjaGRpciIsCgkJCQkiY2htb2QiLAoJCQkJImNsb2NrX2FkanRpbWUiLAoJCQkJImNsb2NrX2FkanRpbWU2NCIsCgkJCQkiY2xvY2tfZ2V0cmVzIiwKCQkJCSJjbG9ja19nZXRyZXNfdGltZTY0IiwKCQkJCSJjbG9ja19nZXR0aW1lIiwKCQkJCSJjbG9ja19nZXR0aW1lNjQiLAoJCQkJImNsb2NrX25hbm9zbGVlcCIsCgkJCQkiY2xvY2tfbmFub3NsZWVwX3RpbWU2NCIsCgkJCQkiY2xvc2UiLAoJCQkJImNsb3NlX3JhbmdlIiwKCQkJCSJjb25uZWN0IiwKCQkJCSJjb3B5X2ZpbGVfcmFuZ2UiLAoJCQkJImNyZWF0IiwKCQkJCSJkdXAiLAoJCQkJImR1cDIiLAoJCQkJImR1cDMiLAoJCQkJImVwb2xsX2NyZWF0ZSIsCgkJCQkiZXBvbGxfY3JlYXRlMSIsCgkJCQkiZXBvbGxfY3RsIiwKCQkJCSJlcG9sbF9jdGxfb2xkIiwKCQkJCSJlcG9sbF9wd2FpdCIsCgkJCQkiZXBvbGxfcHdhaXQyIiwKCQkJCSJlcG9sbF93YWl0IiwKCQkJCSJlcG9sbF93YWl0X29sZCIsCgkJCQkiZXZlbnRmZCIsCgkJCQkiZXZlbnRmZDIiLAoJCQkJImV4ZWN2ZSIsCgkJCQkiZXhlY3ZlYXQiLAoJCQkJImV4aXQiLAoJCQkJImV4aXRfZ3JvdXAiLAoJCQkJImZhY2Nlc3NhdCIsCgkJCQkiZmFjY2Vzc2F0MiIsCgkJCQkiZmFkdmlzZTY0IiwKCQkJCSJmYWR2aXNlNjRfNjQiLAoJCQkJImZhbGxvY2F0ZSIsCgkJCQkiZmFub3RpZnlfbWFyayIsCgkJCQkiZmNoZGlyIiwKCQkJCSJmY2htb2QiLAoJCQkJImZjaG1vZGF0IiwKCQkJCSJmY2hvd24iLAoJCQkJImZjaG93bjMyIiwKCQkJCSJmY2hvd25hdCIsCgkJCQkiZmNudGwiLAoJCQkJImZjbnRsNjQiLAoJCQkJImZkYXRhc3luYyIsCgkJCQkiZmdldHhhdHRyIiwKCQkJCSJmbGlzdHhhdHRyIiwKCQkJCSJmbG9jayIsCgkJCQkiZm9yayIsCgkJCQkiZnJlbW92ZXhhdHRyIiwKCQkJCSJmc2V0eGF0dHIiLAoJCQkJImZzdGF0IiwKCQkJCSJmc3RhdDY0IiwKCQkJCSJmc3RhdGF0NjQiLAoJCQkJImZzdGF0ZnMiLAoJCQkJImZzdGF0ZnM2NCIsCgkJCQkiZnN5bmMiLAoJCQkJImZ0cnVuY2F0ZSIsCgkJCQkiZnRydW5jYXRlNjQiLAoJCQkJImZ1dGV4IiwKCQkJCSJmdXRleF90aW1lNjQiLAoJCQkJImZ1dGltZXNhdCIsCgkJCQkiZ2V0Y3B1IiwKCQkJCSJnZXRjd2QiLAoJCQkJImdldGRlbnRzIiwKCQkJCSJnZXRkZW50czY0IiwKCQkJCSJnZXRlZ2lkIiwKCQkJCSJnZXRlZ2lkMzIiLAoJCQkJImdldGV1aWQiLAoJCQkJImdldGV1aWQzMiIsCgkJCQkiZ2V0Z2lkIiwKCQkJCSJnZXRnaWQzMiIsCgkJCQkiZ2V0Z3JvdXBzIiwKCQkJCSJnZXRncm91cHMzMiIsCgkJCQkiZ2V0aXRpbWVyIiwKCQkJCSJnZXRwZWVybmFtZSIsCgkJCQkiZ2V0cGdpZCIsCgkJCQkiZ2V0cGdycCIsCgkJCQkiZ2V0cGlkIiwKCQkJCSJnZXRwcGlkIiwKCQkJCSJnZXRwcmlvcml0eSIsCgkJCQkiZ2V0cmFuZG9tIiwKCQkJCSJnZXRyZXNnaWQiLAoJCQkJImdldHJlc2dpZDMyIiwKCQkJCSJnZXRyZXN1aWQiLAoJCQkJImdldHJlc3VpZDMyIiwKCQkJCSJnZXRybGltaXQiLAoJCQkJImdldF9yb2J1c3RfbGlzdCIsCgkJCQkiZ2V0cnVzYWdlIiwKCQkJCSJnZXRzaWQiLAoJCQkJImdldHNvY2tuYW1lIiwKCQkJCSJnZXRzb2Nrb3B0IiwKCQkJCSJnZXRfdGhyZWFkX2FyZWEiLAoJCQkJImdldHRpZCIsCgkJCQkiZ2V0dGltZW9mZGF5IiwKCQkJCSJnZXR1aWQiLAoJCQkJImdldHVpZDMyIiwKCQkJCSJnZXR4YXR0ciIsCgkJCQkiaW5vdGlmeV9hZGRfd2F0Y2giLAoJCQkJImlub3RpZnlfaW5pdCIsCgkJCQkiaW5vdGlmeV9pbml0MSIsCgkJCQkiaW5vdGlmeV9ybV93YXRjaCIsCgkJCQkiaW9fY2FuY2VsIiwKCQkJCSJpb2N0bCIsCgkJCQkiaW9fZGVzdHJveSIsCgkJCQkiaW9fZ2V0ZXZlbnRzIiwKCQkJCSJpb19wZ2V0ZXZlbnRzIiwKCQkJCSJpb19wZ2V0ZXZlbnRzX3RpbWU2NCIsCgkJCQkiaW9wcmlvX2dldCIsCgkJCQkiaW9wcmlvX3NldCIsCgkJCQkiaW9fc2V0dXAiLAoJCQkJImlvX3N1Ym1pdCIsCgkJCQkiaW9fdXJpbmdfZW50ZXIiLAoJCQkJImlvX3VyaW5nX3JlZ2lzdGVyIiwKCQkJCSJpb191cmluZ19zZXR1cCIsCgkJCQkiaXBjIiwKCQkJCSJraWxsIiwKCQkJCSJsY2hvd24iLAoJCQkJImxjaG93bjMyIiwKCQkJCSJsZ2V0eGF0dHIiLAoJCQkJImxpbmsiLAoJCQkJImxpbmthdCIsCgkJCQkibGlzdGVuIiwKCQkJCSJsaXN0eGF0dHIiLAoJCQkJImxsaXN0eGF0dHIiLAoJCQkJIl9sbHNlZWsiLAoJCQkJImxyZW1vdmV4YXR0ciIsCgkJCQkibHNlZWsiLAoJCQkJImxzZXR4YXR0ciIsCgkJCQkibHN0YXQiLAoJCQkJImxzdGF0NjQiLAoJCQkJIm1hZHZpc2UiLAoJCQkJIm1lbWJhcnJpZXIiLAoJCQkJIm1lbWZkX2NyZWF0ZSIsCgkJCQkibWluY29yZSIsCgkJCQkibWtkaXIiLAoJCQkJIm1rZGlyYXQiLAoJCQkJIm1rbm9kIiwKCQkJCSJta25vZGF0IiwKCQkJCSJtbG9jayIsCgkJCQkibWxvY2syIiwKCQkJCSJtbG9ja2FsbCIsCgkJCQkibW1hcCIsCgkJCQkibW1hcDIiLAoJCQkJIm1wcm90ZWN0IiwKCQkJCSJtcV9nZXRzZXRhdHRyIiwKCQkJCSJtcV9ub3RpZnkiLAoJCQkJIm1xX29wZW4iLAoJCQkJIm1xX3RpbWVkcmVjZWl2ZSIsCgkJCQkibXFfdGltZWRyZWNlaXZlX3RpbWU2NCIsCgkJCQkibXFfdGltZWRzZW5kIiwKCQkJCSJtcV90aW1lZHNlbmRfdGltZTY0IiwKCQkJCSJtcV91bmxpbmsiLAoJCQkJIm1yZW1hcCIsCgkJCQkibXNnY3RsIiwKCQkJCSJtc2dnZXQiLAoJCQkJIm1zZ3JjdiIsCgkJCQkibXNnc25kIiwKCQkJCSJtc3luYyIsCgkJCQkibXVubG9jayIsCgkJCQkibXVubG9ja2FsbCIsCgkJCQkibXVubWFwIiwKCQkJCSJuYW5vc2xlZXAiLAoJCQkJIm5ld2ZzdGF0YXQiLAoJCQkJIl9uZXdzZWxlY3QiLAoJCQkJIm9wZW4iLAoJCQkJIm9wZW5hdCIsCgkJCQkib3BlbmF0MiIsCgkJCQkicGF1c2UiLAoJCQkJInBpZGZkX29wZW4iLAoJCQkJInBpZGZkX3NlbmRfc2lnbmFsIiwKCQkJCSJwaXBlIiwKCQkJCSJwaXBlMiIsCgkJCQkicG9sbCIsCgkJCQkicHBvbGwiLAoJCQkJInBwb2xsX3RpbWU2NCIsCgkJCQkicHJjdGwiLAoJCQkJInByZWFkNjQiLAoJCQkJInByZWFkdiIsCgkJCQkicHJlYWR2MiIsCgkJCQkicHJsaW1pdDY0IiwKCQkJCSJwc2VsZWN0NiIsCgkJCQkicHNlbGVjdDZfdGltZTY0IiwKCQkJCSJwd3JpdGU2NCIsCgkJCQkicHdyaXRldiIsCgkJCQkicHdyaXRldjIiLAoJCQkJInJlYWQiLAoJCQkJInJlYWRhaGVhZCIsCgkJCQkicmVhZGxpbmsiLAoJCQkJInJlYWRsaW5rYXQiLAoJCQkJInJlYWR2IiwKCQkJCSJyZWN2IiwKCQkJCSJyZWN2ZnJvbSIsCgkJCQkicmVjdm1tc2ciLAoJCQkJInJlY3ZtbXNnX3RpbWU2NCIsCgkJCQkicmVjdm1zZyIsCgkJCQkicmVtYXBfZmlsZV9wYWdlcyIsCgkJCQkicmVtb3ZleGF0dHIiLAoJCQkJInJlbmFtZSIsCgkJCQkicmVuYW1lYXQiLAoJCQkJInJlbmFtZWF0MiIsCgkJCQkicmVzdGFydF9zeXNjYWxsIiwKCQkJCSJybWRpciIsCgkJCQkicnNlcSIsCgkJCQkicnRfc2lnYWN0aW9uIiwKCQkJCSJydF9zaWdwZW5kaW5nIiwKCQkJCSJydF9zaWdwcm9jbWFzayIsCgkJCQkicnRfc2lncXVldWVpbmZvIiwKCQkJCSJydF9zaWdyZXR1cm4iLAoJCQkJInJ0X3NpZ3N1c3BlbmQiLAoJCQkJInJ0X3NpZ3RpbWVkd2FpdCIsCgkJCQkicnRfc2lndGltZWR3YWl0X3RpbWU2NCIsCgkJCQkicnRfdGdzaWdxdWV1ZWluZm8iLAoJCQkJInNjaGVkX2dldGFmZmluaXR5IiwKCQkJCSJzY2hlZF9nZXRhdHRyIiwKCQkJCSJzY2hlZF9nZXRwYXJhbSIsCgkJCQkic2NoZWRfZ2V0X3ByaW9yaXR5X21heCIsCgkJCQkic2NoZWRfZ2V0X3ByaW9yaXR5X21pbiIsCgkJCQkic2NoZWRfZ2V0c2NoZWR1bGVyIiwKCQkJCSJzY2hlZF9ycl9nZXRfaW50ZXJ2YWwiLAoJCQkJInNjaGVkX3JyX2dldF9pbnRlcnZhbF90aW1lNjQiLAoJCQkJInNjaGVkX3NldGFmZmluaXR5IiwKCQkJCSJzY2hlZF9zZXRhdHRyIiwKCQkJCSJzY2hlZF9zZXRwYXJhbSIsCgkJCQkic2NoZWRfc2V0c2NoZWR1bGVyIiwKCQkJCSJzY2hlZF95aWVsZCIsCgkJCQkic2VsZWN0IiwKCQkJCSJzZW1jdGwiLAoJCQkJInNlbWdldCIsCgkJCQkic2Vtb3AiLAoJCQkJInNlbXRpbWVkb3AiLAoJCQkJInNlbXRpbWVkb3BfdGltZTY0IiwKCQkJCSJzZW5kIiwKCQkJCSJzZW5kZmlsZSIsCgkJCQkic2VuZGZpbGU2NCIsCgkJCQkic2VuZG1tc2ciLAoJCQkJInNlbmRtc2ciLAoJCQkJInNlbmR0byIsCgkJCQkic2V0aXRpbWVyIiwKCQkJCSJzZXRwcmlvcml0eSIsCgkJCQkic2V0X3JvYnVzdF9saXN0IiwKCQkJCSJzZXRzaWQiLAoJCQkJInNldHNvY2tvcHQiLAoJCQkJInNldF90aHJlYWRfYXJlYSIsCgkJCQkic2V0X3RpZF9hZGRyZXNzIiwKCQkJCSJzZXR4YXR0ciIsCgkJCQkic2htYXQiLAoJCQkJInNobWN0bCIsCgkJCQkic2htZHQiLAoJCQkJInNobWdldCIsCgkJCQkic2h1dGRvd24iLAoJCQkJInNpZ2FsdHN0YWNrIiwKCQkJCSJzaWduYWxmZCIsCgkJCQkic2lnbmFsZmQ0IiwKCQkJCSJzaWdwcm9jbWFzayIsCgkJCQkic2lncmV0dXJuIiwKCQkJCSJzcGxpY2UiLAoJCQkJInN0YXQiLAoJCQkJInN0YXQ2NCIsCgkJCQkic3RhdGZzIiwKCQkJCSJzdGF0ZnM2NCIsCgkJCQkic3RhdHgiLAoJCQkJInN5bWxpbmsiLAoJCQkJInN5bWxpbmthdCIsCgkJCQkic3luYyIsCgkJCQkic3luY19maWxlX3JhbmdlIiwKCQkJCSJzeW5jZnMiLAoJCQkJInN5c2luZm8iLAoJCQkJInRlZSIsCgkJCQkidGdraWxsIiwKCQkJCSJ0aW1lIiwKCQkJCSJ0aW1lcl9jcmVhdGUiLAoJCQkJInRpbWVyX2RlbGV0ZSIsCgkJCQkidGltZXJfZ2V0b3ZlcnJ1biIsCgkJCQkidGltZXJfZ2V0dGltZSIsCgkJCQkidGltZXJfZ2V0dGltZTY0IiwKCQkJCSJ0aW1lcl9zZXR0aW1lIiwKCQkJCSJ0aW1lcl9zZXR0aW1lNjQiLAoJCQkJInRpbWVyZmRfY3JlYXRlIiwKCQkJCSJ0aW1lcmZkX2dldHRpbWUiLAoJCQkJInRpbWVyZmRfZ2V0dGltZTY0IiwKCQkJCSJ0aW1lcmZkX3NldHRpbWUiLAoJCQkJInRpbWVyZmRfc2V0dGltZTY0IiwKCQkJCSJ0aW1lcyIsCgkJCQkidGtpbGwiLAoJCQkJInRydW5jYXRlIiwKCQkJCSJ0cnVuY2F0ZTY0IiwKCQkJCSJ1Z2V0cmxpbWl0IiwKCQkJCSJ1bWFzayIsCgkJCQkidW5hbWUiLAoJCQkJInVubGluayIsCgkJCQkidW5saW5rYXQiLAoJCQkJInV0aW1lIiwKCQkJCSJ1dGltZW5zYXQiLAoJCQkJInV0aW1lbnNhdF90aW1lNjQiLAoJCQkJInV0aW1lcyIsCgkJCQkidmZvcmsiLAoJCQkJInZtc3BsaWNlIiwKCQkJCSJ3YWl0NCIsCgkJCQkid2FpdGlkIiwKCQkJCSJ3YWl0cGlkIiwKCQkJCSJ3cml0ZSIsCgkJCQkid3JpdGV2IgoJCQldLAoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIgoJCX0sCgkJewoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSwgMCIsCgkJCSJhcmdzIjogWwoJCQkJewoJCQkJCSJpbmRleCI6IDAsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDIKCQkJCX0sCgkJCQl7CgkJCQkJImluZGV4IjogMSwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogMQoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAwCgkJCQl9CgoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19OT05CTE9DSywgMCIsCgkJCSJhcmdzIjogWwoJCQkJewoJCQkJCSJpbmRleCI6IDAsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDIKCQkJCX0sCgkJCQl7CgkJCQkJImluZGV4IjogMSwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogMjA0OQoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAwCgkJCQl9CgoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19DTE9FWEVDLCAwIiwKCQkJImFyZ3MiOiBbCgkJCQl7CgkJCQkJImluZGV4IjogMCwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogMgoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAxLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiA1MjQyODkKCQkJCX0sCgkJCQl7CgkJCQkJImluZGV4IjogMiwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogMAoJCQkJfQoKCQkJXQoJCX0sCgkJewoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0sgfCBTT0NLX0NMT0VYRUMsIDAiLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAwLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAyCgkJCQl9LAoJCQkJewoJCQkJCSJpbmRleCI6IDEsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDUyNjMzNwoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAwCgkJCQl9CgoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNLCBJUFBST1RPX1RDUCIsCgkJCSJhcmdzIjogWwoJCQkJewoJCQkJCSJpbmRleCI6IDAsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDIKCQkJCX0sCgkJCQl7CgkJCQkJImluZGV4IjogMSwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogMQoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiA2CgkJCQl9CgoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19OT05CTE9DSywgSVBQUk9UT19UQ1AiLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAwLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAyCgkJCQl9LAoJCQkJewoJCQkJCSJpbmRleCI6IDEsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDIwNDkKCQkJCX0sCgkJCQl7CgkJCQkJImluZGV4IjogMiwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogNgoJCQkJfQoKCQkJXQoJCX0sCgkJewoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfQ0xPRVhFQywgSVBQUk9UT19UQ1AiLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAwLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAyCgkJCQl9LAoJCQkJewoJCQkJCSJpbmRleCI6IDEsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDUyNDI4OQoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiA2CgkJCQl9CgoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19OT05CTE9DSyB8IFNPQ0tfQ0xPRVhFQywgSVBQUk9UT19UQ1AiLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAwLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAyCgkJCQl9LAoJCQkJewoJCQkJCSJpbmRleCI6IDEsCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsCgkJCQkJInZhbHVlIiA6IDUyNjMzNwoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiA2CgkJCQl9CgoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsgInNvY2tldHBhaXIiIF0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiY29tbWVudCI6ICJBRl9VTklYLCAqLCAwIiwKCQkJImFyZ3MiOiBbCgkJCQl7CgkJCQkJImluZGV4IjogMCwKCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwKCQkJCQkidmFsdWUiIDogMQoJCQkJfSwKCQkJCXsKCQkJCQkiaW5kZXgiOiAyLAoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLAoJCQkJCSJ2YWx1ZSIgOiAwCgkJCQl9CgkJCV0KCQl9LAoJCXsKCQkJIm5hbWVzIjogWwoJCQkJInByb2Nlc3Nfdm1fcmVhZHYiLAoJCQkJInByb2Nlc3Nfdm1fd3JpdGV2IiwKCQkJCSJwdHJhY2UiCgkJCV0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiaW5jbHVkZXMiOiB7CgkJCQkibWluS2VybmVsIjogIjQuOCIKCQkJfQoJCX0sCgkJewoJCQkibmFtZXMiOiBbCgkJCQkicGVyc29uYWxpdHkiCgkJCV0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAwLAoJCQkJCSJ2YWx1ZSI6IDAsCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIgoJCQkJfQoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsKCQkJCSJwZXJzb25hbGl0eSIKCQkJXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJhcmdzIjogWwoJCQkJewoJCQkJCSJpbmRleCI6IDAsCgkJCQkJInZhbHVlIjogOCwKCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiCgkJCQl9CgkJCV0KCQl9LAoJCXsKCQkJIm5hbWVzIjogWwoJCQkJInBlcnNvbmFsaXR5IgoJCQldLAoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwKCQkJImFyZ3MiOiBbCgkJCQl7CgkJCQkJImluZGV4IjogMCwKCQkJCQkidmFsdWUiOiAxMzEwNzIsCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIgoJCQkJfQoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsKCQkJCSJwZXJzb25hbGl0eSIKCQkJXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJhcmdzIjogWwoJCQkJewoJCQkJCSJpbmRleCI6IDAsCgkJCQkJInZhbHVlIjogMTMxMDgwLAoJCQkJCSJvcCI6ICJTQ01QX0NNUF9FUSIKCQkJCX0KCQkJXQoJCX0sCgkJewoJCQkibmFtZXMiOiBbCgkJCQkicGVyc29uYWxpdHkiCgkJCV0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAwLAoJCQkJCSJ2YWx1ZSI6IDQyOTQ5NjcyOTUsCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIgoJCQkJfQoJCQldCgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsKCQkJCSJzeW5jX2ZpbGVfcmFuZ2UyIgoJCQldLAoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwKCQkJImluY2x1ZGVzIjogewoJCQkJImFyY2hlcyI6IFsKCQkJCQkicHBjNjRsZSIKCQkJCV0KCQkJfQoJCX0sCgkJewoJCQkibmFtZXMiOiBbCgkJCQkiYXJtX2ZhZHZpc2U2NF82NCIsCgkJCQkiYXJtX3N5bmNfZmlsZV9yYW5nZSIsCgkJCQkic3luY19maWxlX3JhbmdlMiIsCgkJCQkiYnJlYWtwb2ludCIsCgkJCQkiY2FjaGVmbHVzaCIsCgkJCQkic2V0X3RscyIKCQkJXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsCgkJCSJpbmNsdWRlcyI6IHsKCQkJCSJhcmNoZXMiOiBbCgkJCQkJImFybSIsCgkJCQkJImFybTY0IgoJCQkJXQoJCQl9CgkJfSwKCQl7CgkJCSJuYW1lcyI6IFsKCQkJCSJhcmNoX3ByY3RsIgoJCQldLAoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwKCQkJImluY2x1ZGVzIjogewoJCQkJImFyY2hlcyI6IFsKCQkJCQkiYW1kNjQiLAoJCQkJCSJ4MzIiCgkJCQldCgkJCX0KCQl9LAoJCXsKCQkJIm5hbWVzIjogWwoJCQkJIm1vZGlmeV9sZHQiCgkJCV0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiaW5jbHVkZXMiOiB7CgkJCQkiYXJjaGVzIjogWwoJCQkJCSJhbWQ2NCIsCgkJCQkJIngzMiIsCgkJCQkJIng4NiIKCQkJCV0KCQkJfQoJCX0sCgkJewoJCQkibmFtZXMiOiBbCgkJCQkiczM5MF9wY2lfbW1pb19yZWFkIiwKCQkJCSJzMzkwX3BjaV9tbWlvX3dyaXRlIiwKCQkJCSJzMzkwX3J1bnRpbWVfaW5zdHIiCgkJCV0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiaW5jbHVkZXMiOiB7CgkJCQkiYXJjaGVzIjogWwoJCQkJCSJzMzkwIiwKCQkJCQkiczM5MHgiCgkJCQldCgkJCX0KCQl9LAoJCXsKCQkJIm5hbWVzIjogWwoJCQkJImNsb25lIgoJCQldLAoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwKCQkJImFyZ3MiOiBbCgkJCQl7CgkJCQkJImluZGV4IjogMCwKCQkJCQkidmFsdWUiOiAyMTE0MDYwMjg4LAoJCQkJCSJvcCI6ICJTQ01QX0NNUF9NQVNLRURfRVEiCgkJCQl9CgkJCV0sCgkJCSJleGNsdWRlcyI6IHsKCQkJCSJjYXBzIjogWwoJCQkJCSJDQVBfU1lTX0FETUlOIgoJCQkJXSwKCQkJCSJhcmNoZXMiOiBbCgkJCQkJInMzOTAiLAoJCQkJCSJzMzkweCIKCQkJCV0KCQkJfQoJCX0sCgkJewoJCQkibmFtZXMiOiBbCgkJCQkiY2xvbmUiCgkJCV0sCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLAoJCQkiYXJncyI6IFsKCQkJCXsKCQkJCQkiaW5kZXgiOiAxLAoJCQkJCSJ2YWx1ZSI6IDIxMTQwNjAyODgsCgkJCQkJIm9wIjogIlNDTVBfQ01QX01BU0tFRF9FUSIKCQkJCX0KCQkJXSwKCQkJImNvbW1lbnQiOiAiczM5MCBwYXJhbWV0ZXIgb3JkZXJpbmcgZm9yIGNsb25lIGlzIGRpZmZlcmVudCIsCgkJCSJpbmNsdWRlcyI6IHsKCQkJCSJhcmNoZXMiOiBbCgkJCQkJInMzOTAiLAoJCQkJCSJzMzkweCIKCQkJCV0KCQkJfSwKCQkJImV4Y2x1ZGVzIjogewoJCQkJImNhcHMiOiBbCgkJCQkJIkNBUF9TWVNfQURNSU4iCgkJCQldCgkJCX0KCQl9LAoJCXsKCQkJIm5hbWVzIjogWwoJCQkJImNsb25lMyIKCQkJXSwKCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9FUlJOTyIsCgkJCSJlcnJub1JldCI6IDM4LAoJCQkiZXhjbHVkZXMiOiB7CgkJCQkiY2FwcyI6IFsKCQkJCQkiQ0FQX1NZU19BRE1JTiIKCQkJCV0KCQkJfQoJCX0KCV0KfQo="
        cls.aci_arm_policy = load_policy_from_arm_template_str(cls.custom_arm_json, "")[
            0
        ]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

        cls.aci_arm_policy2 = load_policy_from_arm_template_str(cls.custom_arm_json2.replace("seccompStr", seccomp_profile_contents), "")[
            0
        ]
        cls.aci_arm_policy2.populate_policy_content_for_all_images()

        cls.aci_arm_policy3 = load_policy_from_arm_template_str(cls.custom_arm_json3, "")[
            0
        ]
        cls.aci_arm_policy3.populate_policy_content_for_all_images()

        cls.aci_arm_policy4 = load_policy_from_arm_template_str(cls.custom_arm_json4, "")[
            0
        ]
        cls.aci_arm_policy4.populate_policy_content_for_all_images()

    def test_arm_template_security_context_defaults(self):
        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "",
                "strategy": "any"
            },
            "group_idnames": [
                {
                    "pattern": "",
                    "strategy": "any"
                }
            ],
            "umask": "0022"
        }""")

        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertFalse(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_NO_NEW_PRIVILEGES])
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})
        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256], "")
        # check all the default unprivileged capabilities are present
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_UNPRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_BOUNDING], ignore_order=True), {})
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_UNPRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_EFFECTIVE], ignore_order=True), {})
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_UNPRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_PERMITTED], ignore_order=True), {})
        self.assertEqual([], regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_AMBIENT])
        self.assertEqual([], regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_INHERITABLE])
        # check default pause container
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_CONTAINERS[0], regular_image_json[1], ignore_order=True), {})

    def test_arm_template_security_context_allow_privilege_escalation(self):
        regular_image_json = json.loads(
            self.aci_arm_policy3.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        # value of NO_NEW_PRIVILEGES should be the opposite of allowPrivilegeEscalation
        self.assertFalse(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_NO_NEW_PRIVILEGES])

    def test_arm_template_security_context_user(self):
        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "456",
                "strategy": "id"
            },
            "group_idnames": [
                {
                    "pattern": "123",
                    "strategy": "id"
                }
            ],
            "umask": "0022"
        }""")

        regular_image_json = json.loads(
            self.aci_arm_policy2.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

    def test_arm_template_security_context_seccomp_profile(self):
        expected_seccomp_profile_sha256 = "aeb9bbbd14679be3aab28c35960e2a398e4ce838a066ce2dd5645c4b8da8de21"

        regular_image_json = json.loads(
            self.aci_arm_policy2.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256], expected_seccomp_profile_sha256)

    def test_arm_template_capabilities_unprivileged(self):
        attempted_new_capabilities = ["CAP_SYS_TIME", "CAP_DAC_READ_SEARCH"]
        attempted_removed_capabilities = ["CAP_CHOWN", "CAP_KILL"]
        regular_image_json = json.loads(
            self.aci_arm_policy4.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )
        # ambient & inheritable should still be empty
        self.assertEqual([], regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_AMBIENT])
        self.assertEqual([], regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_INHERITABLE])
        for cap in attempted_new_capabilities:
            self.assertIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_BOUNDING])
            self.assertIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_EFFECTIVE])
            self.assertNotIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_INHERITABLE])
            self.assertIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_PERMITTED])
        for cap in attempted_removed_capabilities:
            self.assertNotIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_BOUNDING])
            self.assertNotIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_EFFECTIVE])
            self.assertNotIn(cap, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_PERMITTED])

    def test_arm_template_capabilities_privileged(self):
        regular_image_json = json.loads(
            self.aci_arm_policy3.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        # check all the default unprivileged capabilities are present
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_PRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_BOUNDING], ignore_order=True), {})
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_PRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_EFFECTIVE], ignore_order=True), {})
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_PRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_PERMITTED], ignore_order=True), {})
        self.assertEqual([], regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_AMBIENT])
        self.assertEqual(deepdiff.DeepDiff(config.DEFAULT_PRIVILEGED_CAPABILITIES, regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES][config.POLICY_FIELD_CONTAINERS_ELEMENTS_CAPABILITIES_INHERITABLE], ignore_order=True), {})


class PolicyGeneratingSecurityContextUserEdgeCases(unittest.TestCase):
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext":{
                        "privileged":"true",
                        "allowPrivilegeEscalation":"true",
                        "capabilities":{
                            "add":["ADDCAP1","ADDCAP2"],
                            "drop":["DROPCAP1","DROPCAP2"]
                        },
                        "runAsUser":456
                    },
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext":{
                        "privileged":"true",
                        "allowPrivilegeEscalation":"true",
                        "capabilities":{
                            "add":["ADDCAP1","ADDCAP2"],
                            "drop":["DROPCAP1","DROPCAP2"]
                        },
                        "runAsGroup":123
                    },
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

    custom_arm_json3 = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "temp_image"
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext":{
                        "privileged":"true",
                        "allowPrivilegeEscalation":"true",
                        "capabilities":{
                            "add":["ADDCAP1","ADDCAP2"],
                            "drop":["DROPCAP1","DROPCAP2"]
                        }
                    },
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

    @classmethod
    def setUpClass(cls):
        cls.aci_arm_policy = load_policy_from_arm_template_str(cls.custom_arm_json, "")[
            0
        ]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

        cls.aci_arm_policy2 = load_policy_from_arm_template_str(cls.custom_arm_json2, "")[
            0
        ]
        cls.aci_arm_policy2.populate_policy_content_for_all_images()

        # create docker file to build and test on
        cls.path = os.path.dirname(__file__)
        cls.dockerfile_path = os.path.join(cls.path, "./Dockerfile")
        cls.dockerfile_path2 = os.path.join(cls.path, "./Dockerfile2.dockerfile")
        cls.dockerfile_path3 = os.path.join(cls.path, "./Dockerfile3.dockerfile")
        cls.dockerfile_path4 = os.path.join(cls.path, "./Dockerfile4.dockerfile")
        cls.dockerfile_path5 = os.path.join(cls.path, "./Dockerfile5.dockerfile")
        cls.dockerfile_path6 = os.path.join(cls.path, "./Dockerfile6.dockerfile")

        cls.client = docker.from_env()

    @classmethod
    def tearDownClass(cls):
        cls.client.containers.prune()
        cls.client.close()

    def test_arm_template_security_context_no_run_as_group(self):
        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "456",
                "strategy": "id"
            },
            "group_idnames": [
                {
                    "pattern": "",
                    "strategy": "any"
                }
            ],
            "umask": "0022"
        }""")

        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

    def test_arm_template_security_context_no_run_as_user(self):
        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "",
                "strategy": "any"
            },
            "group_idnames": [
                {
                    "pattern": "123",
                    "strategy": "id"
                }
            ],
            "umask": "0022"
        }""")

        regular_image_json = json.loads(
            self.aci_arm_policy2.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

    def test_arm_template_security_context_uid_gid(self):
        dockerfile_contents = ["FROM ubuntu\n", "USER 456:123\n"]

        try:
            with open(self.dockerfile_path, "w") as dockerfile:
                dockerfile.writelines(dockerfile_contents)

            # build docker image
            image = self.client.images.build(nocache=True, tag="temp_image", fileobj=open(self.dockerfile_path, "rb"))
        finally:
            if os.path.exists(self.dockerfile_path):
                os.remove(self.dockerfile_path)

        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json3, "")[0]
        aci_arm_policy.populate_policy_content_for_all_images()
        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "456",
                "strategy": "id"
            },
            "group_idnames": [
                {
                    "pattern": "123",
                    "strategy": "id"
                }
            ],
            "umask": "0022"
        }""")
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

        self.client.images.remove(image[0].attrs.get("Id"))

    def test_arm_template_security_context_user_gid(self):
        dockerfile_contents = ["FROM ubuntu\n", "USER test_user:123\n"]

        try:
            with open(self.dockerfile_path2, "w") as dockerfile:
                dockerfile.writelines(dockerfile_contents)

            # build docker image
            image = self.client.images.build(nocache=True, tag="temp_image2", fileobj=open(self.dockerfile_path2, "rb"))
        finally:
            if os.path.exists(self.dockerfile_path2):
                os.remove(self.dockerfile_path2)

        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json3.replace("temp_image", "temp_image2"), "")[0]
        aci_arm_policy.populate_policy_content_for_all_images()
        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "test_user",
                "strategy": "name"
            },
            "group_idnames": [
                {
                    "pattern": "123",
                    "strategy": "id"
                }
            ],
            "umask": "0022"
        }""")
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

        self.client.images.remove(image[0].attrs.get("Id"))

    def test_arm_template_security_context_user_group(self):
        dockerfile_contents = ["FROM ubuntu\n", "USER test_user:test_group\n"]
        try:
            with open(self.dockerfile_path3, "w") as dockerfile:
                dockerfile.writelines(dockerfile_contents)

            # build docker image
            image = self.client.images.build(nocache=True, tag="temp_image3", fileobj=open(self.dockerfile_path3, "rb"))
        finally:
            if os.path.exists(self.dockerfile_path3):
                os.remove(self.dockerfile_path3)

        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json3.replace("temp_image", "temp_image3"), "")[0]
        aci_arm_policy.populate_policy_content_for_all_images()
        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "test_user",
                "strategy": "name"
            },
            "group_idnames": [
                {
                    "pattern": "test_group",
                    "strategy": "name"
                }
            ],
            "umask": "0022"
        }""")
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

        self.client.images.remove(image[0].attrs.get("Id"))

    def test_arm_template_security_context_uid_group(self):
        # valid values are "user", "uid",
        dockerfile_contents = ["FROM ubuntu\n", "USER 456:test_group\n"]
        try:
            with open(self.dockerfile_path4, "w") as dockerfile:
                dockerfile.writelines(dockerfile_contents)

            # build docker image
            image = self.client.images.build(nocache=True, tag="temp_image4", fileobj=open(self.dockerfile_path4, "rb"))
        finally:
            if os.path.exists(self.dockerfile_path4):
                os.remove(self.dockerfile_path4)

        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json3.replace("temp_image", "temp_image4"), "")[0]
        aci_arm_policy.populate_policy_content_for_all_images()
        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "456",
                "strategy": "id"
            },
            "group_idnames": [
                {
                    "pattern": "test_group",
                    "strategy": "name"
                }
            ],
            "umask": "0022"
        }""")

        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

        self.client.images.remove(image[0].attrs.get("Id"))

    def test_arm_template_security_context_uid(self):
        dockerfile_contents = ["FROM ubuntu\n", "USER 456\n"]
        try:
            with open(self.dockerfile_path5, "w") as dockerfile:
                dockerfile.writelines(dockerfile_contents)

            # build docker image
            image = self.client.images.build(nocache=True, tag="temp_image5", fileobj=open(self.dockerfile_path5, "rb"))
        finally:
            if os.path.exists(self.dockerfile_path5):
                os.remove(self.dockerfile_path5)

        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json3.replace("temp_image", "temp_image5"), "")[0]
        aci_arm_policy.populate_policy_content_for_all_images()
        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "456",
                "strategy": "id"
            },
            "group_idnames": [
                {
                    "pattern": "",
                    "strategy": "any"
                }
            ],
            "umask": "0022"
        }""")
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

        self.client.images.remove(image[0].attrs.get("Id"))

    def test_arm_template_security_context_user_dockerfile(self):
        dockerfile_contents = ["FROM ubuntu\n", "USER test_user\n"]
        try:
            with open(self.dockerfile_path6, "w") as dockerfile:
                dockerfile.writelines(dockerfile_contents)

            # build docker image
            image = self.client.images.build(nocache=True, tag="temp_image6", fileobj=open(self.dockerfile_path6, "rb"))
        finally:
            if os.path.exists(self.dockerfile_path6):
                os.remove(self.dockerfile_path6)

        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json3.replace("temp_image", "temp_image6"), "")[0]
        aci_arm_policy.populate_policy_content_for_all_images()
        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        expected_user_json = json.loads("""{
            "user_idname":
            {
                "pattern": "test_user",
                "strategy": "name"
            },
            "group_idnames": [
                {
                    "pattern": "",
                    "strategy": "any"
                }
            ],
            "umask": "0022"
        }""")
        self.assertEqual(deepdiff.DeepDiff(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_USER], expected_user_json, ignore_order=True), {})

        self.client.images.remove(image[0].attrs.get("Id"))


class PolicyGeneratingSecurityContextSeccompProfileEdgeCases(unittest.TestCase):
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
            "apiVersion": "2023-05-01",
            "location": "[parameters('location')]",
            "properties": {
                "containers": [
                {
                    "name": "[parameters('containername')]",

                    "properties": {
                    "image": "[variables('image')]",
                    "securityContext": {
                        "privileged": "false",
                        "capabilities":{
                            "add": ["CAP_SYS_TIME","CAP_DAC_READ_SEARCH"],
                            "drop": ["CAP_CHOWN","CAP_KILL"]
                        },
                        "runAsGroup": 123,
                        "runAsUser": 456,
                        "seccompProfile": "seccompStr"
                    },
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

    def test_arm_template_security_context_seccomp_profile_all_fields(self):
        seccomp_profile_contents = "ew0KCSJjb21tZW50IjogIkRlZmF1bHQgbW9ieSBzZWNjb21wIHBvbGljeSBjb25maWcgZmlsZSBhdDogaHR0cHM6Ly9naXRodWIuY29tL21vYnkvbW9ieS9ibG9iL21hc3Rlci9wcm9maWxlcy9zZWNjb21wL2RlZmF1bHQuanNvbiIsDQoJImRlZmF1bHRBY3Rpb24iOiAiU0NNUF9BQ1RfRVJSTk8iLA0KCSJkZWZhdWx0RXJybm9SZXQiOiAxLA0KCSJhcmNoaXRlY3R1cmVzIjogWyAiU0NNUF9BUkNIX1g4NiIsICJTQ01QX0FSQ0hfUFBDIl0sDQoJImZsYWdzIjogWyAiZmxhZzEiLCAiZmxhZzIiLCAiZmxhZzMiIF0sDQoJImxpc3RlbmVyUGF0aCI6ICIvbGlzdGVuZXIvUGF0aCIsDQoJImxpc3RlbmVyTWV0YWRhdGEiOiAibWV0YWRhdGEiLA0KCSJzeXNjYWxscyI6IFsNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSwgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDENCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMiwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAwDQoJCQkJfQ0KDQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfSU5FVCwgU09DS19TVFJFQU0gfCBTT0NLX05PTkJMT0NLLCAwIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMjA0OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfQ0xPRVhFQywgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDUyNDI4OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0sgfCBTT0NLX0NMT0VYRUMsIDAiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiA1MjYzMzcNCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMiwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAwDQoJCQkJfQ0KDQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfSU5FVCwgU09DS19TVFJFQU0sIElQUFJPVE9fVENQIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0ssIElQUFJPVE9fVENQIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMjA0OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfQ0xPRVhFQywgSVBQUk9UT19UQ1AiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiA1MjQyODkNCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMiwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiA2DQoJCQkJfQ0KDQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfSU5FVCwgU09DS19TVFJFQU0gfCBTT0NLX05PTkJMT0NLIHwgU09DS19DTE9FWEVDLCBJUFBST1RPX1RDUCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDUyNjMzNw0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0cGFpciIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfVU5JWCwgKiwgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicHJvY2Vzc192bV9yZWFkdiIsDQoJCQkJInByb2Nlc3Nfdm1fd3JpdGV2IiwNCgkJCQkicHRyYWNlIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJtaW5LZXJuZWwiOiAiNC44Ig0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiAwLA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiDQoJCQkJfQ0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiA4LA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiDQoJCQkJfQ0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiAxMzEwNzIsDQoJCQkJCSJvcCI6ICJTQ01QX0NNUF9FUSINCgkJCQl9DQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicGVyc29uYWxpdHkiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJ2YWx1ZSI6IDEzMTA4MCwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIg0KCQkJCX0NCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJwZXJzb25hbGl0eSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJInZhbHVlIjogNDI5NDk2NzI5NSwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIg0KCQkJCX0NCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJzeW5jX2ZpbGVfcmFuZ2UyIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJwcGM2NGxlIg0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJhcm1fZmFkdmlzZTY0XzY0IiwNCgkJCQkiYXJtX3N5bmNfZmlsZV9yYW5nZSIsDQoJCQkJInN5bmNfZmlsZV9yYW5nZTIiLA0KCQkJCSJicmVha3BvaW50IiwNCgkJCQkiY2FjaGVmbHVzaCIsDQoJCQkJInNldF90bHMiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJImFybSIsDQoJCQkJCSJhcm02NCINCgkJCQldDQoJCQl9DQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkiYXJjaF9wcmN0bCINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJpbmNsdWRlcyI6IHsNCgkJCQkiYXJjaGVzIjogWw0KCQkJCQkiYW1kNjQiLA0KCQkJCQkieDMyIg0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJtb2RpZnlfbGR0Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJhbWQ2NCIsDQoJCQkJCSJ4MzIiLA0KCQkJCQkieDg2Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJzMzkwX3BjaV9tbWlvX3JlYWQiLA0KCQkJCSJzMzkwX3BjaV9tbWlvX3dyaXRlIiwNCgkJCQkiczM5MF9ydW50aW1lX2luc3RyIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJzMzkwIiwNCgkJCQkJInMzOTB4Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJjbG9uZSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJInZhbHVlIjogMjExNDA2MDI4OCwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX01BU0tFRF9FUSINCgkJCQl9DQoJCQldLA0KCQkJImV4Y2x1ZGVzIjogew0KCQkJCSJjYXBzIjogWw0KCQkJCQkiQ0FQX1NZU19BRE1JTiINCgkJCQldLA0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJzMzkwIiwNCgkJCQkJInMzOTB4Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJjbG9uZSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJInZhbHVlIjogMjExNDA2MDI4OCwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX01BU0tFRF9FUSINCgkJCQl9DQoJCQldLA0KCQkJImNvbW1lbnQiOiAiczM5MCBwYXJhbWV0ZXIgb3JkZXJpbmcgZm9yIGNsb25lIGlzIGRpZmZlcmVudCIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJInMzOTAiLA0KCQkJCQkiczM5MHgiDQoJCQkJXQ0KCQkJfSwNCgkJCSJleGNsdWRlcyI6IHsNCgkJCQkiY2FwcyI6IFsNCgkJCQkJIkNBUF9TWVNfQURNSU4iDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJImNsb25lMyINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0VSUk5PIiwNCgkJCSJlcnJub1JldCI6IDM4LA0KCQkJImV4Y2x1ZGVzIjogew0KCQkJCSJjYXBzIjogWw0KCQkJCQkiQ0FQX1NZU19BRE1JTiINCgkJCQldDQoJCQl9DQoJCX0NCgldDQp9"
        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json.replace("seccompStr", seccomp_profile_contents), "")[
            0
        ]
        aci_arm_policy.populate_policy_content_for_all_images()
        expected_seccomp_profile_sha256 = "fb38009a098475bf3423b00f4f7c30f52a66d455f1ef1dcbe1708ad00f26a8cc"

        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256], expected_seccomp_profile_sha256)

    def test_arm_template_security_context_seccomp_profile_missing_default_action(self):
        seccomp_profile_contents = "ew0KCSJjb21tZW50IjogIkRlZmF1bHQgbW9ieSBzZWNjb21wIHBvbGljeSBjb25maWcgZmlsZSBhdDogaHR0cHM6Ly9naXRodWIuY29tL21vYnkvbW9ieS9ibG9iL21hc3Rlci9wcm9maWxlcy9zZWNjb21wL2RlZmF1bHQuanNvbiIsDQoJImRlZmF1bHRFcnJub1JldCI6IDEsDQoJInN5c2NhbGxzIjogWw0KCQl7DQoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNLCAwIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0ssIDAiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyMDQ5DQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDIsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMA0KCQkJCX0NCg0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19DTE9FWEVDLCAwIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogNTI0Mjg5DQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDIsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMA0KCQkJCX0NCg0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19OT05CTE9DSyB8IFNPQ0tfQ0xPRVhFQywgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDUyNjMzNw0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSwgSVBQUk9UT19UQ1AiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAxDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDIsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogNg0KCQkJCX0NCg0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19OT05CTE9DSywgSVBQUk9UT19UQ1AiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyMDQ5DQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDIsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogNg0KCQkJCX0NCg0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbICJzb2NrZXQiIF0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJjb21tZW50IjogIkFGX0lORVQsIFNPQ0tfU1RSRUFNIHwgU09DS19DTE9FWEVDLCBJUFBST1RPX1RDUCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDUyNDI4OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0sgfCBTT0NLX0NMT0VYRUMsIElQUFJPVE9fVENQIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogNTI2MzM3DQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDIsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogNg0KCQkJCX0NCg0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbICJzb2NrZXRwYWlyIiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9VTklYLCAqLCAwIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAxDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDIsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMA0KCQkJCX0NCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJwcm9jZXNzX3ZtX3JlYWR2IiwNCgkJCQkicHJvY2Vzc192bV93cml0ZXYiLA0KCQkJCSJwdHJhY2UiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJIm1pbktlcm5lbCI6ICI0LjgiDQoJCQl9DQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicGVyc29uYWxpdHkiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJ2YWx1ZSI6IDAsDQoJCQkJCSJvcCI6ICJTQ01QX0NNUF9FUSINCgkJCQl9DQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicGVyc29uYWxpdHkiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJ2YWx1ZSI6IDgsDQoJCQkJCSJvcCI6ICJTQ01QX0NNUF9FUSINCgkJCQl9DQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicGVyc29uYWxpdHkiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJ2YWx1ZSI6IDEzMTA3MiwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIg0KCQkJCX0NCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJwZXJzb25hbGl0eSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJInZhbHVlIjogMTMxMDgwLA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiDQoJCQkJfQ0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiA0Mjk0OTY3Mjk1LA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiDQoJCQkJfQ0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInN5bmNfZmlsZV9yYW5nZTIiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJInBwYzY0bGUiDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJImFybV9mYWR2aXNlNjRfNjQiLA0KCQkJCSJhcm1fc3luY19maWxlX3JhbmdlIiwNCgkJCQkic3luY19maWxlX3JhbmdlMiIsDQoJCQkJImJyZWFrcG9pbnQiLA0KCQkJCSJjYWNoZWZsdXNoIiwNCgkJCQkic2V0X3RscyINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJpbmNsdWRlcyI6IHsNCgkJCQkiYXJjaGVzIjogWw0KCQkJCQkiYXJtIiwNCgkJCQkJImFybTY0Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJhcmNoX3ByY3RsIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJhbWQ2NCIsDQoJCQkJCSJ4MzIiDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJIm1vZGlmeV9sZHQiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJImFtZDY0IiwNCgkJCQkJIngzMiIsDQoJCQkJCSJ4ODYiDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInMzOTBfcGNpX21taW9fcmVhZCIsDQoJCQkJInMzOTBfcGNpX21taW9fd3JpdGUiLA0KCQkJCSJzMzkwX3J1bnRpbWVfaW5zdHIiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJInMzOTAiLA0KCQkJCQkiczM5MHgiDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJImNsb25lIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiAyMTE0MDYwMjg4LA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfTUFTS0VEX0VRIg0KCQkJCX0NCgkJCV0sDQoJCQkiZXhjbHVkZXMiOiB7DQoJCQkJImNhcHMiOiBbDQoJCQkJCSJDQVBfU1lTX0FETUlOIg0KCQkJCV0sDQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJInMzOTAiLA0KCQkJCQkiczM5MHgiDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJImNsb25lIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkidmFsdWUiOiAyMTE0MDYwMjg4LA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfTUFTS0VEX0VRIg0KCQkJCX0NCgkJCV0sDQoJCQkiY29tbWVudCI6ICJzMzkwIHBhcmFtZXRlciBvcmRlcmluZyBmb3IgY2xvbmUgaXMgZGlmZmVyZW50IiwNCgkJCSJpbmNsdWRlcyI6IHsNCgkJCQkiYXJjaGVzIjogWw0KCQkJCQkiczM5MCIsDQoJCQkJCSJzMzkweCINCgkJCQldDQoJCQl9LA0KCQkJImV4Y2x1ZGVzIjogew0KCQkJCSJjYXBzIjogWw0KCQkJCQkiQ0FQX1NZU19BRE1JTiINCgkJCQldDQoJCQl9DQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkiY2xvbmUzIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfRVJSTk8iLA0KCQkJImVycm5vUmV0IjogMzgsDQoJCQkiZXhjbHVkZXMiOiB7DQoJCQkJImNhcHMiOiBbDQoJCQkJCSJDQVBfU1lTX0FETUlOIg0KCQkJCV0NCgkJCX0NCgkJfQ0KCV0NCn0="
        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json.replace("seccompStr", seccomp_profile_contents), "")[
            0
        ]
        aci_arm_policy.populate_policy_content_for_all_images()
        expected_seccomp_profile_sha256 = "fa881ac8600f3b835f7f3b5cb8fb49a5eeab2a3eb335134587dd0e30eb69d353"

        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256], expected_seccomp_profile_sha256)

    def test_arm_template_security_context_seccomp_profile_missing_default_errno(self):
        seccomp_profile_contents = "ew0KCSJjb21tZW50IjogIkRlZmF1bHQgbW9ieSBzZWNjb21wIHBvbGljeSBjb25maWcgZmlsZSBhdDogaHR0cHM6Ly9naXRodWIuY29tL21vYnkvbW9ieS9ibG9iL21hc3Rlci9wcm9maWxlcy9zZWNjb21wL2RlZmF1bHQuanNvbiIsDQoJImRlZmF1bHRBY3Rpb24iOiAiU0NNUF9BQ1RfRVJSTk8iLA0KCSJzeXNjYWxscyI6IFsNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSwgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDENCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMiwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAwDQoJCQkJfQ0KDQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfSU5FVCwgU09DS19TVFJFQU0gfCBTT0NLX05PTkJMT0NLLCAwIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMjA0OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfQ0xPRVhFQywgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDUyNDI4OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0sgfCBTT0NLX0NMT0VYRUMsIDAiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiA1MjYzMzcNCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMiwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAwDQoJCQkJfQ0KDQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfSU5FVCwgU09DS19TVFJFQU0sIElQUFJPVE9fVENQIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfTk9OQkxPQ0ssIElQUFJPVE9fVENQIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiAyDQoJCQkJfSwNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDEsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMjA0OQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0IiBdLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiY29tbWVudCI6ICJBRl9JTkVULCBTT0NLX1NUUkVBTSB8IFNPQ0tfQ0xPRVhFQywgSVBQUk9UT19UQ1AiLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDINCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiA1MjQyODkNCgkJCQl9LA0KCQkJCXsNCgkJCQkJImluZGV4IjogMiwNCgkJCQkJIm9wIiA6ICJTQ01QX0NNUF9FUSIsDQoJCQkJCSJ2YWx1ZSIgOiA2DQoJCQkJfQ0KDQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsgInNvY2tldCIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfSU5FVCwgU09DS19TVFJFQU0gfCBTT0NLX05PTkJMT0NLIHwgU09DS19DTE9FWEVDLCBJUFBST1RPX1RDUCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMg0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAxLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDUyNjMzNw0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDYNCgkJCQl9DQoNCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWyAic29ja2V0cGFpciIgXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImNvbW1lbnQiOiAiQUZfVU5JWCwgKiwgMCIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJvcCIgOiAiU0NNUF9DTVBfRVEiLA0KCQkJCQkidmFsdWUiIDogMQ0KCQkJCX0sDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAyLA0KCQkJCQkib3AiIDogIlNDTVBfQ01QX0VRIiwNCgkJCQkJInZhbHVlIiA6IDANCgkJCQl9DQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicHJvY2Vzc192bV9yZWFkdiIsDQoJCQkJInByb2Nlc3Nfdm1fd3JpdGV2IiwNCgkJCQkicHRyYWNlIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJtaW5LZXJuZWwiOiAiNC44Ig0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiAwLA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiDQoJCQkJfQ0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiA4LA0KCQkJCQkib3AiOiAiU0NNUF9DTVBfRVEiDQoJCQkJfQ0KCQkJXQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJInBlcnNvbmFsaXR5Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImFyZ3MiOiBbDQoJCQkJew0KCQkJCQkiaW5kZXgiOiAwLA0KCQkJCQkidmFsdWUiOiAxMzEwNzIsDQoJCQkJCSJvcCI6ICJTQ01QX0NNUF9FUSINCgkJCQl9DQoJCQldDQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkicGVyc29uYWxpdHkiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiYXJncyI6IFsNCgkJCQl7DQoJCQkJCSJpbmRleCI6IDAsDQoJCQkJCSJ2YWx1ZSI6IDEzMTA4MCwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIg0KCQkJCX0NCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJwZXJzb25hbGl0eSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJInZhbHVlIjogNDI5NDk2NzI5NSwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX0VRIg0KCQkJCX0NCgkJCV0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJzeW5jX2ZpbGVfcmFuZ2UyIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJwcGM2NGxlIg0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJhcm1fZmFkdmlzZTY0XzY0IiwNCgkJCQkiYXJtX3N5bmNfZmlsZV9yYW5nZSIsDQoJCQkJInN5bmNfZmlsZV9yYW5nZTIiLA0KCQkJCSJicmVha3BvaW50IiwNCgkJCQkiY2FjaGVmbHVzaCIsDQoJCQkJInNldF90bHMiDQoJCQldLA0KCQkJImFjdGlvbiI6ICJTQ01QX0FDVF9BTExPVyIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJImFybSIsDQoJCQkJCSJhcm02NCINCgkJCQldDQoJCQl9DQoJCX0sDQoJCXsNCgkJCSJuYW1lcyI6IFsNCgkJCQkiYXJjaF9wcmN0bCINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJpbmNsdWRlcyI6IHsNCgkJCQkiYXJjaGVzIjogWw0KCQkJCQkiYW1kNjQiLA0KCQkJCQkieDMyIg0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJtb2RpZnlfbGR0Ig0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJhbWQ2NCIsDQoJCQkJCSJ4MzIiLA0KCQkJCQkieDg2Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJzMzkwX3BjaV9tbWlvX3JlYWQiLA0KCQkJCSJzMzkwX3BjaV9tbWlvX3dyaXRlIiwNCgkJCQkiczM5MF9ydW50aW1lX2luc3RyIg0KCQkJXSwNCgkJCSJhY3Rpb24iOiAiU0NNUF9BQ1RfQUxMT1ciLA0KCQkJImluY2x1ZGVzIjogew0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJzMzkwIiwNCgkJCQkJInMzOTB4Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJjbG9uZSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMCwNCgkJCQkJInZhbHVlIjogMjExNDA2MDI4OCwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX01BU0tFRF9FUSINCgkJCQl9DQoJCQldLA0KCQkJImV4Y2x1ZGVzIjogew0KCQkJCSJjYXBzIjogWw0KCQkJCQkiQ0FQX1NZU19BRE1JTiINCgkJCQldLA0KCQkJCSJhcmNoZXMiOiBbDQoJCQkJCSJzMzkwIiwNCgkJCQkJInMzOTB4Ig0KCQkJCV0NCgkJCX0NCgkJfSwNCgkJew0KCQkJIm5hbWVzIjogWw0KCQkJCSJjbG9uZSINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0FMTE9XIiwNCgkJCSJhcmdzIjogWw0KCQkJCXsNCgkJCQkJImluZGV4IjogMSwNCgkJCQkJInZhbHVlIjogMjExNDA2MDI4OCwNCgkJCQkJIm9wIjogIlNDTVBfQ01QX01BU0tFRF9FUSINCgkJCQl9DQoJCQldLA0KCQkJImNvbW1lbnQiOiAiczM5MCBwYXJhbWV0ZXIgb3JkZXJpbmcgZm9yIGNsb25lIGlzIGRpZmZlcmVudCIsDQoJCQkiaW5jbHVkZXMiOiB7DQoJCQkJImFyY2hlcyI6IFsNCgkJCQkJInMzOTAiLA0KCQkJCQkiczM5MHgiDQoJCQkJXQ0KCQkJfSwNCgkJCSJleGNsdWRlcyI6IHsNCgkJCQkiY2FwcyI6IFsNCgkJCQkJIkNBUF9TWVNfQURNSU4iDQoJCQkJXQ0KCQkJfQ0KCQl9LA0KCQl7DQoJCQkibmFtZXMiOiBbDQoJCQkJImNsb25lMyINCgkJCV0sDQoJCQkiYWN0aW9uIjogIlNDTVBfQUNUX0VSUk5PIiwNCgkJCSJlcnJub1JldCI6IDM4LA0KCQkJImV4Y2x1ZGVzIjogew0KCQkJCSJjYXBzIjogWw0KCQkJCQkiQ0FQX1NZU19BRE1JTiINCgkJCQldDQoJCQl9DQoJCX0NCgldDQp9"
        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json.replace("seccompStr", seccomp_profile_contents), "")[
            0
        ]
        aci_arm_policy.populate_policy_content_for_all_images()
        expected_seccomp_profile_sha256 = "7bf01bd03f545de915a4ef29d8a60febfe2ee2ef557240d181460fb9a24aea88"

        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256], expected_seccomp_profile_sha256)

    def test_arm_template_security_context_seccomp_profile_missing_syscalls(self):
        seccomp_profile_contents = "ew0KCSJjb21tZW50IjogIkRlZmF1bHQgbW9ieSBzZWNjb21wIHBvbGljeSBjb25maWcgZmlsZSBhdDogaHR0cHM6Ly9naXRodWIuY29tL21vYnkvbW9ieS9ibG9iL21hc3Rlci9wcm9maWxlcy9zZWNjb21wL2RlZmF1bHQuanNvbiIsDQoJImRlZmF1bHRBY3Rpb24iOiAiU0NNUF9BQ1RfRVJSTk8iLA0KCSJkZWZhdWx0RXJybm9SZXQiOiAxLA0KCSJhcmNoaXRlY3R1cmVzIjogWyAiU0NNUF9BUkNIX1g4NiIsICJTQ01QX0FSQ0hfUFBDIl0sDQoJImZsYWdzIjogWyAiZmxhZzEiLCAiZmxhZzIiLCAiZmxhZzMiIF0sDQoJImxpc3RlbmVyUGF0aCI6ICIvbGlzdGVuZXIvUGF0aCIsDQoJImxpc3RlbmVyTWV0YWRhdGEiOiAibWV0YWRhdGEiDQp9"
        aci_arm_policy = load_policy_from_arm_template_str(self.custom_arm_json.replace("seccompStr", seccomp_profile_contents), "")[
            0
        ]
        aci_arm_policy.populate_policy_content_for_all_images()
        expected_seccomp_profile_sha256 = "4fef6e87b27dfb72359d960b62948bb2072226b497d8f8164c57d6eeaf108479"

        regular_image_json = json.loads(
            aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )

        self.assertEqual(regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SECCOMP_PROFILE_SHA256], expected_seccomp_profile_sha256)


class PolicyStopSignal(unittest.TestCase):
    custom_arm_json = """
    {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "variables": {
            "image": "nginx:1.24"
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
            "defaultValue": "80"
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
    aci_policy = None

    @classmethod
    def setUpClass(cls):

        cls.aci_arm_policy = load_policy_from_arm_template_str(cls.custom_arm_json, "")[
            0
        ]
        cls.aci_arm_policy.populate_policy_content_for_all_images()

    def test_stop_signal(self):
        regular_image_json = json.loads(
            self.aci_arm_policy.get_serialized_output(
                output_type=OutputType.RAW, rego_boilerplate=False
            )
        )
        # check for the signal for SIGQUIT. this is part of the nginx image
        self.assertTrue(
            3 in
            regular_image_json[0][config.POLICY_FIELD_CONTAINERS_ELEMENTS_SIGNAL_CONTAINER_PROCESSES]
        )
