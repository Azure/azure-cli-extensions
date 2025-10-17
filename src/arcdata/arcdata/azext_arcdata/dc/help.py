# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.help_files import helps
from azext_arcdata.core.util import get_environment_list_by_target

"""Help documentation for `control` commands."""


helps["arcdata"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Commands for using Azure Arc-enabled data services."
    )
)

helps["arcdata dc"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Create, delete, and manage data controllers."
    )
)

helps["arcdata dc create"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc create --name dc-name
            --connectivity-mode direct --resource-group rg-name
            --location eastasia --subscription subscription
            --custom-location arc-cl
        - name: {ex2}
          text: >
            az arcdata dc create --name dc-name
            --subscription subscription --resource-group rg-name
            --cluster-name arc-cluster --connectivity-mode direct
            --custom-location arc-cl
""".format(
        short="Create data controller.",
        long="Create data controller - kube config is required on your system "
        "along with credentials for the monitoring dashboards provided by the "
        "following environment variables - AZDATA_LOGSUI_USERNAME and "
        "AZDATA_LOGSUI_PASSWORD for Logs Dashboard, and "
        "AZDATA_METRICSUI_USERNAME and AZDATA_METRICSUI_PASSWORD for Metrics "
        "Dashboard. Alternatively AZDATA_USERNAME and AZDATA_PASSWORD will be "
        "used as a fallback if either sets of environment variables are "
        "missing. When using ARM-targeted arguments, the following optional environment variables are "
        "also possible - WORKSPACE_ID for Log Analytics Workspace ID and "
        "WORKSPACE_SHARED_KEY for the Log Analytics Primary Key.",
        ex1="Deploy an Arc data controller through Azure Resource Manager (direct connectivity mode only).",
        ex2="Deploy an Arc data controller to a given Arc-enabled Kubernetes cluster through ARM "
        "(direct connectivity mode only). This command will deploy the Arc data services extension "
        "and custom location if they do not exist already.",
    )
)

helps["arcdata dc upgrade"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc upgrade --k8s-namespace arc --use-k8s
""".format(
        short="Upgrade data controller.",
        long="Upgrade data controller to the desired-version specified.  If desired-version is not specified, an attempt to upgrade to the latest version will be made. "
        "If you are unsure of the desired version, you may use the list-upgrades command to view available versions, or use the --dry-run argument to show which version would be used",
        ex1="Data controller upgrade.",
    )
)

helps["arcdata dc update"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Update data controller properties."
    )
)

helps["arcdata dc update"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc update --auto-upload-logs true --name dc-name --resource-group rg-name
        - name: {ex2}
          text: >
            az arcdata dc update --auto-upload-metrics true --name dc-name --resource-group rg-name
""".format(
        short="Update data controller.",
        long="Updates the datacontroller to enable/disable auto-uploading logs and metrics",
        ex1="Enable auto-uploading of logs through Azure Resource Manager (ARM).",
        ex2="Enable auto-uploading of metrics through ARM.",
    )
)


helps["arcdata dc list-upgrades"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc list-upgrades --k8s-namespace namespace --use-k8s
""".format(
        short="List available upgrade versions.",
        long="Attempts to list versions that are available in the docker image registry for upgrade. "
        "- kube config is required on your system "
        "along with the following environment variables {0}.".format(
            get_environment_list_by_target("cluster")
        ),
        ex1="Data controller upgrade list.",
    )
)

helps["arcdata dc delete"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc delete --name dc-name --k8s-namespace arc --use-k8s
        - name: {ex2}
          text: >
            az arcdata dc delete --name dc-name --resource-group rg-name
""".format(
        short="Delete data controller.",
        long="Delete data controller - kube config is required on your system.",
        ex1="Delete a data controller through the Kubernetes API.",
        ex2="Delete a data controller through Azure Resource Manager (ARM).",
    )
)

helps["arcdata dc list"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc list --resource-group rg-name
        - name: {ex2}
          text: >
            az arcdata dc list --subscription subscriptionId
""".format(
        short="List Azure Arc data controllers by resource group or subscription.",
        ex1="Lists all Arc data controllers in the given resource group.",
        ex2="Lists all Arc data controllers in the given subscription.",
    )
)

helps["arcdata dc endpoint"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Endpoint commands."
    )
)

helps["arcdata dc endpoint list"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc endpoint list --k8s-namespace namespace
""".format(
        short="List the data controller endpoint.",
        long="List the data controller endpoint.",
        ex1="Lists all available data controller endpoints.",
    )
)

helps["arcdata dc status"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Status commands."
    )
)

helps["arcdata dc status show"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc status show --k8s-namespace namespace --use-k8s
        - name: {ex2}
          text: >
            az arcdata dc status show --resource-group resource-group
""".format(
        short="Show the status of the data controller.",
        long="Show the status of the data controller.",
        ex1="Show the status of the data controller in a particular kubernetes "
        "namespace.",
        ex2="Show the status of a directly connected data controller in a "
        "particular resource group.",
    )
)

helps["arcdata dc config"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Configuration commands."
    )
)

helps["arcdata dc config init"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc config init
        - name: {ex2}
          text: >
            az arcdata dc config init --source azure-arc-kubeadm --path custom
""".format(
        short="Initialize a data controller configuration profile that can be used with `az arcdata dc create`.",
        long="Initialize a data controller configuration profile that can be used with `az arcdata dc create`. "
        "The specific source of the configuration profile can be specified in the arguments.",
        ex1="Guided data controller config init experience - you will receive prompts for needed values.",
        ex2="arcdata dc config init with arguments, creates a configuration profile of aks-dev-test in ./custom.",
    )
)

helps["arcdata dc config list"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc config list
        - name: {ex2}
          text: >
            az arcdata dc config list --config-profile aks-dev-test
""".format(
        short="List available configuration profile choices.",
        long="List available configuration profile choices for use in `arcdata dc config init`",
        ex1="Shows all available configuration profile names.",
        ex2="Shows json of a specific configuration profile.",
    )
)

helps["arcdata dc config add"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc config add --path custom/control.json
            --json-values 'spec.storage={val1}'
""".format(
        short="Add a value for a json path in a config file.",
        long="Add the value at the json path in the config file. All examples "
        "below are given in Bash.  If using another command line, you may need to escape"
        "quotations appropriately.  Alternatively, you may use the patch file functionality.",
        ex1="Add data controller storage.",
        val1='{"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}',
    )
)

helps["arcdata dc config remove"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc config remove --path custom/control.json
            --json-path '.spec.storage'
""".format(
        short="Remove a value for a json path in a config file.",
        long="Remove the value at the json path in the config file.  All examples "
        "below are given in Bash.  If using another command line, you may need to escape"
        "quotations appropriately.  Alternatively, you may use the patch file functionality.",
        ex1="Ex 1 - Remove data controller storage.",
    )
)

helps["arcdata dc config replace"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc config replace --path custom/control.json
            --json-values '$.spec.endpoints[?(@.name=="Controller")].port=30080'
        - name: {ex2}
          text: >
            az arcdata dc config replace --path custom/control.json
            --json-values '{val2}'
""".format(
        short="Replace a value for a json path in a config file.",
        long="Replace the value at the json path in the config file.  All examples"
        "below are given in Bash.  If using another command line, you may need to escape"
        "quotations appropriately.  Alternatively, you may use the patch file functionality.",
        ex1="Ex 1 - Replace the port of a single endpoint (Data Controller Endpoint).",
        ex2="Ex 2 - Replace data controller storage.",
        val2='spec.storage={"accessMode":"ReadWriteOnce","className":"managed-premium","size":"10Gi"}',
    )
)

helps["arcdata dc config patch"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc config patch --path custom/control.json --patch ./patch.json

                Patch File Example (patch.json):
                    {patch1}
        - name: {ex2}
          text: >
            az arcdata dc config patch --path custom/control.json --patch ./patch.json

                Patch File Example (patch.json):
                    {patch2}
""".format(
        short="Patch a config file based on a json patch file.",
        long="Patch the config file according to the given patch file. "
        "Consult http://jsonpatch.com/ for a better understanding of how the paths should be composed. "
        "The replace operation can use conditionals in its path due to the jsonpath library https://jsonpath.com/. "
        'All patch json files must start with a key of "patch" that has an array of patches with their '
        "corresponding op (add, replace, remove), path, and value. "
        'The "remove" op does not require a value, just a path. '
        "See the examples below.",
        ex1="Ex 1 - Replace the port of a single endpoint (Data Controller Endpoint) with patch file.",
        patch1='{"patch":[{"op":"replace","path":"$.spec.endpoints[?(@.name==\'Controller\')].port",'
        '"value":30080}]}',
        ex2="Ex 2 - Replace data controller storage with patch file.",
        patch2='{"patch":[{"op":"replace","path":".spec.storage",'
        '"value":{"accessMode":"ReadWriteMany","className":"managed-premium","size":"10Gi"}}]}',
    )
)

helps["arcdata dc debug"] = (
    """
    type: group
    short-summary: {short}.
""".format(
        short="Debug data controller."
    )
)

helps["arcdata dc debug copy-logs"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
        short="Copy logs.",
        long="Copy the debug logs from the data controller - Kubernetes configuration is required on your system.",
    )
)

helps["arcdata dc debug dump"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
        short="Trigger memory dump.",
        long="Trigger memory dump and copy it out from container - Kubernetes configuration is required on your system.",
    )
)

helps["arcdata dc debug restore-controldb-snapshot"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc debug restore-controldb-snapshot -k arc-data-services -f /path/to/backup/controller-1675653451.bak
        - name: {ex2}
          text: >
            az arcdata dc debug restore-controldb-snapshot -k arc-data-services -f C:\\path\\to\\backup\\controller-1675653451.bak
""".format(
        short="Restores a unique copy of ControlDB from backup - for troubleshooting purposes only.",
        long="Restores a COPY_ONLY backup of ControlDB under a unique name for troubleshooting - Kubernetes configuration is required on your system.",
        ex1="Linux - Restore a backup taken from a previously run 'arcdata dc debug copy-logs' command.",
        ex2="Windows - Restore a backup taken from a previously run 'arcdata dc debug copy-logs' command.",
    )
)

helps["arcdata dc debug controldb-cdc"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata dc debug controldb-cdc -k arc-data-services --enable true --retention-hours 4
        - name: {ex2}
          text: >
            az arcdata dc debug controldb-cdc -k arc-data-services --enable false
""".format(
        short="Enable/disable CDC on Data Controller Database and Tables - for troubleshooting purposes only.",
        long="Enable/Disable Change Data Capture for 'controller' Database and supported tables with configurable retention hours.",
        ex1="Enables Change Data Capture with 4 hours of retention.",
        ex2="Disables Change Data Capture.",
    )
)

helps["arcdata dc export"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
        short="Export metrics, logs or usage.",
        long="Export metrics, logs or usage to a file.",
    )
)

helps["arcdata dc upload"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
""".format(
        short="Upload exported data file.",
        long="Upload data file exported from a data controller to Azure.",
    )
)

helps["arcdata resource-kind"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Resource-kind commands to define and template custom resources on your cluster."
    )
)

helps["arcdata resource-kind list"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az arcdata resource-kind list
""".format(
        short="List the available custom resource kinds for Arc that can be defined and created.",
        long="List the available custom resource kinds for Arc that can be defined and created. After listing, you"
        " can proceed to getting the template file needed to define or create that custom resource.",
        ex1="Example command for listing the available custom resource kinds for Arc.",
    )
)

helps["arcdata resource-kind get"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata resource-kind get --kind SqlManagedInstance
""".format(
        short="Get the Arc resource-kind's template file.",
        ex1="Example command for getting an Arc resource-kind's CRD template file.",
    )
)
