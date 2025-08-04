# Azure CLI offazure Extension #
This package is for the 'offazure' extension, i.e. 'az offazure', which serves as the on-premise resources assessment tool for [Azure Migrate](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name offazure
```

### Included Features ###
#### Manage Hyper-V on-premise resources ####
```
Group
    az offazure hyperv : Manage Hyper-V on-premise resources.
Subgroups:
    cluster        : Manage Hyper-V cluster.
    host           : Manage Hyper-V host.
    machine        : Manage Hyper-V machine.
    run-as-account : Manage Hyper-V run-as-account.
    site           : Manage Hyper-V site.
```
```
az offazure hyperv cluster : Manage Hyper-V cluster.
    list : Get all clusters on the on-premise site.
    show : Get the details of a Hyper-V cluster.

az offazure hyperv host : Manage Hyper-V host.
    list : Get all hosts on the on-premise site.
    show : Get the details of a Hyper-V host.

az offazure hyperv machine : Manage Hyper-V machine.
    list : List all machines on the on-premise site.
    show : Get the details of a machine.

az offazure hyperv run-as-account : Manage Hyper-V run-as-account.
    list : List all run-as-accounts on the on-premise site.
    show : Get the details of a run-as-account.

az offazure hyperv site : Manage Hyper-V site.
    create : Create a Hyper-V site.
    delete : Delete a Hyper-V site.
    show   : Get the details of a site.
```
#### Manage VMware on-premise resources ####
```
Group
    az offazure vmware : Manage VMware on-premise resources.
Subgroups:
    machine        : Manage VMware machine.
    run-as-account : Manage VMware run-as-account.
    site           : Manage VMware site.
    vcenter        : Manage VMware vCenter.
```
```
az offazure vmware machine : Manage VMware machine.
    list : List all machines on the on-premise site.
    show : Get the details of a machine.

az offazure vmware run-as-account : Manage VMware run-as-account.
    list : List all run-as-accounts on the on-premise site.
    show : Get the details of a run-as-account.

az offazure vmware site : Manage VMware site.
    create : Create a site for VMware resources.
    delete : Delete a VMware site.
    show   : Get the details of a VMware site.

az offazure vmware vcenter : Manage VMware vCenter.
    list : List all vCenters on the on-premise site.
    show : Get the details of a vCenter.
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.