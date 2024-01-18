# Release History

## 6.0.1 (2023-12)

- Fix `az vmware private-cloud list-admin-credentials` not returning `nsxtPassword` and `vcenterPassword`

## 6.0.0 (2023-09)

- Update to AVS 2023-03-01 API
- Add `--ext-nw-blocks` argument to `az vmware private-cloud create`
- Add `--ext-nw-blocks` argument to `az vmware private-cloud update`
- Add `az vmware private-cloud identity-source` command group
- Deprecate `az vmware private-cloud add-identity-source` command
- Deprecate `az vmware private-cloud delete-identity-source` command
- Fix `--out` argument for `az vmware script-execution create` to accept a list of string values
- [BREAKING CHANGE] Remove `--port-name argument` argument from `az vmware workload-network segment create` as it is used by a read-only property
- [BREAKING CHANGE] Remove `--affinity-strength` and `--azure-hybrid-benefit` argument from `az vmware placement-policy vm update` as they are only used for `az vmware placement-policy vm-host update`

## 5.0.3 (2023-07)

- Fix the mandatory flag of `--hosts` for `az vmware cluster create` [#26653](https://github.com/Azure/azure-cli/issues/26653)

## 5.0.2 (2023-05)

- Update `az vmware cluster` subcommand descriptions

## 5.0.1 (2022-12)

- Update to AVS 2022-05-01 API
- Add `az vmware cluster list-zones`
- Add `--affinity-strength` and `--azure-hybrid-benefit-type` parameters to `az vmware placement-policy vm-host create`
- Add `--affinity-strength` and `--azure-hybrid-benefit-type` parameters to `az vmware placement-policy vm-host update`
- Add `--express-route-id` parameter to `az vmware authorization create`
- Add `vmware addon arc` command group
- Add `az vmware location check-trial-availability`
- Add `az vmware location check-quota-availability`
- Deprecate `az vmware location checktrialavailability`
- Deprecate `az vmware location checkquotaavailability`
- [BREAKING CHANGE] `az vmware private-cloud add-availability-zone` has been removed. Availability zone cannot be modified after private cloud creation
- [BREAKING CHANGE] `az vmware private-cloud delete-availability-zone` has been removed. Availability zone cannot be modified after private cloud creation.

## 4.1.0 (2022-07)

- Add `az vmware private-cloud enable-cmk-encryption`
- Add `az vmware private-cloud disable-cmk-encryption`
- Deprecate `az vmware private-cloud add-cmk-encryption`
- Deprecate `az vmware private-cloud delete-cmk-encryption`
- Add `--system-assigned` parameter to `az vmware private-cloud identity remove`

## 4.0.2 (2022-02)

- Update `az vmware datastore disk-pool-volume create` to only accept one argument for --mount-option

## 4.0.1 (2021-11)

- Fix publishing extension

## 4.0.0 (2021-11)

- Add `az vmware placement-policy` command group
- Add `az vmware vm` command group
- Updated `az vmware private-cloud create` with new Identity parameter
- Updated `az vmware private-cloud update` with new Identity parameter
- Add `az vmware private-cloud add-availability-zone`
- Add `az vmware private-cloud delete-availability-zone`
- Add `az vmware private-cloud add-cmk-encryption`
- Add `az vmware private-cloud delete-cmk-encryption`
- Add `az vmware private-cloud list-admin-credentials`
- Add `az vmware private-cloud add-identity-source`
- Add `az vmware private-cloud delete-identity-source`
- Add `az vmware private-cloud identity` command group
- Deprecate `az vmware private-cloud listadmincredentials`
- Deprecate `az vmware private-cloud addidentitysource`
- Deprecate `az vmware private-cloud deleteidentitysource`
- [BREAKING CHANGE] Add confirmation prompt to `az vmware private-cloud rotate-vcenter-password`
- [BREAKING CHANGE] Add confirmation prompt to `az vmware private-cloud rotate-nsxt-password`
- [BREAKING CHANGE] Add confirmation prompt to all delete commands

## 3.2.0 (2021-10)

- Add `az vmware workload-network dhcp` command group
- Add `az vmware workload-network dns-service` command group
- Add `az vmware workload-network dns-zone` command group
- Add `az vmware workload-network port-mirroring` command group
- Add `az vmware workload-network segment` command group
- Add `az vmware workload-network public-ip` command group
- Add `az vmware workload-network vm-group` command group
- Add `az vmware workload-network vm` command group
- Add `az vmware workload-network gateway` command group

## 3.1.0 (2021-08)

- Add `az vmware cloud-link` command group
- Add `az vmware script-cmdlet` command group
- Add `az vmware script-execution` command group
- Add `az vmware script-package` command group

## 3.0.0 (2021-07)

- [BREAKING CHANGE] `az vmware datastore create` has been removed. Please use `az vmware datastore netapp-volume create` or `az vmware datastore disk-pool-volume create` instead.

Other changes:

- Update to AVS 2021-06-01 API
- Add `az vmware private-cloud rotate-vcenter-password`
- Add `az vmware private-cloud rotate-nsxt-password`
- Add `az vmware addon` command group
- Add `az vmware addon hcx` command group to manage a HCX addon
- Add `az vmware addon srm` command group to manage a Site Recovery Manager (SRM) addon
- Add `az vmware addon vr` command group to manage a vSphere Replication (VR) addon
- Add `az vmware global-reach-connection` command group to manage Global Reach Connections

## 2.0.1 (2021-02)

- Update the minimum az cli version to 2.11.0 [#3045](https://github.com/Azure/azure-cli-extensions/issues/3045)

## 2.0.0 (2021-02)

This version has **breaking changes** for scripts.

- prompt for legal terms for `az vmware private-cloud create` [#2932](https://github.com/Azure/azure-cli-extensions/pull/2932)
  - scripts will need to add `--accept-eula` to avoid being prompted
- prompt to confirm for `az vmware private-cloud delete` [#2930](https://github.com/Azure/azure-cli-extensions/pull/2930)
  - scripts will need to add `--yes` to avoid being prompted

Other changes:

- update to AVS 2021-01-01-preview API [#2976](https://github.com/Azure/azure-cli-extensions/pull/2976)
- add az vmware datastore command group [#2998](https://github.com/Azure/azure-cli-extensions/pull/2998)

```
az vmware datastore --help

Group
    az vmware datastore : Commands to manage a datastore in a private cloud cluster.

Commands:
    create : Create a datastore in a private cloud cluster.
    delete : Delete a datastore in a private cloud cluster.
    list   : List datastores in a private cloud cluster.
    show   : Show details of a datastore in a private cloud cluster.
```

## 1.0.0 (2020-11-02)

- GA Release
- Moved to https://github.com/Azure/azure-cli-extensions

## 0.7.2 (2020-10-20)

- switches some code to use show_command to fix a pylint error [#44](https://github.com/Azure/az-vmware-cli/pull/44)

## 0.7.1 (2020-10-19)

- removed the preview flags [#43](https://github.com/Azure/az-vmware-cli/pull/43)

## 0.7.0 (2020-07-21)

Update to the 2020-03-20 API [#31](https://github.com/Azure/az-vmware-cli/pull/31)

Adds commands for managing ExpressRoute Circuit authorizations for a private cloud:

- az vmware authorization create
- az vmware authorization list
- az vvware authorization delete
- az vmware authorization show

Removes:

- az vmware private-cloud addauthorization
- az vmware private-cloud deleteauthorization
- az vmware checkquotaavailability

Adds:

- az vmware location checkquotaavailability
- az vmware location checktrialavailability

Add command for managing HCX Enterprise Sites for a private cloud:

- az vmware hcx-enterprise-site create
- az vmware hcx-enterprise-site list
- az vmware hcx-enterprise-site delete
- az vmware hcx-enterprise-site show

## 0.6.0 (2020-05-06)

- switch to Microsoft.AVS 2019-08-09-preview API [#35](https://github.com/Azure/az-vmware-cli/pull/35)
- vmware checkquotaavailability [#34](https://github.com/Azure/az-vmware-cli/pull/34)
  - example: az vmware checkquotaavailability --location northcentralus

## 0.2.0 (2019-07-16)

- initial preview release
- see archived [az-vmware-cli releases](https://github.com/Azure/az-vmware-cli/releases)
