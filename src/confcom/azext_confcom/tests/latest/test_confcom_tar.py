# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import pytest
import deepdiff
import json
import docker

from azext_confcom.security_policy import (
    OutputType,
    load_policy_from_arm_template_str,
)
from azext_confcom.errors import (
    AccContainerError,
)
import azext_confcom.config as config


# @unittest.skip("not in use")
@pytest.mark.run(order=11)
class PolicyGeneratingArmParametersCleanRoomTarFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # this is simulating the output of the "load_tar_mapping_from_file" output
        path = os.path.dirname(__file__)
        image_path = os.path.join(path, "./nginx.tar")

        tar_mapping_file = {"nginx:1.22": image_path}

        cls.path = path
        cls.tar_mapping_file = tar_mapping_file
        cls.image_path = image_path

    def test_arm_template_with_parameter_file_clean_room_tar(self):
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
                "defaultValue":"nginx:1.22"
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

        regular_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        regular_image.populate_policy_content_for_all_images()

        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        # save the tar file for the image in the testing directory
        client = docker.from_env()
        image = client.images.get("nginx:1.22")

        # Note: Class setup and teardown shouldn't have side effects, and reading from the tar file fails when all the tests are running in parallel, so we want to save and delete this tar file as a part of the test. Not as a part of the testing class.
        f = open(self.image_path, "wb")
        for chunk in image.save(named=True):
            f.write(chunk)
        f.close()
        client.close()

        try:
            clean_room_image.populate_policy_content_for_all_images(
                tar_mapping=self.tar_mapping_file
            )
        except:
            raise AccContainerError("Could not get image from tar file")
        finally:
            # delete the tar file
            if os.path.isfile(self.image_path):
                os.remove(self.image_path)

        regular_image_json = json.loads(
            regular_image.get_serialized_output(output_type=OutputType.RAW, use_json=True)
        )

        clean_room_json = json.loads(
            clean_room_image.get_serialized_output(output_type=OutputType.RAW, use_json=True)
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

    def test_arm_template_with_parameter_file_clean_room_tar_invalid(self):
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
                "defaultValue":"rust:latest"
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

        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]
        # save the tar file for the image in the testing directory
        client = docker.from_env()
        image = client.images.pull("nginx:1.23")
        image = client.images.get("nginx:1.23")

        # Note: Class setup and teardown shouldn't have side effects, and reading from the tar file fails when all the tests are running in parallel, so we want to save and delete this tar file as a part of the test. Not as a part of the testing class.
        f = open(self.image_path, "wb")
        for chunk in image.save(named=True):
            f.write(chunk)
        f.close()
        client.close()

        try:
            clean_room_image.populate_policy_content_for_all_images(
                tar_mapping=self.tar_mapping_file
            )
            raise AccContainerError("getting image should fail")
        except:
            pass
        finally:
            # delete the tar file
            if os.path.isfile(self.image_path):
                os.remove(self.image_path)

    def test_clean_room_fake_tar_invalid(self):
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
                "defaultValue":"rust:latest"
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

        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]
        try:
            clean_room_image.populate_policy_content_for_all_images(
                tar_mapping=os.path.join(self.path, "fake-file.tar")
            )
            raise AccContainerError("getting image should fail")
        except FileNotFoundError:
            pass
