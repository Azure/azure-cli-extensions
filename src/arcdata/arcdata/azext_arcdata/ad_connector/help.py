# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.help_files import helps

helps["arcdata ad-connector"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Manage Active Directory authentication for Azure Arc data services."
    )
)

helps["arcdata ad-connector create"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata ad-connector create
            --name arcadc 
            --k8s-namespace arc 
            --realm CONTOSO.LOCAL 
            --account-provisioning manual
            --primary-ad-dc-hostname azdc01.contoso.local 
            --secondary-ad-dc-hostnames "azdc02.contoso.local, azdc03.contoso.local" 
            --netbios-domain-name CONTOSO 
            --dns-domain-name contoso.local 
            --nameserver-addresses 10.10.10.11,10.10.10.12,10.10.10.13 
            --dns-replicas 2 
            --prefer-k8s-dns false 
            --use-k8s
        - name: {ex2}
          text: >
            az arcdata ad-connector create 
            --name arcadc
            --resource-group rg-name
            --data-controller-name dc-name
            --realm CONTOSO.LOCAL 
            --account-provisioning manual
            --primary-ad-dc-hostname azdc01.contoso.local 
            --secondary-ad-dc-hostnames "azdc02.contoso.local, azdc03.contoso.local" 
            --netbios-domain-name CONTOSO 
            --dns-domain-name contoso.local 
            --nameserver-addresses 10.10.10.11,10.10.10.12,10.10.10.13 
            --dns-replicas 2 
            --prefer-k8s-dns false
""".format(
        short="Create a new Active Directory connector.",
        ex1="Ex 1 - Deploy a new Active Directory connector using the Kubernetes API.",
        ex2="Ex 2 - Deploy a new Active Directory connector through Azure Resource Manager (ARM).",
    )
)

helps["arcdata ad-connector update"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata ad-connector update
            --name arcadc 
            --k8s-namespace arc 
            --primary-ad-dc-hostname azdc01.contoso.local
            --secondary-ad-dc-hostname "azdc02.contoso.local, azdc03.contoso.local" 
            --nameserver-addresses 10.10.10.11,10.10.10.12,10.10.10.13
            --dns-replicas 2 
            --prefer-k8s-dns false 
            --use-k8s
        - name: {ex2}
          text: >
            az arcdata ad-connector update
            --name arcadc
            --resource-group rg-name
            --data-controller-name dc-name
            --primary-ad-dc-hostname azdc01.contoso.local
            --secondary-ad-dc-hostname "azdc02.contoso.local, azdc03.contoso.local"
            --nameserver-addresses 10.10.10.11,10.10.10.12,10.10.10.13
            --dns-replicas 2
            --prefer-k8s-dns false
""".format(
        short="Update the settings of an existing Active Directory connector.",
        ex1="Ex 1 - Update an existing Active Directory connector using the Kubernetes API.",
        ex2="Ex 2 - Update an existing Active Directory connector through Azure Resource Manager (ARM).",
    )
)

helps["arcdata ad-connector delete"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata ad-connector delete
            --name arcadc
            --k8s-namespace arc 
            --use-k8s
        - name: {ex2}
          text: >
            az arcdata ad-connector delete
            --name arcadc
            --resource-group rg-name 
            --data-controller-name dc-name
""".format(
        short="Delete an existing Active Directory connector.",
        ex1="Ex 1 - Delete an existing Active Directory connector using the Kubernetes API.",
        ex2="Ex 2 - Delete an existing Active Directory connector through Azure Resource Manager (ARM).",
    )
)

helps["arcdata ad-connector show"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata ad-connector show
            --name arcadc
            --k8s-namespace arc
            --use-k8s
        - name: {ex2}
          text: >
            az arcdata ad-connector show
            --name arcadc
            --resource-group rg-name
            --data-controller-name dc-name
""".format(
        short="Get the details of an existing Active Directory connector.",
        ex1="Ex 1 - Get an existing Active Directory connector using the Kubernetes API.",
        ex2="Ex 2 - Get an existing Active Directory connector by querying Azure Resource Manager (ARM).",
    )
)

helps["arcdata ad-connector list"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az arcdata ad-connector list
            --k8s-namespace arc
            --use-k8s
        - name: {ex2}
          text: >
            az arcdata ad-connector list
            --resource-group rg-name
            --data-controller-name dc-name
""".format(
        short="List all Active Directory connectors.",
        ex1="Ex 1 - List all Active Directory connectors "
        "in a given Kubernetes namespace using the Kubernetes API.",
        ex2="Ex 2 - List all Active Directory connectors "
        "associated with a given Arc data controller by querying Azure Resource Manager (ARM).",
    )
)
