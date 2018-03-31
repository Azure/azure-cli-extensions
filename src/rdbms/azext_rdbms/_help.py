# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

#  pylint: disable=line-too-long


def add_helps(command_group, server_type):
    helps['{} server create'.format(command_group)] = """
                short-summary: Create a server.
                examples:
                    - name: Create a {0} server with only required paramaters in North Europe.
                      text: az {1} server create -l northeurope -g testgroup -n testsvr -u username -p password
                    - name: Create a {0} server with a Standard performance tier and 2 vcore in North Europe.
                      text: az {1} server create -l northeurope -g testgroup -n testsvr -u username -p password \\
                            --sku-name GP_Gen4_2
                    - name: Create a {0} server with all paramaters set.
                      text: az {1} server create -l northeurope -g testgroup -n testsvr -u username -p password \\
                            --sku-name B_Gen4_2 --ssl-enforcement Disabled \\
                            --storage-size 51200 --tags "key=value" --version {{server-version}}
                """.format(server_type, command_group)
    helps['{} server georestore'.format(command_group)] = """
                type: command
                short-summary: Georestore a server from backup.
                examples:
                    - name: Georestore 'testsvr' as 'testsvrnew' where 'testsvrnew' is in same resource group as 'testsvr'.
                      text: az {0} server georestore -g testgroup -n testsvrnew --source-server testsvr -l westus2
                    - name: Georestore 'testsvr2' to 'testsvrnew', where 'testsvrnew' is in the different resource group as the original server.
                      text: |
                        az {0} server georestore -g testgroup -n testsvrnew \\
                            -s "/subscriptions/${{SubID}}/resourceGroups/${{ResourceGroup}}/providers/Microsoft.DBfor{1}/servers/testsvr2" -l westus2 --sku-name GP_Gen5_2
                """.format(command_group, server_type)


add_helps("mysql", "MySQL")
add_helps("postgres", "PostgreSQL")
