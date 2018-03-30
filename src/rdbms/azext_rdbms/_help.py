# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

#  pylint: disable=line-too-long


def add_helps(command_group, server_type):
    helps['{} server georestore'.format(command_group)] = """
                type: command
                short-summary: Georestore a server from backup.
                examples:
                    - name: Georestore 'testsvr' as 'testsvrnew'.
                      text: az {0} server georestore -g testgroup -n testsvrnew --source-server testsvr -l westus2"
                    - name: Georestore 'testsvr2' to 'testsvrnew', where 'testsvrnew' is in the same resource group as the original server but in a different location.
                      text: |
                        az {0} server georestore -g testgroup -n testsvrnew \\
                            -s "/subscriptions/${{SubID}}/resourceGroups/${{ResourceGroup}}/providers/Microsoft.DBfor{1}/servers/testsvr2" -l westus2 --sku-name GP_Gen5_2 "
                """.format(command_group, server_type)


add_helps("mysql", "MySQL")
add_helps("postgres", "PostgreSQL")
