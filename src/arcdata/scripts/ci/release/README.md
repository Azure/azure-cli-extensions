# Release Overview

Releases are under the ADO Releases pipeline [azure-cli-extension (release)](https://msdata.visualstudio.com/Tina/_release?definitionId=111&view=mine&_a=releases)

## About `arcdatabot` github machine-user

The [arcdatabot](https://github.com/arcdatabot) is a service account github 
machine-user with the aim of helping to bring the Azure ArcData release process 
to full-automation. For the `arcdata` azure-cli-extension release, this user is
in charge of automating (CI/CD) the creation and merging of Pull Requests over 
to the [Azure/azure-cli-extensions](https://github.com/Azure/azure-cli-extensions) 
repository.

## About `ARCDATABOTGHSECRET` key-value secret

> *NOTE:* To update `ARCDATABOTGHSECRET` you will need read/write role under `arcdata-lab` key-vault.

- `ARCDATABOTGHSECRET` is a key in key-vault that holds the machine-user [arcdatabot](https://github.com/arcdatabot)'s 
Personal access token (classic) [arcdatabot token for CI/CD ](https://github.com/settings/tokens)
- `ARCDATABOTGHSECRET` is stored under the key-vault [arcdata-lab](https://ms.portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/d2f40113-58af-4e0d-8c88-5d0109e2f446/resourceGroups/arcdata-lab/providers/Microsoft.KeyVault/vaults/arcdata-lab/overview)
- `ARCDATABOTGHSECRET` coincides with [arcdatabot token for CI/CD ](https://github.com/settings/tokens) and should be rotated every 365 days. An email notification will remind DRI in advance when it needs to be rotated. 
- 
## Maintenance and PAT rotation

Every 365 days the [arcdatabot](https://github.com/arcdatabot)'s Personal 
access token (classic) [arcdatabot token for CI/CD ](https://github.com/settings/tokens)
will expire.

**Action:**
1. The `arcdatabot` github owner/subsidiary should generate a new PAT for a new 365 days.
2. Update `ARCDATABOTGHSECRET` value with the new PAT in the key-vault [arcdata-lab](https://ms.portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/d2f40113-58af-4e0d-8c88-5d0109e2f446/resourceGroups/arcdata-lab/providers/Microsoft.KeyVault/vaults/arcdata-lab/overview)


