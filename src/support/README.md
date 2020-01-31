# Microsoft Azure CLI 'support' Extension #

Create and manage Azure Support tickets using Azure CLI. [Learn more](https://aka.ms/supportticketAPI) about operations and scenarios we support programmatically. 

## How to use ##

Install this extension using the below CLI command. For details on each command, use ``-h`` or ``--help``.

```
az extension add --name support
```

## Included Commands ##

### *"Services"* commands ###

* #### List Services ####

    *Examples:*

    ```
    # Gets list of services for which a support ticket can be created.
    az support services list
    ```

* #### Get Single Service ####

    *Examples:*

    ```
    # Gets details of Azure service.
    az support services show --service-name "ServiceNameGuid"
    ```

### *"Problem-Classifications"* commands ###

* #### List Problem Classifications ####

    *Examples:*

    ```
    # Gets list of problemClassifications for a service for which a support ticket can be created.
    az support services problem-classifications list --service-name "ServiceNameGuid"
    ```

* #### Get Single Problem Classification ####

    *Examples:*

    ```
    # Gets details of problemClassification for Azure service.
    az support services problem-classifications --service-name "ServiceNameGuid" show --problem-classification-name "ProblemClassificationNameGuid"
    ```

### *"Tickets"* commands ###

* #### List Tickets ####

    *Examples:*

    ```
    # List support tickets for a subscription.
    az support tickets list

    # List support tickets in open state for a subscription.
    az support tickets list --filters "Status eq 'Open'"

    # List support tickets created on or after a certain date and in open state for a subscription.
    az support tickets list --filters "CreatedDate ge 2020-01-01 and Status eq 'Open'"
    ```

* #### Get Single Ticket ####

    *Examples:*

    ```
    # Get details of a subscription ticket.
    az support tickets show --ticket-name "TestTicketName"
    ```

* #### Update Ticket ####

    *Examples:*

    ```
    # Update support ticket severity.
    az support tickets update --ticket-name "TestTicketName" --severity "moderate"

    # Update support ticket customer contact details properties.
    az support tickets update --ticket-name "TestTicketName" \
        --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "phone" \
        --contact-phone-number "123-456-7890" \
        --contact-timezone "Pacific Standard Time"

    # Update support ticket severity and customer contact details properties.
    az support tickets update --ticket-name "TestTicketName" \
        --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "phone" \
        --contact-phone-number "123-456-7890" \
        --contact-timezone "Pacific Standard Time" \
        --severity "moderate"
    ```

* #### Create Ticket ####

    *Examples:*

    ```
    # Create a ticket for Billing related issues.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "BillingTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/BillingServiceNameGuid/problemClassifications/BillingProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "BillingTestTicketName" \
        --title "BillingTicketTitle"
        
    # Create a ticket for Subscription Management related issues.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "SubMgmtTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/SubMgmtServiceNameGuid/problemClassifications/SubMgmtProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "SubMgmtTestTicketName" \
        --title "SubMgmtTicketTitle"
        
    # Create a ticket for Technical issue related to a specific resource.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "TechnicalTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/TechnicalServiceNameGuid/problemClassifications/TechnicalProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "TechnicalTestTicketName" \
        --title "TechnicalTicketTitle" \
        --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \
        --technical-resource "/subscriptions/SubscriptionGuid/resourceGroups/RgName/providers/Microsoft.Compute/virtualMachines/RName"
        
    # Create a ticket for Billing related issues in admin on behalf of (AOBO) mode.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "BillingTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/BillingServiceNameGuid/problemClassifications/BillingProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "BillingTestTicketName" \
        --title "BillingTicketTitle" \
        --partner-tenant-id "CSPPartnerTenantIdGuid"
        
    # Create a ticket to request Quota increase for Compute VM Cores.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/CoresQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"SKU\":\"DSv3 Series\", \"NewLimit\":104}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0"

    # Create a ticket to request Quota increase for Low-priority cores for a Batch account.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"AccountName\":\"test\", \"NewLimit\":200, \"Type\":\"LowPriority\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Account"
        
    # Create a ticket to request Quota increase for specific VM family cores for a Batch account.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"AccountName\":\"test\", \"VMFamily\":\"standardA0_A7Family\", \"NewLimit\":200, \"Type\":\"Dedicated\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Account"
        
    # Create a ticket to request Quota increase for Pools for a Batch account.
     az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"AccountName\":\"test\", \"NewLimit\":200, \"Type\":\"Pools\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Account"
        
    # Create a ticket to request Quota increase for Active Jobs and Job Schedules for a Batch account.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"AccountName\":\"test\", \"NewLimit\":200, \"Type\":\"Jobs\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Account"
        
    # Create a ticket to request Quota increase for number of Batch accounts for a subscription.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/BatchQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"NewLimit\":200, \"Type\":\"Account\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Subscription"
        
    # Create a ticket to request Quota increase for DTUs for SQL Database.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDatabaseQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"ServerName\":\"testserver\", \"NewLimit\":54000}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "DTUs"
        
    # Create a ticket to request Quota increase for Servers for SQL Database.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDatabaseQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"NewLimit\":54000}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Servers"
        
    # Create a ticket to request Quota increase for DTUs for SQL Data Warehouse.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDataWarehouseQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"ServerName\":\"testserver\", \"NewLimit\":54000}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "DTUs"
        
    # Create a ticket to request Quota increase for Servers for SQL Data Warehouse.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/SqlDataWarehouseQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"NewLimit\":200}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "Servers"
        
    # Create a ticket to request Quota increase for specific VM family cores for Machine Learning service.
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/MachineLearningQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"VMFamily\":\"standardA0_A7Family\", \"NewLimit\":200, \"Type\":\"Dedicated\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "BatchAml"
        
    # Create a ticket to request Quota increase for Low-priority cores for Machine Learning service.
     az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "QuotaTicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/MachineLearningQuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "QuotaTestTicketName" \
        --title "QuotaTicketTitle" \
        --quota-change-payload "{\"NewLimit\":200, \"Type\":\"LowPriority\"}" \
        --quota-change-regions "EastUS" \
        --quota-change-version "1.0" \
        --quota-change-subtype "BatchAml"
    ```

### *"Communications"* commands ###

* #### List Communications ####

    *Examples:*

    ```
    # List communications for a subscription support ticket.
    az support tickets communications list --name "TestTicketName"

    # List web communications for a subscription support ticket.
    az support tickets communications list \
        --ticket-name "TestTicketName" \
        --filters "communicationType eq 'Web'"

    # List web communication created on or after a specific date for a subscription support ticket.
    az support tickets communications list \
        --ticket-name "TestTicketName" \
        --filters "CreatedDate ge 2020-01-01 and communicationType eq 'Web'"
    ```

* #### Get Communication ####

    *Examples:*

    ```
    # Get communication details for a subscription support ticket.
    az support tickets communications show \
        --ticket-name "TestTicketName" \
        --communication-name "TestTicketCommunicationName"
    ```

* #### Add Communication ####

    *Examples:*

    ```
    # Add communication to subscription ticket.
    az support tickets communications create \
        --ticket-name "TestTicketName" \
        --communication-name "TestTicketCommunicationName" \
        --communication-body "TicketCommunicationBody" \
        --communication-subject "TicketCommunicationSubject"
    ```
