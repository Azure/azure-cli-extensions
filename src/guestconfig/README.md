Microsoft Azure CLI 'guestconfig' Extension
==========================================

This package is for the 'guestconfig' extension.
i.e. 'az guestconfig'

## Azure CLI Guest Configuration Extension ##

Azure Policy Guest Configuration provides auditing Azure virtual machines
and Arc connected servers.
The commands below return compliance status, detailed compliance reasons,
and compliance status history.
For more information, please visit: https://aka.ms/gcpol.

### How to use ###

Install this extension using the below CLI command
```
az extension add --name guestconfig
```

### Included Features

#### Azure Policy Guest Configuration assignments:

Provide details about the Guest Configuration assignments that have been created.
These Azure resources represent each of the scenarios
that will be audited inside the Azure virtual machine.

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

#### Azure Policy Guest Configuration reports:

Returns detailed compliance reports
from Guest Configuration for Azure virtual machines.
The detailed reports include setting-by-setting information collected
inside the machine that determines whether
the Azure Policy is compliant or not-compliant.

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

#### ARC Hybrid Machine Guest Configuration assignments:

Provide details about the Guest Configuration assignments that have been created.
These Azure resources represent each of the scenarios
that will be audited inside the Arc connected server.

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

#### ARC Hybrid Machine Guest Configuration reports:

Returns detailed compliance reports
from Guest Configuration for Arc connected servers.
The detailed reports include setting-by-setting information collected
inside the machine that determines whether
the Azure Policy is compliant or not-compliant.

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