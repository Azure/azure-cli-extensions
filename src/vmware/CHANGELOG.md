# Release History

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
