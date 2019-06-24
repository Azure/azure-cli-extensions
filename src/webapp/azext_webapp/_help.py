# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['webapp remote-connection'] = """
    type: group
    short-summary: Create a remote connection using a tcp tunnel to your web app
"""

helps['webapp remote-connection create'] = """
    type: command
    short-summary: Creates a remote connection using a tcp tunnel to your web app
"""

helps['webapp scan'] = """
    type: group
    short-summary: Holds group of commands which cater to webapp scans
"""

helps['webapp scan start-scan'] = """
    type: command
    short-summary: Starts the scan on the specified webapp files
"""

helps['webapp scan get-scan-result'] = """
    type: command
    short-summary: Get results of specified scan-id
"""

helps['webapp scan track-scan'] = """
    type: command
    short-summary: Track status of scan by providing scan-id
"""

helps['webapp scan get-all-scan-result'] = """
    type: command
    short-summary: Get details of all scans conducted on webapp, upto max scan limit set on the webapp
"""
