# Release History

## 2.0.0 (TBD)

- prompt for legal terms in private-cloud create [#2932](https://github.com/Azure/azure-cli-extensions/pull/2932)
- update to AVS 2021-01-01-preview API

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