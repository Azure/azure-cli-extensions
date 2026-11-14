# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from knack.help_files import helps

# ------------------------------------------------------------------------------
# Server Commands
# ------------------------------------------------------------------------------

# pylint: disable=line-too-long
helps["postgres server-arc"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Manage Azure Arc enabled PostgreSQL servers."
    )
)

helps["postgres server-arc create"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc create -n pg1 --k8s-namespace namespace --use-k8s
""".format(
        short="Create an Azure Arc enabled PostgreSQL server.",
        long="To set the password of the server, please set the environment variable AZDATA_PASSWORD",
        ex1="Create an Azure Arc enabled PostgreSQL server.",
    )
)

helps["postgres server-arc restore"] = (
    """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc restore -n <to-pg> --source-server <from-pg> --k8s-namespace namespace --use-k8s
""".format(
        short="Restore an Azure Arc enabled PostgreSQL server from backup from another server.",
        long="To set the password of the server, please set the environment variable AZDATA_PASSWORD",
        ex1="Restore an Azure Arc enabled PostgreSQL server.",
    )
)

helps["postgres server-arc update"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc update --path ./spec.json -n pg1 --k8s-namespace namespace --use-k8s
        - name: {ex2}
          text: >
            az postgres server-arc update -n pg1 --extensions 'pgaudit,pg_partman' --k8s-namespace namespace --use-k8s
        - name: {ex3}
          text: >
            az postgres server-arc update -n pg1 --extensions "''" --k8s-namespace namespace --use-k8s
""".format(
        short="Update the configuration of an Azure Arc enabled PostgreSQL server.",
        ex1="Update the configuration of an Azure Arc enabled PostgreSQL server.",
        ex2="Enable extensions for an existing Azure Arc enabled PostgreSQL server.",
        ex3="Remove extensions from an Azure Arc enabled PostgreSQL server.",
    )
)

helps["postgres server-arc delete"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc delete -n pg1 --k8s-namespace namespace --use-k8s
""".format(
        short="Delete an Azure Arc enabled PostgreSQL server.",
        ex1="Delete an Azure Arc enabled PostgreSQL server.",
    )
)

helps["postgres server-arc show"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc show -n pg1 --k8s-namespace namespace --use-k8s
""".format(
        short="Show the details of an Azure Arc enabled PostgreSQL server.",
        ex1="Show the details of an Azure Arc enabled PostgreSQL server.",
    )
)

helps["postgres server-arc list"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc list --k8s-namespace namespace --use-k8s
""".format(
        short="List Azure Arc enabled PostgreSQL server.",
        ex1="List Azure Arc enabled PostgreSQL server.",
    )
)

helps["postgres server-arc endpoint"] = (
    """
    type: group
    short-summary: {short}
""".format(
        short="Manage Azure Arc enabled PostgreSQL server endpoints."
    )
)

helps["postgres server-arc endpoint list"] = (
    """
    type: command
    short-summary: {short}
    examples:
        - name: {ex1}
          text: >
            az postgres server-arc endpoint list --name postgres01
            --k8s-namespace namespace --use-k8s
""".format(
        short="List Azure Arc enabled PostgreSQL server endpoints.",
        ex1="List Azure Arc enabled PostgreSQL server endpoints.",
    )
)
