# Azure CLI NeuroShield Extension

Azure CLI extension for managing NeuroShield (`Microsoft.NetworkSecurity/neuroShields`)
resources, using API version `2026-10-01-preview`.

NeuroShield is in preview. The subscription must be registered for the
`Microsoft.NetworkSecurity/NeuroShieldPreview` feature:

```bash
az feature register --namespace Microsoft.NetworkSecurity --name NeuroShieldPreview
az provider register --namespace Microsoft.NetworkSecurity
```

## Install

```bash
az extension add --name neuroshield
```

## Usage

### NeuroShield

```bash
az neuroshield create -g myResourceGroup -n myNeuroShield --location eastus2 \
    --response-mode Manual --severity-threshold Medium
az neuroshield update -g myResourceGroup -n myNeuroShield --response-mode Auto
az neuroshield show -g myResourceGroup -n myNeuroShield
az neuroshield list -g myResourceGroup
az neuroshield delete -g myResourceGroup -n myNeuroShield
```

### Protected resources

A protected resource registers a VM or VMSS with a NeuroShield. The target resource ID
and target identity are set at creation and cannot be updated; recreate the protected
resource to change them.

```bash
az neuroshield protected-resource create -g myResourceGroup --neuroshield-name myNeuroShield -n vm-01 \
    --target-resource-id /subscriptions/{sub}/resourceGroups/myComputeRg/providers/Microsoft.Compute/virtualMachines/vm-01 \
    --target-identity "{type:SystemAssigned,principal-id:{principalId},tenant-id:{tenantId}}"
az neuroshield protected-resource list -g myResourceGroup --neuroshield-name myNeuroShield
az neuroshield protected-resource trigger-inventory-upload -g myResourceGroup --neuroshield-name myNeuroShield -n vm-01
az neuroshield protected-resource delete -g myResourceGroup --neuroshield-name myNeuroShield -n vm-01
```

### Findings and mitigations

```bash
# All findings and mitigations under a NeuroShield
az neuroshield finding list -g myResourceGroup --neuroshield-name myNeuroShield
az neuroshield mitigation list -g myResourceGroup --neuroshield-name myNeuroShield

# Per protected resource
az neuroshield protected-resource finding list -g myResourceGroup --neuroshield-name myNeuroShield --protected-resource vm-01
az neuroshield protected-resource finding mitigate -g myResourceGroup --neuroshield-name myNeuroShield --protected-resource vm-01 --finding-id {findingId}
az neuroshield protected-resource mitigation execute -g myResourceGroup --neuroshield-name myNeuroShield --protected-resource vm-01 --mitigation-id {mitigationId}
az neuroshield protected-resource mitigation rollback -g myResourceGroup --neuroshield-name myNeuroShield --protected-resource vm-01 --mitigation-id {mitigationId}

# Counts of findings and mitigations
az neuroshield summary show -g myResourceGroup --neuroshield-name myNeuroShield
```

To list the resource provider operations, use
`az provider operation show --namespace Microsoft.NetworkSecurity`.
