# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long
helps[
    "sql mi-arc"
] = """
    type: group
    short-summary: {short}
""".format(
    short="Manage Azure Arc-enabled SQL managed instances."
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc endpoint"
] = """
    type: group
    short-summary: {short}
""".format(
    short="View and manage SQL endpoints."
)

helps[
    "sql mi-arc endpoint list"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc endpoint list -n sqlmi1
""".format(
    short="List the SQL endpoints.",
    ex1="List the endpoints for a SQL managed instance.",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc create"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc create -n sqlmi1 --k8s-namespace arc --use-k8s
        - name: {ex2}
          text: >
            az sql mi-arc create -n sqlmi2 --replicas 3 --k8s-namespace arc --use-k8s
        - name: {ex3}
          text: >
            az sql mi-arc create --name sqlmi3 --resource-group rg-name --custom-location arc-cl
        - name: {ex4}
          text: >
            az sql mi-arc create --name contososqlmi --k8s-namespace arc
            --ad-connector-name arcadc --ad-account-name arcuser
            --keytab-secret arcuser-keytab-secret
            --primary-dns-name contososqlmi-primary.contoso.local
            --primary-port-number 8143 --use-k8s
""".format(
    short="Create a SQL managed instance.",
    long="To set the password of the SQL managed instance, set the environment "
    "variable AZDATA_PASSWORD",
    ex1="Create a SQL managed instance through the Kubernetes API.",
    ex2="Create a SQL managed instance with 3 replicas in HA scenario through the Kubernetes API.",
    ex3="Create a SQL managed instance through Azure Resource Manager (ARM).",
    ex4="Create a SQL managed instance with Active Directory authentication through the Kubernetes API.",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc update"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc update --path ./spec.json -n sqlmi1 --use-k8s
""".format(
    short="Update the configuration of a SQL managed instance.",
    ex1="Update the configuration of a SQL managed instance.",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc delete"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc delete --name sqlmi1 --k8s-namespace arc --use-k8s
        - name: {ex2}
          text: >
            az sql mi-arc delete --name sqlmi1 --resource-group rg-name
""".format(
    short="Delete a SQL managed instance.",
    ex1="Delete a SQL managed instance through the Kubernetes API.",
    ex2="Delete a SQL managed instance through Azure Resource Manager (ARM).",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc show"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc show --name sqlmi1 --k8s-namespace arc --use-k8s
        - name: {ex2}
          text: >
            az sql mi-arc show --name sqlmi1 --resource-group rg-name
""".format(
    short="Show the details of a SQL managed instance.",
    ex1="Show the details of a SQL Managed Instance using the Kubernetes API.",
    ex2="Show the details of a SQL Managed Instance by querying Azure Resource Manager (ARM).",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc get-mirroring-cert"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc get-mirroring-cert -n sqlmi1 --cert-file fileName1
""".format(
    short="Retrieve certificate of availability group mirroring endpoint from "
    "sql mi and store in a file.",
    ex1="Retrieve certificate of availability group mirroring endpoint from "
    "sqlmi1 and store in file fileName1",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc upgrade"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc upgrade -n sqlmi1 -k arc --desired-version v1.1.0 --use-k8s
""".format(
    short="Upgrade SQL managed instance.",
    long="Upgrade SQL managed instance to the desired-version specified.  If "
    "desired-version is not specified, the data controller version will "
    "be used.",
    ex1="Upgrade SQL managed instance.",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc list"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc list --use-k8s
""".format(
    short="List SQL managed instances.", ex1="List SQL managed instances."
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc config"
] = """
    type: group
    short-summary: {short}
""".format(
    short="Configuration commands."
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc config init"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc config init --path ./template
""".format(
    short="Initialize the CRD and specification files for a SQL managed "
    "instance.",
    ex1="Initialize the CRD and specification files for a SQL managed "
    "instance.",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc config add"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc config add --path custom/spec.json
            --json-values 'spec.storage={val1}'
""".format(
    short="Add a value for a json path in a config file.",
    long="Add the value at the json path in the config file.  All examples "
    "below are given in Bash.  If using another command line, you may "
    "need to escape quotations appropriately.  Alternatively, you may use "
    "the patch file functionality.",
    ex1="Ex 1 - Add storage.",
    val1='{"accessMode":"ReadWriteOnce","className":"managed-premium",'
    '"size":"10Gi"}',
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc config remove"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc config remove --path custom/spec.json
            --json-path '.spec.storage'
""".format(
    short="Remove a value for a json path in a config file.",
    long="Remove the value at the json path in the config file. All examples "
    "below are given in Bash. If using another command line, you may need "
    "to escape quotations appropriately. Alternatively, you may use the "
    "patch file functionality.",
    ex1="Ex 1 - Remove storage.",
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc config replace"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc config replace --path custom/spec.json
            --json-values '$.spec.endpoints[?(@.name=="Controller")].port=30080'
        - name: {ex2}
          text: >
            az sql mi-arc config replace --path custom/spec.json
            --json-values '{val2}'
""".format(
    short="Replace a value for a json path in a config file.",
    long="Replace the value at the json path in the config file.  All examples "
    "below are given in Bash.  If using another command line, you may "
    "need to escape quotations appropriately.  Alternatively, you may use "
    "the patch file functionality.",
    ex1="Ex 1 - Replace the port of a single endpoint.",
    ex2="Ex 2 - Replace storage.",
    val2='spec.storage={"accessMode":"ReadWriteOnce","className":'
    '"managed-premium","size":"10Gi"}',
)

# pylint: disable=line-too-long
helps[
    "sql mi-arc config patch"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            {cmd}

                Patch File Example (patch.json):
                    {patch1}
        - name: {ex2}
          text: >
            {cmd}

                Patch File Example (patch.json):
                    {patch2}
""".format(
    short="Patch a config file based on a json patch file.",
    long="Patch the config file according to the given patch file. Consult "
    "http://jsonpatch.com/ for a better understanding of how the paths "
    "should be composed. The replace operation can use conditionals in "
    "its path due to the jsonpath library https://jsonpath.com/. All patch "
    "json files must start with a key of `patch` that has an array of "
    "patches with their corresponding op (add, replace, remove), path, "
    "and value. The `remove` op does not require a value, just a path. See "
    "the examples below.",
    ex1="Ex 1 - Replace the port of a single endpoint with patch file.",
    cmd="az sql mi-arc config patch --path custom/spec.json "
    "--patch ./patch.json",
    patch1='{"patch":[{"op":"replace","path":"$.spec.endpoints'
    '[?(@.name==\'Controller\')].port","value":30080}]}',
    ex2="Ex 2 - Replace storage with patch file.",
    patch2='{"patch":[{"op":"replace","path":".spec.storage","value":{'
    '"accessMode":"ReadWriteMany","className":"managed-premium",'
    '"size":"10Gi"}}]}',
)

helps[
    "sql mi-arc reprovision-replica"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql mi-arc reprovision-replica -n sqlmi1-1 --use-k8s --k8s-namespace namespace
""".format(
    short="Reprovision a replica in a SQL managed instance.",
    long="Reprovision a replica in a SQL managed instance. "
    "This resets all the data in that instance and reseeds it from the primary instance.",
    ex1="Ex 1 - Reprovision replica 1 of SQL managed instance sqlmi1.",
)
