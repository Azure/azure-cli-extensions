# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import tempfile
from azure.cli.testsdk import ScenarioTest


class CLITranslatorScenarioTest(ScenarioTest):

    def test_arm_translator(self):
        TEMPLATE_CONTENT = '''
{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "location": {
            "type": "string"
        },
        "networkInterfaceName": {
            "type": "string"
        },
        "subnetName": {
            "type": "string"
        },
        "virtualNetworkName": {
            "type": "string"
        },
        "addressPrefixes": {
            "type": "array"
        },
        "subnets": {
            "type": "array"
        },
        "publicIpAddressName": {
            "type": "string"
        },
        "publicIpAddressType": {
            "type": "string"
        },
        "publicIpAddressSku": {
            "type": "string"
        },
        "virtualMachineName": {
            "type": "string"
        },
        "virtualMachineComputerName": {
            "type": "string"
        },
        "virtualMachineRG": {
            "type": "string"
        },
        "osDiskType": {
            "type": "string"
        },
        "dataDisks": {
            "type": "array"
        },
        "dataDiskResources": {
            "type": "array"
        },
        "virtualMachineSize": {
            "type": "string"
        },
        "adminUsername": {
            "type": "string"
        }
    },
    "variables": {
        "vnetId": "[resourceId(resourceGroup().name,'Microsoft.Network/virtualNetworks', parameters('virtualNetworkName'))]",
        "subnetRef": "[concat(variables('vnetId'), '/subnets/', parameters('subnetName'))]"
    },
    "resources": [
        {
            "name": "[parameters('networkInterfaceName')]",
            "type": "Microsoft.Network/networkInterfaces",
            "apiVersion": "2019-07-01",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[concat('Microsoft.Network/virtualNetworks/', parameters('virtualNetworkName'))]",
                "[concat('Microsoft.Network/publicIpAddresses/', parameters('publicIpAddressName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "subnet": {
                                "id": "[variables('subnetRef')]"
                            },
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIpAddress": {
                                "id": "[resourceId(resourceGroup().name, 'Microsoft.Network/publicIpAddresses', parameters('publicIpAddressName'))]"
                            }
                        }
                    }
                ]
            }
        },
        {
            "name": "[parameters('virtualNetworkName')]",
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2019-09-01",
            "location": "[parameters('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": "[parameters('addressPrefixes')]"
                },
                "subnets": "[parameters('subnets')]"
            }
        },
        {
            "name": "[parameters('publicIpAddressName')]",
            "type": "Microsoft.Network/publicIpAddresses",
            "apiVersion": "2019-02-01",
            "location": "[parameters('location')]",
            "properties": {
                "publicIpAllocationMethod": "[parameters('publicIpAddressType')]"
            },
            "sku": {
                "name": "[parameters('publicIpAddressSku')]"
            }
        },
        {
            "name": "[parameters('dataDiskResources')[copyIndex()].name]",
            "type": "Microsoft.Compute/disks",
            "apiVersion": "2019-07-01",
            "location": "[parameters('location')]",
            "properties": "[parameters('dataDiskResources')[copyIndex()].properties]",
            "sku": {
                "name": "[parameters('dataDiskResources')[copyIndex()].sku]"
            },
            "copy": {
                "name": "managedDiskResources",
                "count": "[length(parameters('dataDiskResources'))]"
            }
        },
        {
            "name": "[parameters('virtualMachineName')]",
            "type": "Microsoft.Compute/virtualMachines",
            "apiVersion": "2019-07-01",
            "location": "[parameters('location')]",
            "dependsOn": [
                "managedDiskResources",
                "[concat('Microsoft.Network/networkInterfaces/', parameters('networkInterfaceName'))]"
            ],
            "properties": {
                "hardwareProfile": {
                    "vmSize": "[parameters('virtualMachineSize')]"
                },
                "storageProfile": {
                    "osDisk": {
                        "createOption": "fromImage",
                        "managedDisk": {
                            "storageAccountType": "[parameters('osDiskType')]"
                        }
                    },
                    "imageReference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "18.04-LTS",
                        "version": "latest"
                    },
                    "copy": [
                        {
                            "name": "dataDisks",
                            "count": "[length(parameters('dataDisks'))]",
                            "input": {
                                "lun": "[parameters('dataDisks')[copyIndex('dataDisks')].lun]",
                                "createOption": "[parameters('dataDisks')[copyIndex('dataDisks')].createOption]",
                                "caching": "[parameters('dataDisks')[copyIndex('dataDisks')].caching]",
                                "writeAcceleratorEnabled": "[parameters('dataDisks')[copyIndex('dataDisks')].writeAcceleratorEnabled]",
                                "diskSizeGB": "[parameters('dataDisks')[copyIndex('dataDisks')].diskSizeGB]",
                                "managedDisk": {
                                    "id": "[coalesce(parameters('dataDisks')[copyIndex('dataDisks')].id, if(equals(parameters('dataDisks')[copyIndex('dataDisks')].name, json('null')), json('null'), resourceId('Microsoft.Compute/disks', parameters('dataDisks')[copyIndex('dataDisks')].name)))]",
                                    "storageAccountType": "[parameters('dataDisks')[copyIndex('dataDisks')].storageAccountType]",
                                    "diskEncryptionSet": {
                                        "id": "[parameters('dataDisks')[copyIndex('dataDisks')].diskEncryptionSet.id]"
                                    }
                                }
                            }
                        }
                    ]
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', parameters('networkInterfaceName'))]"
                        }
                    ]
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachineComputerName')]",
                    "adminUsername": "[parameters('adminUsername')]",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true
                    }
                }
            }
        }
    ],
    "outputs": {
        "adminUsername": {
            "type": "string",
            "value": "[parameters('adminUsername')]"
        }
    }
}
        '''

        PARAMETERS_CONTENT = '''
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "location": {
            "value": "japaneast"
        },
        "networkInterfaceName": {
            "value": "test-vm650"
        },
        "subnetName": {
            "value": "default2"
        },
        "virtualNetworkName": {
            "value": "test-rg-vnet"
        },
        "addressPrefixes": {
            "value": [
                "10.2.11.0/24"
            ]
        },
        "subnets": {
            "value": [
                {
                    "name": "default1",
                    "properties": {
                        "addressPrefix": "10.2.11.128/25"
                    }
                },
                {
                    "name": "default2",
                    "properties": {
                        "addressPrefix": "10.2.11.0/25"
                    }
                }
            ]
        },
        "publicIpAddressName": {
            "value": "test-vm-ip"
        },
        "publicIpAddressType": {
            "value": "Dynamic"
        },
        "publicIpAddressSku": {
            "value": "Basic"
        },
        "virtualMachineName": {
            "value": "test-vm"
        },
        "virtualMachineComputerName": {
            "value": "test-vm"
        },
        "virtualMachineRG": {
            "value": "test-rg"
        },
        "osDiskType": {
            "value": "Premium_LRS"
        },
        "dataDisks": {
            "value": [
                {
                    "lun": 0,
                    "createOption": "attach",
                    "caching": "None",
                    "writeAcceleratorEnabled": false,
                    "id": null,
                    "name": "test-vm_DataDisk_0",
                    "storageAccountType": null,
                    "diskSizeGB": null,
                    "diskEncryptionSet": {
                        "id": null
                    }
                }
            ]
        },
        "dataDiskResources": {
            "value": [
                {
                    "name": "test-vm_DataDisk_0",
                    "sku": "Premium_LRS",
                    "properties": {
                        "diskSizeGB": 16,
                        "creationData": {
                            "createOption": "empty"
                        }
                    }
                }
            ]
        },
        "virtualMachineSize": {
            "value": "Standard_D2s_v3"
        },
        "adminUsername": {
            "value": "AzureUser"
        }
    }
}
        '''
        tempdir = os.path.realpath(tempfile.gettempdir())
        template_path = os.path.join(tempdir, 'template.json')
        parameters_path = os.path.join(tempdir, 'parameters.json')
        with open(template_path, 'w') as fp:
            fp.write(TEMPLATE_CONTENT)
        with open(parameters_path, 'w') as fp:
            fp.write(PARAMETERS_CONTENT)
        self.kwargs.update({
            'parameters': parameters_path,
            'template': template_path,
            'resource_group': 'test-rg',
            'target_subscription': '00000000-0000-0000-0000-000000000000'
        })
        self.cmd('cli-translator arm translate --target-subscription {target_subscription} --resource-group {resource_group} --template {template} --parameters {parameters}')
