def create_dev_center(self):
    dev_center = self.cmd('az devcenter admin devcenter create '
                          '--location "{location}" '
                          '--tags CostCode="12345" '
                          '--name "{devcenterName}" '
                          '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'devCenterId': dev_center['id'],
    })


def create_identity(self):
    return self.cmd('az identity create '
                    '--resource-group {rg} '
                    '--name {identityName}').get_output_in_json()


def create_dev_center_with_identity(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
        'identityName': self.create_random_name(prefix='testid_', length=24)
    })

    test_identity = create_identity(self)

    self.kwargs.update({
        'userAssignedIdentity': test_identity['id'],
        'identityPrincipalId': test_identity['principalId']
    })

    dev_center = self.cmd('az devcenter admin devcenter create '
                          '--identity-type "UserAssigned" '
                          '--user-assigned-identities "{{\\"{userAssignedIdentity}\\":{{}}}}" '
                          '--location "{location}" '
                          '--tags CostCode="12345" '
                          '--name "{devcenterName}" '
                          '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'devCenterId': dev_center['id']
    })


def create_virtual_network_with_subnet(self):
    self.kwargs.update({
        'vNetName': self.create_random_name(prefix='cli', length=24),
        'subnetName': self.create_random_name(prefix='cli', length=24)
    })

    self.cmd('az network vnet create -n "{vNetName}" --location "{location}" -g "{rg}"')

    return self.cmd('az network vnet subnet create -n "{subnetName}" --vnet-name "{vNetName}" -g "{rg}" --address-prefixes "10.0.0.0/21"').get_output_in_json()


def create_sig(self):
    self.kwargs.update({
        'sigName': self.create_random_name(prefix='cli', length=24),
        'imageDefName': self.create_random_name(prefix='cli', length=12),
        'computeVmName': self.create_random_name(prefix='cli', length=12),
        'computeVmPassword': 'Cli!123123fakepassword',
        'computeUserName': self.create_random_name(prefix='cli', length=12),
        'publisher': "MicrosoftWindowsDesktop",
        'offer': "Windows-10",
        'sku': "win10-21h2-entn-g2",
        'imageVersion': "1.0.0"
    })

    sig = self.cmd('az sig create -r "{sigName}" --location "{location}" -g "{rg}"').get_output_in_json()

    self.cmd('az sig image-definition create -i "{imageDefName}" -p "{publisher}" '
             '-g "{rg}" -f "{offer}" -s "{sku}" --location "{location}" '
             '--os-type "Windows" -r "{sigName}" --hyper-v-generation "V2" --features SecurityType=TrustedLaunch')

    self.kwargs.update({
        'sigId': sig['id']
    })

    # Create compute virtual machine
    self.cmd('az vm create -n "{computeVmName}" '
             '-g "{rg}" '
             '--image "MicrosoftWindowsDesktop:Windows-10:win10-21h2-entn-g2:19044.2486.230107" '
             '--location "{location}" '
             '--security-type TrustedLaunch '
             '--admin-password "{computeVmPassword}" '
             '--admin-username "{computeUserName}"')

    compute_vm = self.cmd('az vm show -n "{computeVmName}" '
                          '-g "{rg}" ').get_output_in_json()

    self.kwargs.update({
        'diskId': compute_vm['storageProfile']['osDisk']['managedDisk']['id'],
    })

    self.cmd('az sig image-version create '
             '-g "{rg}" '
             '--gallery-name "{sigName}" '
             '--gallery-image-definition "{imageDefName}" '
             '--location "{location}" '
             '--gallery-image-version {imageVersion} '
             '--os-snapshot "{diskId}" ')


def create_sig_role_assignments(self):
    self.kwargs.update({
        'windows365ObjectId': '8eec7c09-06ae-48e9-aafd-9fb31a5d5175'
    })

    self.cmd('az role assignment create --role "Contributor" '
             '--assignee "{identityPrincipalId}" '
             '--scope "{sigId}"')

    self.cmd('az role assignment create --role "Reader" '
             '--assignee "{windows365ObjectId}" '
             '--scope "{sigId}"')

def create_kv_policy(self):
    self.cmd('az keyvault set-policy -n "clitesting" '
            '--secret-permissions get list '
            '--object-id "{identityPrincipalId}"')

def create_project(self):
    self.kwargs.update({
        'projectName': self.create_random_name(prefix='cli', length=24)
    })

    self.cmd('az devcenter admin project create '
             '--location "{location}" '
             '--name "{projectName}" '
             '--dev-center-id "{devCenterId}" '
             '--resource-group "{rg}"')


def create_network_connection(self):
    subnet = create_virtual_network_with_subnet(self)

    self.kwargs.update({
        'subnetId': subnet['id'],
        'networkConnectionName': self.create_random_name(prefix='cli', length=24),
        'networkingRgName1': self.create_random_name(prefix='cli', length=24),
    })

    network_connection = self.cmd('az devcenter admin network-connection create '
                                  '--location "{location}" '
                                  '--tags CostCode="12345" '
                                  '--name "{networkConnectionName}" '
                                  '--domain-join-type "AzureADJoin" '
                                  '--subnet-id "{subnetId}" '
                                  '--networking-resource-group-name "{networkingRgName1}" '
                                  '--resource-group "{rg}"').get_output_in_json()

    self.kwargs.update({
        'networkConnectionId': network_connection['id'],
    })


def create_attached_network_dev_box_definition(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
    })

    create_dev_center(self)
    create_project(self)
    create_network_connection(self)
    self.kwargs.update({
        'imageRefId': "/subscriptions/{subscriptionId}/resourceGroups/{rg}/providers/Microsoft.DevCenter/devcenters/{devcenterName}/galleries/default/images/microsoftwindowsdesktop_windows-ent-cpc_win11-22h2-ent-cpc-m365",
        'devBoxDefinitionName': self.create_random_name(prefix='c1', length=12),
        'osStorageType': "ssd_1024gb",
        'skuName': "general_a_8c32gb_v1",
        'attachedNetworkName': self.create_random_name(prefix='c2', length=12),
        'devBoxDefinitionName2': self.create_random_name(prefix='c2', length=12)
    })

    self.cmd('az devcenter admin attached-network create '
             '--dev-center "{devcenterName}" '
             '--name "{attachedNetworkName}" '
             '--network-connection-id "{networkConnectionId}" '
             '--resource-group "{rg}" '
             )

    self.cmd('az devcenter admin devbox-definition create '
             '--dev-center "{devcenterName}" '
             '--name "{devBoxDefinitionName}" '
             '--image-reference id="{imageRefId}" '
             '--resource-group "{rg}" '
             '--os-storage-type "{osStorageType}" '
             '--sku name="{skuName}" '
             '--location "{location}" '
             )

    self.cmd('az devcenter admin devbox-definition create '
             '--dev-center "{devcenterName}" '
             '--name "{devBoxDefinitionName2}" '
             '--image-reference id="{imageRefId}" '
             '--resource-group "{rg}" '
             '--os-storage-type "{osStorageType}" '
             '--sku name="{skuName}" '
             '--location "{location}" '
             )
