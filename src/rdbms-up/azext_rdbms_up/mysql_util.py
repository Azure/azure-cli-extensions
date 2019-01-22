# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=too-few-public-methods
class ClientType:
    '''
    Types of MySQL clients whose connection strings we can generate.
    '''

    mysql_cmd = 'mysql_cmd'
    ado_net = 'ado.net'
    jdbc = 'jdbc'
    nodejs = 'node.js'
    php = 'php'
    python = 'python'
    ruby = 'ruby'
    odbc = 'odbc'
