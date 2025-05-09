# Azure CLI SiteRecovery Extension #
This is an extension to Azure CLI to manage SiteRecovery resources.

## How to use ##
### Create a VM as the target
`az vm create -n vm_name -g vm_rg --image Win2012Datacenter --public-ip-sku Standard --admin-password password`

### Create a SiteRecovery Vault
`az backup vault create -g rg -n vault_name -l recovery_loc`

### Create fabrics for the target and recovery region
`az site-recovery fabric create -n fabric_source_name -g rg --vault-name vault_name 
--custom-details '{azure:{location:source_loc}}'`  

`az site-recovery fabric create -n fabric_recovery_name -g rg --vault-name vault_name 
--custom-details '{azure:{location:recovery_loc}}'`

### Create a policy
`az site-recovery policy create -g rg --vault-name vault_name -n policy_name 
--provider-specific-input '{a2a:{multi-vm-sync-status:Enable}}'`

### Create protection containers
`az site-recovery protection-container create -g rg --fabric-name fabric_source_name 
-n container_source_name --vault-name vault_name --provider-input '[{instance-type:A2A}]'`  

`az site-recovery protection-container create -g rg --fabric-name fabric_recovery_name 
-n container_recovery_name --vault-name vault_name --provider-input '[{instance-type:A2A}]'`

### Create container mappings
`az site-recovery protection-container mapping create -g rg --fabric-name fabric_source_name 
-n container_mapping_source_name --protection-container container_source_name --vault-name vault_name 
--policy-id policy_id --provider-input '{a2a:{agent-auto-update-status:Disabled}}' --target-container container_recovery_id`  

`az site-recovery protection-container mapping create -g rg --fabric-name fabric_recovery_name 
-n container_mapping_recovery_name --protection-container container_recovery_name --vault-name vault_name 
--policy-id policy_id --provider-input '{a2a:{agent-auto-update-status:Disabled}}' --target-container container_source_id`

### Create network mappings
`az site-recovery network-mapping create -g rg --fabric-name fabric_source_name 
-n network_mapping_src_to_recovery_name --network-name azureNetwork --vault-name vault_name 
--recovery-network-id vnet_recovery_id --fabric-details '{azure-to-azure:{primary-network-id:vnetvm_id}}' 
--recovery-fabric-name fabric_recovery_name`  

`az site-recovery network-mapping create -g rg --fabric-name fabric_recovery_name 
-n network_mapping_recovery_to_src_name --network-name azureNetwork --vault-name vault_name 
--recovery-network-id vnetvm_id --fabric-details '{azure-to-azure:{primary-network-id:vnet_recovery_id}}' 
--recovery-fabric-name fabric_source_name`

### Enable protection
`az site-recovery protected-item create -g rg --fabric-name fabric_source_name -n protected_item_name 
--protection-container container_source_name --vault-name vault_name --policy-id policy_id 
--provider-details '{a2a:{fabric-object-id:vm_id,vm-managed-disks:[{disk-id:os_disk,
primary-staging-azure-storage-account-id:sa_src_id,recovery-resource-group-id:rg_id}],
recovery-azure-network-id:vnet_recovery_id,recovery-container-id:container_recovery_id,
recovery-resource-group-id:rg_id,recovery-subnet-name:vnet_recovery_subnet}}'`

### Failover
`az site-recovery protected-item unplanned-failover --fabric-name fabric_source_name 
--protection-container container_source_name -n protected_item_name -g rg --vault-name vault_name 
--failover-direction PrimaryToRecovery --provider-details '{a2a:{}}' --source-site-operations NotRequired`
