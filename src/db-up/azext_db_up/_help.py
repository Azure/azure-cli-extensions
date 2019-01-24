# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['mysql up'] = """
    type: command
    short-summary: Experimental command to create an Azure Database for MySQL server and configure a firewall rule.
    examples:
        - name: Ensure that a Azure Database for MySQL server is up and running and configured for immediate use.
          text: az mysql up
        - name: To override default names, provide parameters indicating desired values/existing resources.
          text: az mysql up -g MyResourceGroup -s MyServer -d MyDatabase -u MyUsername -p MyPassword
"""
