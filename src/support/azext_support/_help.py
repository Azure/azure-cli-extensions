# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['support'] = """
type: group
short-summary: Manage and administer support tickets.
"""

helps['support services'] = """
type: group
short-summary: Commands to manage services.
"""

helps['support services list'] = """
type: command
short-summary: List services.
examples:
  - name: List services available for creating support ticket.
    text: |-
          az support services list
"""

helps['support services show'] = """
type: command
short-summary: Show service.
examples:
  - name: Show service corresponding to name "ServiceNameGuid".
    text: |-
          az support services show --service-name "ServiceNameGuid"
"""

helps['support services problem-classifications'] = """
type: group
short-summary: Commands to manage problem classifications for a service.
"""

helps['support services problem-classifications list'] = """
type: command
short-summary: List problem classifications for a service.
examples:
  - name: Show supported problem classifications for a service corresponding to name "ServiceNameGuid".
    text: |-
          az support services problem-classifications list --service-name "ServiceNameGuid"
"""

helps['support services problem-classifications show'] = """
type: command
short-summary: Show a problem classification for service.
examples:
  - name: Show a problem classification corresponding to name "ProblemClassificationNameGuid" for a service corresponding to name "ServiceNameGuid".
    text: |
          az support services problem-classifications show \\
            --service-name "ServiceNameGuid" \\
            --problem-classification-name "ProblemClassificationNameGuid"
"""

helps['support tickets'] = """
type: group
short-summary: Commands to manage support tickets.
"""

helps['support tickets list'] = """
type: command
short-summary: List support tickets.
examples:
  - name: List support tickets created after 1st January, 2020 that are still open (unresolved).
    text: |-
          az support tickets list --filters "CreatedDate ge 2020-01-01 and Status eq 'Open'"
"""

helps['support tickets show'] = """
type: command
short-summary: Show support ticket.
examples:
  - name: Show support ticket named "TicketCreatedFromPythonCLI".
    text: |-
          az support tickets show --ticket-name "TicketCreatedFromPythonCLI"
"""

helps['support tickets update'] = """
type: command
short-summary: Update support ticket.
examples:
  - name: Update severity for support ticket named "TicketCreatedFromPythonCLI".
    text: |-
          az support tickets update --ticket-name "TicketCreatedFromPythonCLI" --severity "moderate"

  - name: Update one or more properties of contact details for support ticket named "TicketCreatedFromPythonCLI".
    text: |
          az support tickets update --ticket-name "TicketCreatedFromPythonCLI" \\
            --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "phone" \\
            --contact-phone-number "123-456-7890" \\
            --contact-timezone "Pacific Standard Time"
"""

helps['support tickets create'] = """
type: command
short-summary: Create support ticket.
examples:
  - name: Create support ticket for technical issue.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "TicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/TechnicalServiceNameGuid/problemClassifications/TechnicalProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "TicketCreatedFromPythonCLI" \\
            --title "TicketTitle" \\
            --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
            --technical-resource "/subscriptions/SubscriptionGuid/resourceGroups/RgName/providers/Microsoft.Compute/virtualMachines/RName"

  - name: Create support ticket for billing issue.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "TicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/BillingServiceNameGuid/problemClassifications/BillingProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "TicketCreatedFromPythonCLI" \\
            --title "TicketTitle" \\
            --partner-tenant-id "CSPPartnerTenantIdGuid"

  - name: Create quota change support ticket for DSv3 sku in EastUS and EastUS2 regions.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "TicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/QuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "TicketCreatedFromPythonCLI" \\
            --title "TicketTitle" \\
            --quota-change-payload "{\"SKU\":\"DSv3 Series\",\"NewLimit\":111}" "{\"SKU\":\"DSv3 Series\",\"NewLimit\":102}" \\
            --quota-change-regions "EastUS" "EastUS2" \\
            --quota-change-version "1.0"
"""

helps['support tickets communications'] = """
type: group
short-summary: Commands to manage support ticket communication.
examples:
  - name: Show support ticket named "TicketCreatedFromPythonCLI".
    text: |-
          az support tickets communications list --ticket-name "TicketCreatedFromPythonCLI"
"""

helps['support tickets communications list'] = """
type: command
short-summary: List communications for support ticket.
examples:
  - name: List communications for support ticket named "TicketCreatedFromPythonCLI".
    text: |-
          az support tickets communications list --ticket-name "TicketCreatedFromPythonCLI" --filters "CreatedDate ge 2020-01-01 and communicationType eq 'Web'"
"""

helps['support tickets communications show'] = """
type: command
short-summary: Show communication for support ticket.
examples:
  - name: Show communication named "TicketCommunicationCreatedFromPythonCLI" for support ticket named "TicketCreatedFromPythonCLI"
    text: |-
          az support tickets communications show --ticket-name "TicketCreatedFromPythonCLI" --communication-name "TicketCommunicationCreatedFromPythonCLI"
"""

helps['support tickets communications create'] = """
type: command
short-summary: Create communication for support ticket.
examples:
  - name: Create communication named "TicketCommunicationCreatedFromPythonCLI" for support ticket named "TicketCreatedFromPythonCLI".
    text: |
          az support tickets communications create \\
            --ticket-name "TicketCreatedFromPythonCLI" \\
            --communication-name "TicketCommunicationCreatedFromPythonCLI" \\
            --communication-body "TicketCommunicationBody" \\
            --communication-subject "TicketCommunicationSubject"
"""
