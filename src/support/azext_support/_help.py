# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['support'] = """
type: group
short-summary: Manage Azure support resource.
"""

helps['support services'] = """
type: group
short-summary: Azure services and related problem categories.
"""

helps['support services list'] = """
type: command
short-summary: Lists all the Azure services available for support ticket creation. Always use the service and it's corresponding problem classification(s) obtained programmatically for support ticket creation. This practice ensures that you always have the most recent set of service and problem classification Ids.
examples:
  - name: Gets list of services for which a support ticket can be created.
    text: |-
          az support services list
"""

helps['support services show'] = """
type: command
short-summary: Gets a specific Azure service for support ticket creation.
examples:
  - name: Gets details of Azure service.
    text: |-
          az support services show --service-name "ServiceNameGuid"
"""

helps['support services problem-classifications'] = """
type: group
short-summary: Problem classifications for an Azure service.
"""

helps['support services problem-classifications list'] = """
type: command
short-summary: Lists all the problem classifications (categories) available for an Azure service. Always use the service and it's corresponding problem classification(s) obtained programmatically for support ticket creation. This practice ensures that you always have the most recent set of service and problem classification Ids.
examples:
  - name: Gets list of problemClassifications for a service for which a support ticket can be created.
    text: |-
          az support services problem-classifications list --service-name "ServiceNameGuid"
"""

helps['support services problem-classifications show'] = """
type: command
short-summary: Gets the problem classification details for an Azure service.
examples:
  - name: Gets details of problemClassification for Azure service.
    text: |
          az support services problem-classifications show \\
            --service-name "ServiceNameGuid" \\
            --problem-classification-name "ProblemClassificationNameGuid"
"""

helps['support tickets'] = """
type: group
short-summary: Create and manage Azure support ticket.
"""

helps['support tickets list'] = """
type: command
short-summary: Lists all the support tickets for an Azure subscription.
examples:
  - name: List support tickets for a subscription.
    text: |-
          az support tickets list

  - name: List support tickets in open state for a subscription.
    text: |-
          az support tickets list --filters "Status eq 'Open'"

  - name: List support tickets created on or after a certain date and in open state for a subscription.
    text: |-
          az support tickets list --filters "CreatedDate ge 2020-01-01 and Status eq 'Open'"
"""

helps['support tickets show'] = """
type: command
short-summary: Gets support ticket details for an Azure subscription.
examples:
  - name: Get details of a subscription ticket.
    text: |-
          az support tickets show --ticket-name "TestTicketName"
"""

helps['support tickets update'] = """
type: command
short-summary: Updates severity level and customer contact information for a support ticket.
examples:
  - name: Update support ticket severity.
    text: |-
          az support tickets update --ticket-name "TestTicketName" --severity "moderate"

  - name: Update support ticket customer contact details properties.
    text: |
          az support tickets update --ticket-name "TestTicketName" \\
            --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "phone" \\
            --contact-phone-number "123-456-7890" \\
            --contact-timezone "Pacific Standard Time"

  - name: Update support ticket severity and customer contact details properties.
    text: |
          az support tickets update --ticket-name "TestTicketName" \\
            --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "phone" \\
            --contact-phone-number "123-456-7890" \\
            --contact-timezone "Pacific Standard Time" \\
            --severity "moderate"
"""

helps['support tickets create'] = """
type: command
short-summary: Creates a new support ticket for Quota increase, Technical, Billing, and Subscription Management issues for the specified subscription.
examples:
  - name: Create a ticket for Billing related issues.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "BillingTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/BillingServiceNameGuid/problemClassifications/BillingProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "BillingTestTicketName" \\
            --title "BillingTicketTitle"

  - name: Create a ticket for Subscription Management related issues.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "SubMgmtTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/SubMgmtServiceNameGuid/problemClassifications/SubMgmtProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "SubMgmtTestTicketName" \\
            --title "SubMgmtTicketTitle"

  - name: Create a ticket for Technical issue related to a specific resource.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "TechnicalTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/TechnicalServiceNameGuid/problemClassifications/TechnicalProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "TechnicalTestTicketName" \\
            --title "TechnicalTicketTitle" \\
            --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \\
            --technical-resource "/subscriptions/SubscriptionGuid/resourceGroups/RgName/providers/Microsoft.Compute/virtualMachines/RName"

  - name: Create a ticket for Billing related issues in admin on behalf of (AOBO) mode.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "BillingTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/BillingServiceNameGuid/problemClassifications/BillingProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "BillingTestTicketName" \\
            --title "BillingTicketTitle" \\
            --partner-tenant-id "CSPPartnerTenantIdGuid"

  - name: Create a ticket to request Quota increase for Compute VM Cores.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/CoresQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"SKU\\\":\\\"DSv3 Series\\\", \\\"NewLimit\\\":104}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0"

  - name: Create a ticket to request Quota increase for Low-priority cores for a Batch account.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"AccountName\\\":\\\"test\\\", \\\"NewLimit\\\":200, \\\"Type\\\":\\\"LowPriority\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Account"

  - name: Create a ticket to request Quota increase for specific VM family cores for a Batch account.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"AccountName\\\":\\\"test\\\", \\\"VMFamily\\\":\\\"standardA0_A7Family\\\", \\\"NewLimit\\\":200, \\\"Type\\\":\\\"Dedicated\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Account"

  - name: Create a ticket to request Quota increase for Pools for a Batch account.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"AccountName\\\":\\\"test\\\", \\\"NewLimit\\\":200, \\\"Type\\\":\\\"Pools\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Account"

  - name: Create a ticket to request Quota increase for Active Jobs and Job Schedules for a Batch account.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"AccountName\\\":\\\"test\\\", \\\"NewLimit\\\":200, \\\"Type\\\":\\\"Jobs\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Account"

  - name: Create a ticket to request Quota increase for number of Batch accounts for a subscription.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"NewLimit\\\":200, \\\"Type\\\":\\\"Account\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Subscription"

  - name: Create a ticket to request Quota increase for DTUs for SQL Database.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDatabaseQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"ServerName\\\":\\\"testserver\\\", \\\"NewLimit\\\":54000}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "DTUs"

  - name: Create a ticket to request Quota increase for Servers for SQL Database.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDatabaseQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"NewLimit\\\":54000}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Servers"

  - name: Create a ticket to request Quota increase for DTUs for SQL Data Warehouse.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDataWarehouseQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"ServerName\\\":\\\"testserver\\\", \\\"NewLimit\\\":54000}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "DTUs"

  - name: Create a ticket to request Quota increase for Servers for SQL Data Warehouse.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDataWarehouseQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"NewLimit\\\":200}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "Servers"

  - name: Create a ticket to request Quota increase for specific VM family cores for Machine Learning service.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/MachineLearningQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"VMFamily\\\":\\\"standardA0_A7Family\\\", \\\"NewLimit\\\":200, \\\"Type\\\":\\\"Dedicated\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "BatchAml"

  - name: Create a ticket to request Quota increase for Low-priority cores for Machine Learning service.
    text: |
          az support tickets create \\
            --contact-country "USA" \\
            --contact-email "abc@contoso.com" \\
            --contact-first-name "Foo" \\
            --contact-language "en-US" \\
            --contact-last-name "Bar" \\
            --contact-method "email" \\
            --contact-timezone "Pacific Standard Time" \\
            --description "QuotaTicketDescription" \\
            --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/MachineLearningQuotaProblemClassificationNameGuid" \\
            --severity "minimal" \\
            --ticket-name "QuotaTestTicketName" \\
            --title "QuotaTicketTitle" \\
            --quota-change-payload "{\\\"NewLimit\\\":200, \\\"Type\\\":\\\"LowPriority\\\"}" \\
            --quota-change-regions "EastUS" \\
            --quota-change-version "1.0" \\
            --quota-change-subtype "BatchAml"
"""

helps['support tickets communications'] = """
type: group
short-summary: Manage support ticket communications.
"""

helps['support tickets communications list'] = """
type: command
short-summary: Lists all communications (attachments not included) for a support ticket.
examples:
  - name: List communications for a subscription support ticket.
    text: |-
          az support tickets communications list --ticket-name "TestTicketName"

  - name: List web communications for a subscription support ticket.
    text: |-
          az support tickets communications list \\
            --ticket-name "TestTicketName" \\
            --filters "communicationType eq 'Web'"

  - name: List web communication created on or after a specific date for a subscription support ticket.
    text: |-
          az support tickets communications list \\
            --ticket-name "TestTicketName" \\
            --filters "CreatedDate ge 2020-01-01 and communicationType eq 'Web'"
"""

helps['support tickets communications show'] = """
type: command
short-summary: Gets communication details for a support ticket.
examples:
  - name: Get communication details for a subscription support ticket.
    text: |-
          az support tickets communications show \\
            --ticket-name "TestTicketName" \\
            --communication-name "TestTicketCommunicationName"
"""

helps['support tickets communications create'] = """
type: command
short-summary: Adds a new customer communication to an Azure support ticket.
examples:
  - name: Add communication to subscription ticket.
    text: |
          az support tickets communications create \\
            --ticket-name "TestTicketName" \\
            --communication-name "TestTicketCommunicationName" \\
            --communication-body "TicketCommunicationBody" \\
            --communication-subject "TicketCommunicationSubject"
"""
