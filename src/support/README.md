# Microsoft Azure CLI 'support' Extension #

## How to use ##

Install this extension using the below CLI command

```python
az extension add --name support
```

## Included Commands ##

### *"Services"* commands ###

* #### List Services ####

    *Examples:*

    ```python
    az support services list
    ```

* #### Get Single Service ####

    *Examples:*

    ```python
    az support services show --service-name "ServiceNameGuid"
    ```

### *"Problem-Classifications"* commands ###

* #### List Problem Classifications ####

    *Examples:*

    ```python
    az support services problem-classifications list --service-name "ServiceNameGuid"
    ```

* #### Get Single Problem Classification ####

    *Examples:*

    ```python
    az support services problem-classifications --service-name "ServiceNameGuid" show --problem-classification-name "ProblemClassificationNameGuid"
    ```

### *"Tickets"* commands ###

* #### List Tickets ####

    *Examples:*

    ```python
    # Vanilla variant
    az support tickets list

    # Tickets created after 1st January, 2020 that are still open (unresolved)
    az support tickets list --filters "CreatedDate ge 2020-01-01 and Status eq 'Open'"
    ```

* #### Get Single Ticket ####

    *Examples:*

    ```python
    az support tickets show --ticket-name "TicketCreatedFromPythonCLI"
    ```

* #### Update Ticket ####

    *Examples:*

    ```python
    # Update Severity
    az support tickets update --ticket-name "TicketCreatedFromPythonCLI" --severity "moderate"

    # Update one or more Contact Details properties
    az support tickets update --ticket-name "TicketCreatedFromPythonCLI" \
        --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "phone" \
        --contact-phone-number "123-456-7890" \
        --contact-timezone "Pacific Standard Time"
    ```

* #### Create Ticket ####

    *Examples:*

    ```python
    # Create technical ticket
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "TicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/TechnicalServiceNameGuid/problemClassifications/TechnicalProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "TicketCreatedFromPythonCLI" \
        --title "TicketTitle" \
        --contact-additional-emails "xyz@contoso.com" "devs@contoso.com" \
        --technical-resource "/subscriptions/SubscriptionGuid/resourceGroups/RgName/providers/Microsoft.Compute/virtualMachines/RName"

    # Create billing ticket
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "TicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/BillingServiceNameGuid/problemClassifications/BillingProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "TicketCreatedFromPythonCLI" \
        --title "TicketTitle" \
        --partner-tenant-id "CSPPartnerTenantIdGuid"

    # Create quota change ticket for DSv3 sku in EastUS and EastUS2 regions
    az support tickets create \
        --contact-country "USA" \
        --contact-email "abc@contoso.com" \
        --contact-first-name "Foo" \
        --contact-language "en-US" \
        --contact-last-name "Bar" \
        --contact-method "email" \
        --contact-timezone "Pacific Standard Time" \
        --description "TicketDescription" \
        --problem-classification "/providers/Microsoft.Support/services/QuotaServiceNameGuid/problemClassifications/QuotaProblemClassificationNameGuid" \
        --severity "minimal" \
        --ticket-name "TicketCreatedFromPythonCLI" \
        --title "TicketTitle" \
        --quota-change-payload "{\"SKU\":\"DSv3 Series\",\"NewLimit\":111}" "{\"SKU\":\"DSv3 Series\",\"NewLimit\":102}" \
        --quota-change-regions "EastUS" "EastUS2" \
        --quota-change-version "1.0"
    ```

### *"Communications"* commands ###

* #### List Communications ####

    *Examples:*

    ```python
    # Vanilla variant
    az support tickets communications list --name "TicketCreatedFromPythonCLI"

    # Communications created after 1st January, 2020 of type "web"
    az support tickets communications list \
        --ticket-name "TicketCreatedFromPythonCLI" \
        --filters "CreatedDate ge 2020-01-01 and communicationType eq 'Web'"
    ```

* #### Get Communication ####

    *Examples:*

    ```python
    az support tickets communications show \
        --ticket-name "TicketCreatedFromPythonCLI" \
        --communication-name "TicketCommunicationCreatedFromPythonCLI"
    ```

* #### Add Communication ####

    *Examples:*

    ```python
    az support tickets communications create \
        --ticket-name "TicketCreatedFromPythonCLI" \
        --communication-name "TicketCommunicationCreatedFromPythonCLI" \
        --communication-body "TicketCommunicationBody" \
        --communication-subject "TicketCommunicationSubject"
    ```
