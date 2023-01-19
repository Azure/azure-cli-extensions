def create_dev_center(self):
    self.kwargs.update({
        'devcenterName': self.create_random_name(prefix='cli', length=24),
    })

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
            'imageDefName': self.create_random_name(prefix='cli', length=6),
            'computeVmName': self.create_random_name(prefix='cli', length=12),
            'computeVmPassword': self.create_random_name(prefix='Cli!', length=13),
            'computeUserName': self.create_random_name(prefix='cli', length=6),
            'publisher': "MicrosoftWindowsDesktop",
            'offer': "Windows-10",
            'sku': "win10-21h2-entn-g2",
            'imageVersion': "1.0.0"
        })

    sig = self.cmd('az sig create -r "{sigName}" --location "{location}" -g "{rg}"')    

    self.cmd('az sig image-definition create -i "{imageDefName}" -p "{publisher}" '
         '-g "{rg}" -f "{offer}" -s "{sku}" --location "{location}" '
         '--os-type "Windows" -r "{sigName}" --hyper-v-generation "V2" --features SecurityType=TrustedLaunch')

    self.kwargs.update({
        'sigId': sig['id']
    })
    
    #Create compute virtual machine
    self.cmd('az vm create -n "{computeVmName}" '
         '-g "{rg}" '
         '--image "MicrosoftWindowsDesktop:Windows-10:win10-21h2-entn-g2:19044.2486.230107" '
         '--location "{location}" '
         '--security-type TrustedLaunch'
         '--admin-password "{computeVmPassword}" '
         '--admin-username "{computeUserName}"')
    
    compute_vm = self.cmd('az vm show -n "{computeVmName}" '
         '-g "{rg}" ').get_output_in_json()

    self.kwargs.update({
            'diskId': compute_vm['managedDisk']['id'],
        })

    self.cmd('az sig image-version create '
         '-g "{rg}" '
         '-gallery-name "{sigName}" '
         '--gallery-image-definition "{imageDefName}" '
         '--location "{location}" '
         '--gallery-image-version {imageVersion} '
         '--os-snapshot "{diskId}" ')

def create_sig_with_role_assignments(self):

    self.kwargs.update({
            'windows365ObjectId': '8eec7c09-06ae-48e9-aafd-9fb31a5d5175'
        })

    create_sig(self)

    self.command('az role assignment create --role "Contributor" ' 
         '--assignee "{identityPrincipalId}" ' 
         '--scope "{sigId}"')
    
    self.command('az role assignment create --role "Reader" ' 
         '--assignee "{windows365ObjectId}" ' 
         '--scope "{sigId}"')

def create_project(self):
    self.kwargs.update({
        'projectName': self.create_random_name(prefix='cli', length=24)
    })

    self.cmd('az devcenter admin project create '
             '--location "{location}" '
             '--name "{projectName}" '
             '--dev-center-id "{devCenterId}" '
             '--resource-group "{rg}"')