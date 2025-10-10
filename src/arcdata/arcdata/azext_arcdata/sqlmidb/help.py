# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.help_files import helps

helps[
    "sql midb-arc"
] = """
    type: group
    short-summary: {short}
""".format(
    short="Manage databases for Azure Arc-enabled SQL managed instances."
)

helps[
    "sql midb-arc restore"
] = """
    type: command
    short-summary: {short}
    long-summary: {long}
    examples:
        - name: {ex1}
          text: >
            az sql midb-arc restore --managed-instance sqlmi1 --name mysourcedb
             --dest-name mynewdb --time "2021-10-20T05:34:22Z" --k8s-namespace
             arc --use-k8s --dry-run
""".format(
    short=" Restore a database to an Azure Arc enabled SQL managed instance.",
    long="",
    ex1="Ex 1 - Restore a database using Point in time restore.",
)
