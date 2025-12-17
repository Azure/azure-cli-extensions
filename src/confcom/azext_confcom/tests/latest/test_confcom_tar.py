# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
import tempfile
import unittest
from tarfile import TarFile

import azext_confcom.config as config
import deepdiff
from azext_confcom.errors import AccContainerError
from azext_confcom.os_util import delete_silently
from azext_confcom.rootfs_proxy import SecurityPolicyProxy
from azext_confcom.security_policy import (OutputType,
                                           load_policy_from_arm_template_str)
from azext_confcom.template_util import DockerClient


def create_tar_file(image_path: str) -> None:
    if not os.path.isfile(image_path):
        with DockerClient() as client:
            client.images.pull("mcr.microsoft.com/aks/e2e/library-busybox", tag="master.220314.1-linux-amd64")
            image = client.images.get("mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64")
            f = open(image_path, "wb")
            for chunk in image.save(named=True):
                f.write(chunk)
            f.close()


class PolicyGeneratingArmParametersCleanRoomOCITarFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.dirname(__file__)
        cls.path = path

    def test_oci_tar_file(self):
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
                "defaultValue":"mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64"
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

        regular_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        regular_image.populate_policy_content_for_all_images()
        SecurityPolicyProxy.layer_cache = {}
        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        try:
            with tempfile.TemporaryDirectory() as folder:
                filename = os.path.join(folder, "oci.tar")
                filename2 = os.path.join(self.path, "oci2.tar")

                tar_mapping_file = {"mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64": filename2}
                create_tar_file(filename)
                with TarFile(filename, "r") as tar:
                    tar.extractall(path=folder)

                with TarFile.open(filename2, mode="w") as out_tar:
                    out_tar.add(os.path.join(folder, "index.json"), "index.json")
                    out_tar.add(os.path.join(folder, "blobs"), "blobs", recursive=True)

                clean_room_image.populate_policy_content_for_all_images(
                    tar_mapping=tar_mapping_file
                )
        except Exception as e:
            raise AccContainerError("Could not get image from tar file") from e

        regular_image_json = json.loads(
            regular_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        clean_room_json = json.loads(
            clean_room_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        regular_image_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertEqual(
            deepdiff.DeepDiff(regular_image_json, clean_room_json, ignore_order=True),
            {},
        )

class PolicyGeneratingArmParametersCleanRoomTarFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.dirname(__file__)
        cls.path = path

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
                "defaultValue":"mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64"
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

        regular_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        regular_image.populate_policy_content_for_all_images()
        SecurityPolicyProxy.layer_cache = {}
        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        try:
            filename = os.path.join(self.path, "mariner.tar")
            tar_mapping_file = {"mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64": filename}
            create_tar_file(filename)
            clean_room_image.populate_policy_content_for_all_images(
                tar_mapping=tar_mapping_file
            )
        except Exception as e:
            raise AccContainerError("Could not get image from tar file") from e
        finally:
            delete_silently(filename)

        regular_image_json = json.loads(
            regular_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        clean_room_json = json.loads(
            clean_room_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        regular_image_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)

        # see if the remote image and the local one produce the same output
        self.assertEqual(
            deepdiff.DeepDiff(regular_image_json, clean_room_json, ignore_order=True),
            {},
        )

    def test_arm_template_mixed_mode_tar(self):
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
                "defaultValue":"mcr.microsoft.com/aks/e2e/library-busybox:master.220314.1-linux-amd64"
            },
            "containername": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container"
            },
            "image2": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container group"
                },
                "defaultValue":"mcr.microsoft.com/azurelinux/base/python:3.12"
            },
            "containername2": {
                "type": "string",
                "metadata": {
                    "description": "Name for the container"
                },
                "defaultValue":"simple-container2"
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
                },
                {
                    "name": "[parameters('containername2')]",

                    "properties": {
                    "image": "[parameters('image2')]",
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

        regular_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        regular_image.populate_policy_content_for_all_images()
        SecurityPolicyProxy.layer_cache = {}
        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        filename = os.path.join(self.path, "./mariner2.tar")
        create_tar_file(filename)
        image_mapping = {"mcr.microsoft.com/azurelinux/base/python:3.12": filename}

        # check to make sure many:1 mapping doesn't work
        with self.assertRaises(SystemExit) as exc_info:
            clean_room_image.populate_policy_content_for_all_images(
                tar_mapping=filename
            )
        self.assertEqual(exc_info.exception.code, 1)

        clean_room_image.populate_policy_content_for_all_images(
            tar_mapping=image_mapping
        )

        delete_silently(filename)
        regular_image_json = json.loads(
            regular_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        clean_room_json = json.loads(
            clean_room_image.get_serialized_output(output_type=OutputType.RAW, rego_boilerplate=False)
        )

        regular_image_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[0].pop(config.POLICY_FIELD_CONTAINERS_ID)
        regular_image_json[1].pop(config.POLICY_FIELD_CONTAINERS_ID)
        clean_room_json[1].pop(config.POLICY_FIELD_CONTAINERS_ID)

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
                "defaultValue":"mcr.microsoft.com/azurelinux/distroless/base:3.0"
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

        clean_room_image = load_policy_from_arm_template_str(
            custom_arm_json_default_value, ""
        )[0]

        filename = os.path.join(self.path, "./mariner3.tar")

        try:
            create_tar_file(filename)
            clean_room_image.populate_policy_content_for_all_images(
                tar_mapping=filename
            )
            raise AccContainerError("getting image should fail")
        except:
            pass
        finally:
            delete_silently(filename)

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
                "defaultValue":"mcr.microsoft.com/azurelinux/distroless/base:3.0"
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
