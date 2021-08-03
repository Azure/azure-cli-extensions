# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['webapp scan'] = """
    type: group
    short-summary: Holds group of commands which cater to webapp scans. Currently available only for Linux based webapps.
"""

helps['webapp scan start'] = """
    type: command
    short-summary: Starts the scan on the specified webapp files in the wwwroot directory. It returns a JSON containing the ScanID, traking and results URL.
"""

helps['webapp scan show-result'] = """
    type: command
    short-summary: Get results of specified scan-id. This will fetch you the Scan log results of the specified scan-id.
"""

helps['webapp scan track'] = """
    type: command
    short-summary: Track status of scan by providing scan-id. You can track the status of the scan from [Starting, Success, Failed, TimeoutFailure, Executing]
"""

helps['webapp scan list-result'] = """
    type: command
    short-summary: Get details of all scans conducted on webapp, upto max scan limit set on the webapp This will get you the scan log results in addition to the scan status of each scan conducted on the webapp.
"""

helps['webapp scan stop'] = """
    type: command
    short-summary: Stops the current executing scan. Does nothing if no scan is executing.
"""
