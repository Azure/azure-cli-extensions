Microsoft Azure CLI 'mesh' Command Module
==============================================================
Official doc https://docs.microsoft.com/en-us/azure/service-fabric-mesh/
Commands to manage Azure Service Fabric Mesh resources
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::
    Group
        az mesh: Manage Azure Service Fabric Mesh Resources.

    Subgroups:
        app             : Manage Service Fabric Mesh applications.
        code-package-log: Examine the logs for a codepackage.
        deployment      : Manage Service Fabric Mesh deployments.
        network         : Manage networks.
        service         : Manage Service Fabric Mesh services.
        service-replica : Manage Service Fabric Mesh service replicas.
        volume          : Manage volumes.


Commands to create an application
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

-Command
    az mesh deployment create: Create a Service Fabric Mesh application.

-Arguments
     --resource-group -g [Required]: Name of resource group. You can configure the default group
                                    using `az configure --defaults group=<name>`.
     --mode
     --name -n                     : The deployment name. Default to template file base name.
     --no-wait                     : Do not wait for the long-running operation to finish.
     --parameters
     --template-file               : The full file path of creation template.
     --template-uri                : The full file path of creation template on a http or https link.

-Global Arguments
     --debug                       : Increase logging verbosity to show all debug logs.
     --help -h                     : Show this help message and exit.
     --output -o                   : Output format.  Allowed values: json, jsonc, table, tsv.
                                    Default: json.
     --query                       : JMESPath query string. See http://jmespath.org/ for more
                                    information and examples.
     --subscription                : Name or ID of subscription. You can configure the default
                                    subscription using `az account set -s NAME_OR_ID`".
     --verbose                     : Increase logging verbosity. Use --debug for full debug logs.

-Examples
     Create a deployment with a template file on the remote.
         az mesh deployment create --resource-group mygroup --template-uri
         https://seabreezequickstart.blob.core.windows.net/templates/quickstart/sbz_rp.linux.json

     Create a deployment with a template file on local disk.
         az mesh deployment create --resource-group mygroup --template-file ./appTemplate.json
