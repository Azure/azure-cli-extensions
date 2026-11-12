# Azure CLI Commvault Extension #

This extension manages the Commvault Cloud resources of the `Commvault.ContentStore` resource provider
(API version `2026-09-30`): cloud accounts, backup plans, storages, protection groups, protected items and
role mappings.

## Install ##

```bash
az extension add --name commvault
```

## Command groups ##

| Command group | Description |
| --- | --- |
| `az commvault cloud-account` | Create, update, list, show and delete cloud accounts. Link a Marketplace SaaS resource. |
| `az commvault cloud-account identity` | Assign, remove and show the managed identities of a cloud account. |
| `az commvault cloud-account plan` | Manage backup plans. |
| `az commvault cloud-account storage` | Manage storages and their compliance lock. |
| `az commvault cloud-account protection-group` | Manage protection groups, start ad-hoc backups, stop or resume backups and restore virtual machines. |
| `az commvault cloud-account protection-group protected-item` | List protected items, get their restore points and restore them. |
| `az commvault cloud-account role-mapping` | Map Commvault roles to Microsoft Entra users and groups. |
| `az commvault` | Activate a SaaS resource (`activate-saas`) and count protected items (`protected-item-count`). |

Run `az commvault -h` or `az commvault cloud-account create -h` for the full list of arguments and examples.

## Examples ##

Create a cloud account:

```bash
az commvault cloud-account create --resource-group rg-commvault-demo --name contoso-commvault --location eastus \
    --marketplace "{subscription-id:00000000-0000-0000-0000-000000000001,offer-details:{publisher-id:commvault,offer-id:commvault-cloud-offer,plan-id:commvault-cloud-plan,plan-name:'Commvault Cloud',term-unit:P1M,term-id:commvault-cloud-term}}" \
    --user "{first-name:John,last-name:Smith,email-address:john.smith@contoso.com,upn:john.smith@contoso.com,phone-number:425-555-0100}"
```

Create an Air Gap Protect storage:

```bash
az commvault cloud-account storage create --resource-group rg-commvault-demo --cloud-account-name contoso-commvault \
    --name contoso-airgap-storage --location eastus --storage-type Air_Gap_Protect --vendor Azure_Blob_Storage --class COLD
```

Create a protection group of Azure virtual machines and start an ad-hoc backup:

```bash
az commvault cloud-account protection-group create --resource-group rg-commvault-demo --cloud-account-name contoso-commvault \
    --name vm-protection-group --data-source-type AzureVM --plan daily-vm-plan \
    --resources "{match-rules:{match-type:all,rules:[{property:resourceGroup,operator:equals,value:rg-workloads}]}}"

az commvault cloud-account protection-group backup --resource-group rg-commvault-demo --cloud-account-name contoso-commvault \
    --protection-group-name vm-protection-group --vm-list "[{vm-guid:40000000-aaaa-4bbb-8ccc-000000000000}]" \
    --backup-options "{backup-level:FULL,job-description:'Ad-hoc backup',backup-copy-immediately:true,run-snap-shot-backup:true,notify-user-on-job-completion:false}"
```

List the cloud accounts of the current subscription:

```bash
az commvault cloud-account list
```
