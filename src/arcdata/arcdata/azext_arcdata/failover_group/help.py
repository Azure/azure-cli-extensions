# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long
helps[
    "sql instance-failover-group-arc"
] = """
    type: group
    short-summary: {short}
""".format(
    short="Manage Arc-enabled SQL managed instance Failover Groups."
)

# pylint: disable=line-too-long
helps[
    "sql instance-failover-group-arc create"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql instance-failover-group-arc create --name fogcr --shared-name sharedname1
            --mi sqlmi1 --role primary --partner-mi sqlmi2
            --partner-mirroring-url 10.20.5.20:970
            --partner-mirroring-cert-file ./sqlmi2.cer --use-k8s
        - name: {ex2}
          text: >
            az sql instance-failover-group-arc create --name fogcr 
            --mi sqlmi1 --resource-group primary-rg-name 
            --partner-mi sqlmi2 --partner-resource-group partner-rg-name
            --partner-sync-mode async
        - name: {ex3}
          text: >
            az sql instance-failover-group-arc create --name fogcr 
            --mi sqlmi1 --resource-group primary-rg-name 
            --partner-mi sqlmi2 --partner-resource-group partner-rg-name
            --partner-sync-mode async --primary-mirroring-url 21.10.6.30:6603
            --partner-mirroring-url 10.20.5.20:970
""".format(
    short="Create a failover group resource",
    long="Create an Arc-enabled SQL Managed Instance failover group resource to set up a "
    "distributed availability group.",
    ex1="Use the Kubernetes API to create a failover group resource between "
    "primary SQL managed instance sqlmi1 and partner SQL managed instance sqlmi2."
    "The partner mirroring endpoint and cert file are required.",
    ex2="Use Azure Resource Manager (ARM) to create a failover group resource.",
    ex3="Use ARM to create a failover group with custom mirroring URLs.",
)

# pylint: disable=line-too-long
helps[
    "sql instance-failover-group-arc update"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql instance-failover-group-arc update --name fogcr --role secondary --use-k8s
        - name: {ex2}
          text: >
            az sql instance-failover-group-arc update --name fogcr 
            --role secondary --mi sqlmi1 --resource-group rg-name
""".format(
    short="Update a failover group resource",
    long="Update an Arc-enabled SQL Managed Instance failover group resource to "
    "change the role of the distributed availability group.",
    ex1="Update a failover group resource to the secondary role from primary using the Kubernetes API.",
    ex2="Update a failover group resource using Azure Resource Manager.",
)

# pylint: disable=line-too-long
helps[
    "sql instance-failover-group-arc delete"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql instance-failover-group-arc delete --name fogcr --use-k8s
        - name: {ex2}
          text: >
            az sql instance-failover-group-arc delete --name fogcr --mi sqlmi1 -g rg-name
""".format(
    short="Delete an Arc-enabled SQL Managed Instance failover group.",
    ex1="Delete a failover group resource using the Kubernetes API.",
    ex2="Delete a failover group resource using Azure Resource Manager.",
)

helps[
    "sql instance-failover-group-arc show"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql instance-failover-group-arc show --name fogcr --use-k8s
        - name: {ex2}
          text: >
            az sql instance-failover-group-arc show --name fogcr1 --mi sqlmi1 -g rg-name
""".format(
    short="Show the details of a failover group resource.",
    ex1="Show the details of a failover group using the Kubernetes API.",
    ex2="Show the details of a failover group by querying Azure Resource Manager (ARM).",
)

helps[
    "sql instance-failover-group-arc list"
] = """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az sql instance-failover-group-arc list --k8s-namespace arcdata --use-k8s
        - name: {ex2}
          text: >
            az sql instance-failover-group-arc list --mi sqlmi1 -g rg-name
""".format(
    short="List all failover groups.",
    ex1="List all failover groups in a namespace using the Kubernetes API.",
    ex2="List all failover groups by querying Azure Resource Manager (ARM).",
)
