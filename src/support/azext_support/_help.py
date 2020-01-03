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
        text: >
               az support services problem-classifications show \\
                 --service-name "6f16735c-b0ae-b275-ad3a-03479cfa1396" \\
                 --problem-classification-name "0cb121be-61df-48e4-5faa-b34f01c7aa16"
"""

helps['support tickets'] = """
    type: group
    short-summary: Commands to manage support tickets.
"""

helps['support tickets list'] = """
    type: command
    short-summary: List support tickets.
    examples:
      - name: List support tickets that are active and created after specific date"
        text: |-
               az support tickets list --filters "CreatedDate ge 2019-12-01 and Status eq 'Open'"
"""

helps['support tickets show'] = """
    type: command
    short-summary: Show support ticket.
    examples:
      - name: Show support ticket named "test_ticket_from_pythoncli"
        text: |-
               az support tickets show --ticket-name "test_ticket_from_pythoncli"
"""

helps['support tickets update'] = """
    type: command
    short-summary: Update support ticket.
    examples:
      - name: Update severity for support ticket named "test_ticket_from_pythoncli"
        text: |-
               az support tickets update --ticket-name "test_ticket_from_pythoncli" --severity "moderate"

      - name: Update one or more contact details for support ticket named "test_ticket_from_pythoncli"
        text: >
               az support tickets update --ticket-name "test_ticket_from_pythoncli" \\
                --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
                --contact-country "USA" \\
                --contact-email "abc@contoso.com" \\
                --contact-first-name "Foo" \\
                --contact-language "en-US" \\
                --contact-last-name "Bar" \\
                --contact-method "phone" \\
                --contact-phone-numbe "123-456-7890" \\
                --contact-timezone "Pacific Standard Time"
"""

helps['support tickets create'] = """
    type: command
    short-summary: Create support ticket
    examples:
      - name: Create support ticket for technical issue
        text: >
               az support tickets create \\
                --contact-country "USA" \\
                --contact-email "abc@contoso.com" \\
                --contact-first-name "Foo" \\
                --contact-language "en-US" \\
                --contact-last-name "Bar" \\
                --contact-method "email" \\
                --contact-timezone "Pacific Standard Time" \\
                --description "test ticket description" \\
                --problem-classification "/providers/Microsoft.Support/services/cddd3eb5-1830-b494-44fd-782f691479dc/problemClassifications/ef8b3865-0c5a-247b-dcaa-d70fd7611a3c" \\
                --service "/providers/Microsoft.Support/services/cddd3eb5-1830-b494-44fd-782f691479dc" \\
                --severity "minimal" \\
                --ticket-name "test_ticket_from_pythoncli" \\
                --title "test ticket from python cli" \\
                --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
                --technical-resource "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/testserver"

      - name: Create support ticket for billing issue using AOBO scenario. First run "az login" (To customer tenant) and "az login -t contoso.onmicrosoft.com --allow-no-subscriptions" (To partner tenant)
        text: >
               az support tickets create \\
                --contact-country "USA" \\
                --contact-email "abc@contoso.com" \\
                --contact-first-name "Foo" \\
                --contact-language "en-US" \\
                --contact-last-name "Bar" \\
                --contact-method "email" \\
                --contact-timezone "Pacific Standard Time" \\
                --description "test ticket description" \\
                --problem-classification "/providers/Microsoft.Support/services/517f2da6-78fd-0498-4e22-ad26996b1dfc/problemClassifications/a8d819ba-73bd-10c2-fcd5-7059fc386df3" \\
                --service "/providers/Microsoft.Support/services/517f2da6-78fd-0498-4e22-ad26996b1dfc" \\
                --severity "minimal" \\
                --ticket-name "test_ticket_from_pythoncli" \\
                --title "test ticket from python cli" \\
                --partner-subscription-id "00000000-0000-0000-0000-000000000000"

      - name: Create support ticket for quota issue
        text: >
               az support tickets create \\
                --contact-country "USA" \\
                --contact-email "abc@contoso.com" \\
                --contact-first-name "Foo" \\
                --contact-language "en-US" \\
                --contact-last-name "Bar" \\
                --contact-method "email" \\
                --contact-timezone "Pacific Standard Time" \\
                --description "test ticket description" \\
                --problem-classification "/providers/Microsoft.Support/services/06bfd9d3-516b-d5c6-5802-169c800dec89/problemClassifications/e12e3d1d-7fa0-af33-c6d0-3c50df9658a3" \\
                --service "/providers/Microsoft.Support/services/06bfd9d3-516b-d5c6-5802-169c800dec89" \\
                --severity "minimal" \\
                --ticket-name "test_ticket_from_pythoncli" \\
                --title "test ticket from python cli" \\
                --quota-change-payload "{\"SKU\":\"DSv3 Series\",\"NewLimit\":111}" "{\"SKU\":\"DSv3 Series\",\"NewLimit\":102}" \\
                --quota-change-regions "EastUS" "EastUS2" \\
                --quota-change-version "1.0"
"""

helps['support tickets communications'] = """
    type: group
    short-summary: Commands to manage support ticket communication.
    examples:
      - name: Show support ticket named "test_ticket_from_pythoncli"
        text: |-
               az support tickets communications list --ticket-name "test_ticket_from_pythoncli"
"""

helps['support tickets communications list'] = """
    type: command
    short-summary: List communications for support ticket.
    examples:
      - name: List communications for support ticket named "test_ticket_from_pythoncli"
        text: |-
               az support tickets communications list --ticket-name "test_ticket_from_pythoncli" --filters "CreatedDate ge 2019-12-01 and communicationType eq 'web'"
"""

helps['support tickets communications show'] = """
    type: command
    short-summary: Show communication for support ticket.
    examples:
      - name: Show communication named "mycommunicationname" for support ticket named "test_ticket_from_pythoncli"
        text: |-
               az support tickets communications show --ticket-name "test_ticket_from_pythoncli" --communication-name "message1"
"""

helps['support tickets communications create'] = """
    type: command
    short-summary: Create communication for support ticket.
    examples:
      - name: Post message named "message1" for support ticket named "test_ticket_from_pythoncli"
        text: >
               az support tickets communications create --ticket-name "test_ticket_from_pythoncli" \\
                --communication-name "message1" \\
                --communication-body "test communication message body" \\
                --communication-subject "message from python cli"
"""
