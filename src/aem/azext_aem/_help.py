# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['vm aem'] = """
    type: group
    short-summary: Manage Azure Enhanced Monitoring Extension for SAP
"""

helps['vm aem set'] = """
    type: command
    short-summary: Configure Azure Enhanced Monitoring Extension
    long-summary: It can take up to 15 minutes for the monitoring data to appear in the SAP system
"""

helps['vm aem delete'] = """
    type: command
    short-summary: Remove Azure Enhanced Monitoring Extension
"""

helps['vm aem verify'] = """
    type: command
    short-summary: Verify Azure Enhanced Monitoring Extensions configured correctly
"""
