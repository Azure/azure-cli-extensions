# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['support'] = """
    type: group
    short-summary: Use Azure Support functionality.
"""

helps['support services'] = """
    type: group
    short-summary: Commands to manage services.
"""

helps['support services list'] = """
    type: command
    short-summary: List services.
"""

helps['support services show'] = """
    type: command
    short-summary: Show service.
    examples:
      - name: Show Virtual Machine Running Windows Service
        text: |-
               az support services show --service-name "6f16735c-b0ae-b275-ad3a-03479cfa1396"
"""

helps['support services problem-classifications'] = """
    type: group
    short-summary: Commands to manage problem classifications for service.
"""

helps['support services problem-classifications list'] = """
    type: command
    short-summary: List problem classifications for service.
    examples:
      - name: Show supported problem classifications under service 'Virtual Machine Running Window'
        text: |-
               az support services problem-classifications list --service-name "6f16735c-b0ae-b275-ad3a-03479cfa1396"
"""

helps['support services problem-classifications show'] = """
    type: command
    short-summary: Show problem classification for service.
    examples:
      - name: Show problem classification 'VM Performance / Memory usage is higher than expected' under service 'Virtual Machine Running Window'
        text: |-
               az support services problem-classifications show --service-name "6f16735c-b0ae-b275-ad3a-03479cfa1396" --problem-classification-name "0cb121be-61df-48e4-5faa-b34f01c7aa16"
"""

helps['support tickets'] = """
    type: group
    short-summary: Commands to manage support tickets.
"""

helps['support tickets list'] = """
    type: command
    short-summary: List support tickets.
"""

helps['support tickets show'] = """
    type: command
    short-summary: Show support ticket.
    examples:
      - name: Show support ticket named "myticketname"
        text: |-
               az support tickets show --ticket-name "myticketname"
"""

helps['support tickets update'] = """
    type: command
    short-summary: Update support ticket.
"""

helps['support tickets create'] = """
    type: command
    short-summary: Create support ticket.
"""

helps['support tickets wait'] = """
    type: command
    short-summary: Wait for support ticket creation to reach completion.
"""

helps['support tickets communications'] = """
    type: group
    short-summary: Commands to manage support ticket communication.
"""

helps['support tickets communications list'] = """
    type: command
    short-summary: List communications for support ticket.
    examples:
      - name: Show communications for support ticket named "myticketname"
        text: |-
               az support tickets communications list --ticket-name "myticketname"
"""

helps['support tickets communications show'] = """
    type: command
    short-summary: Show communication for support ticket.
    examples:
      - name: Show communication named "mycommunicationname" for support ticket named "myticketname"
        text: |-
               az support tickets communications show --ticket-name "myticketname" --communication-name "mycommunicationname"
"""

helps['support tickets communications create'] = """
    type: command
    short-summary: Create communication for support ticket.
"""

helps['support tickets communications wait'] = """
    type: command
    short-summary: Wait for support ticket communication creation to reach completion.
"""
