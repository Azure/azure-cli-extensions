# Azure CLI Automanage Extension #
This is an extension to Azure CLI to manage Automanage resources.

## How to use ##
# configuration-profile
Create a configuration-profile  
`az automanage configuration-profile create -n {profile_name} -g {rg} --configuration '{"Antimalware/Enable":false,"Backup/Enable":false,"VMInsights/Enable":true,"AzureSecurityCenter/Enable":true,"UpdateManagement/Enable":true,"ChangeTrackingAndInventory/Enable":true,"GuestConfiguration/Enable":true,"LogAnalytics/Enable":true,"BootDiagnostics/Enable":true}'`  

Show a configuration-profile  
`az automanage configuration-profile show -n {profile_name} -g {rg}`

Update a configuration-profile  
`az automanage configuration-profile update -n {profile_name} -g {rg} --configuration '{"Antimalware/Enable":true,"VMInsights/Enable":false}'`

List configuration-profiles  
`az automanage configuration-profile list -g {rg}`

Delete a configuration-profile  
`az automanage configuration-profile delete -n {profile_name} -g {rg}`

# configuration-profile-assignment
Create a configuration-profile-assignment for vm  
`az automanage configuration-profile-assignment vm create -n default -g {rg} --vm-name {vm_name} --configuration-profile {profile_id}`

Show a configuration-profile-assignment for vm  
`az automanage configuration-profile-assignment vm show -n default -g {rg} --vm-name {vm_name}`

Update a configuration-profile-assignment for vm  
`az automanage configuration-profile-assignment vm update --n default -g {rg} --vm-name {vm_name} --configuration-profile {profile_id_2}`

Delete configuration-profile-assignment for vm  
`az automanage configuration-profile-assignment vm delete -n default -g {rg} --vm-name {vm_name}`

Create a configuration-profile-assignment for arc   
`az automanage configuration-profile-assignment arc create -n default -g {rg} --machine-name {arc_name} --configuration-profile {profile_id}`

# configuration-profile-assignment report
List configuration-profile-assignment report for vm  
`az automanage configuration-profile-assignment vm report list --assignment-name default -g {rg} --vm-name {vm_name}`