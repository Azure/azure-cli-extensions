Microsoft Azure CLI 'guestconfig' Extension
==========================================

This package is for the 'guestconfig' extension.
i.e. 'az guestconfig'

# Azure CLI GuestConfiguration Extension #
Microsoft Azure CLI - Guest Configuration for Azure Resource Manager. Allows querying VM and ARC machines compliance statuses for initiatives (part of Azure Policy) of category "Guest configuration", compliance reasons, compliance status history. For more information, please visit: https://aka.ms/guestconfigcmdlets

### How to use ###
Install this extension using the below CLI command
```
az extension add --name guestconfig
```

### Included Features

#### Azure VM Guestconfiguration assignments:
    Query Azure VM guestconfiguration policy assignment information.

*Examples:*
```
az guestconfig guest-configuration-assignment show
    --name "{GuestConfigurationAssignment}"
    --resource-group "{ResourceGroup}"
    --vm-name "{VMName}"
```

```
az guestconfig guest-configuration-assignment list
    --resource-group "{ResourceGroup}"
    --vm-name "{VMName}"
```

#### Azure VM Guestconfiguration reports:
    Query Azure VM guestconfiguration policy reports information.

*Examples:*
```
az guestconfig guest-configuration-assignment-report show
    --guest-configuration-assignment-name "{GuestConfigurationAssignment}"
    --report-id "{ReportId}"
    --resource-group "{ResourceGroup}"
    --vm-name "{VMName}"
```

```
az guestconfig guest-configuration-assignment-report list
    --guest-configuration-assignment-name "{GuestConfigurationAssignment}"
    --resource-group "{ResourceGroup}"
    --vm-name "{VMName}"
```

#### ARC Hybrid Machine Guestconfiguration assignments:
    Query ARC Hybrid Machine guestconfiguration policy assignment information.

*Examples:*
```
az guestconfig guest-configuration-hcrp-assignment show
    --guest-configuration-assignment-name "{GuestConfigurationAssignment}"
    --resource-group "{ResourceGroup}"
    --machine-name "{MachineName}"
```

```
az guestconfig guest-configuration-hcrp-assignment list
    --resource-group "{ResourceGroup}"
    --machine-name "{MachineName}"
```

#### ARC Hybrid Machine Guestconfiguration reports:
    Query ARC Hybrid Machine guestconfiguration policy reports information.

*Examples:*
```
az guestconfig guest-configuration-hcrp-assignment-report show
    --guest-configuration-assignment-name "{GuestConfigurationAssignment}"
    --resource-group "{ResourceGroup}"
    --machine-name "{MachineName}"
    --report-id "{ReportId}"
```

```
az guestconfig guest-configuration-hcrp-assignment-report list
    --guest-configuration-assignment-name "{GuestConfigurationAssignment}"
    --resource-group "{ResourceGroup}"
    --machine-name "{MachineName}"
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.