# Azure CLI billing Extension #
This is the extension for billing

### How to use ###
Install this extension using the below CLI command
```
az extension add --name billing
```

### Included Features ###
#### billing account ####
##### List #####
```
az billing account list
```
##### List #####
```
az billing account list --expand "soldTo,billingProfiles,billingProfiles/invoiceSections"
```
##### List #####
```
az billing account list --expand "enrollmentDetails,departments,enrollmentAccounts"
```
##### Show #####
```
az billing account show --expand "soldTo,billingProfiles,billingProfiles/invoiceSections" --name "{billingAccountName}"
```
##### Show #####
```
az billing account show --name "{billingAccountName}"
```
##### Update #####
```
az billing account update --name "{billingAccountName}" --display-name "Test Account" \
    --sold-to address-line1="Test Address 1" city="Redmond" company-name="Contoso" country="US" first-name="Test" last-name="User" postal-code="12345" region="WA" 
```
#### billing balance ####
##### Show #####
```
az billing balance show --account-name "{billingAccountName}" --profile-name "{billingProfileName}"
```
#### billing instruction ####
##### Create #####
```
az billing instruction create --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --name "{instructionName}" --amount 5000 --end-date "2020-12-30T21:26:47.997Z" \
    --start-date "2019-12-30T21:26:47.997Z" 
```
##### Show #####
```
az billing instruction show --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --name "{instructionName}" 
```
##### List #####
```
az billing instruction list --account-name "{billingAccountName}" --profile-name "{billingProfileName}"
```
#### billing profile ####
##### Create #####
```
az billing profile create --account-name "{billingAccountName}" --name "{billingProfileName}" \
    --bill-to address-line1="Test Address 1" city="Redmond" country="US" first-name="Test" last-name="User" postal-code="12345" region="WA" \
    --display-name "Finance" --enabled-azure-plans sku-id="0001" --enabled-azure-plans sku-id="0002" \
    --invoice-email-opt-in true --po-number "ABC12345" 
```
##### List #####
```
az billing profile list --expand "invoiceSections" --account-name "{billingAccountName}"
```
##### Show #####
```
az billing profile show --account-name "{billingAccountName}" --name "{billingProfileName}"
```
##### Show #####
```
az billing profile show --expand "invoiceSections" --account-name "{billingAccountName}" --name "{billingProfileName}"
```
##### List #####
```
az billing profile list --account-name "{billingAccountName}"
```
#### billing customer ####
##### List #####
```
az billing customer list --account-name "{billingAccountName}" --profile-name "{billingProfileName}"
```
##### Show #####
```
az billing customer show --account-name "{billingAccountName}" --name "{customerName}"
```
##### Show #####
```
az billing customer show --expand "enabledAzurePlans,resellers" --account-name "{billingAccountName}" \
    --name "{customerName}" 
```
#### billing invoice section ####
##### Create #####
```
az billing invoice section create --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --name "{invoiceSectionName}" --display-name "invoiceSection1" --labels costCategory="Support" pcCode="A123456" 
```
##### Show #####
```
az billing invoice section show --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --name "{invoiceSectionName}" 
```
##### List #####
```
az billing invoice section list --account-name "{billingAccountName}" --profile-name "{billingProfileName}"
```
#### billing permission ####
##### List #####
```
az billing permission list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --invoice-section-name "{invoiceSectionName}" 
```
#### billing subscription ####
##### List #####
```
az billing subscription list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --invoice-section-name "{invoiceSectionName}" 
```
##### Show #####
```
az billing subscription show --account-name "{billingAccountName}"
```
##### Update #####
```
az billing subscription update --account-name "{billingAccountName}" --cost-center "ABC1234"
```
##### Move #####
```
az billing subscription move --account-name "{billingAccountName}" \
    --destination-invoice-section-id "/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/invoiceSections/{newInvoiceSectionName}" 
```
##### Validate-move #####
```
az billing subscription validate-move --account-name "{billingAccountName}" \
    --destination-invoice-section-id "/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/invoiceSections/{newInvoiceSectionName}" 
```
##### Validate-move #####
```
az billing subscription validate-move --account-name "{billingAccountName}" \
    --destination-invoice-section-id "/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/invoiceSections/{newInvoiceSectionName}" 
```
#### billing product ####
##### List #####
```
az billing product list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --invoice-section-name "{invoiceSectionName}" 
```
##### Show #####
```
az billing product show --account-name "{billingAccountName}" --name "{productName}"
```
##### Update #####
```
az billing product update --account-name "{billingAccountName}" --auto-renew "Off" --name "{productName}"
```
##### Move #####
```
az billing product move --account-name "{billingAccountName}" \
    --destination-invoice-section-id "/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/invoiceSections/{newInvoiceSectionName}" \
    --name "{productName}" 
```
##### Validate-move #####
```
az billing product validate-move --account-name "{billingAccountName}" \
    --destination-invoice-section-id "/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/invoiceSections/{newInvoiceSectionName}" \
    --name "{productName}" 
```
##### Validate-move #####
```
az billing product validate-move --account-name "{billingAccountName}" \
    --destination-invoice-section-id "/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/invoiceSections/{newInvoiceSectionName}" \
    --name "{productName}" 
```
#### billing invoice ####
##### List #####
```
az billing invoice list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --period-end-date "2018-06-30" --period-start-date "2018-01-01" 
```
##### List #####
```
az billing invoice list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --period-end-date "2018-06-30" --period-start-date "2018-01-01" 
```
##### Show #####
```
az billing invoice show --account-name "{billingAccountName}" --name "{invoiceName}"
```
##### Show #####
```
az billing invoice show --account-name "{billingAccountName}" --name "{invoiceName}"
```
##### Show #####
```
az billing invoice show --account-name "{billingAccountName}" --name "{invoiceName}"
```
##### Show #####
```
az billing invoice show --account-name "{billingAccountName}" --name "{invoiceName}"
```
#### billing transaction ####
##### List #####
```
az billing transaction list --account-name "{billingAccountName}" --invoice-name "{invoiceName}"
```
#### billing policy ####
##### Update #####
```
az billing policy update --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --marketplace-purchases "OnlyFreeAllowed" --reservation-purchases "NotAllowed" --view-charges "Allowed" 
```
#### billing property ####
##### Show #####
```
az billing property show
```
##### Update #####
```
az billing property update --cost-center "1010"
```
#### billing role-definition ####
##### List #####
```
az billing role-definition list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --invoice-section-name "{invoiceSectionName}" 
```
#### billing role-assignment ####
##### List #####
```
az billing role-assignment list --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --invoice-section-name "{invoiceSectionName}" 
```
##### Delete #####
```
az billing role-assignment delete --account-name "{billingAccountName}" --profile-name "{billingProfileName}" \
    --name "{billingRoleAssignmentName}" --invoice-section-name "{invoiceSectionName}" 
```
#### billing agreement ####
##### List #####
```
az billing agreement list --account-name "{billingAccountName}"
```
##### Show #####
```
az billing agreement show --name "{agreementName}" --account-name "{billingAccountName}"
```