# Azure CLI Acat Extension #
This is an extension to Azure CLI to manage Acat resources.

## How to use ##
## Manage ACAT reports
```powershell
$reportName = "yourReportName"
$resourceIds = @()
# list resources by graph
$resources = (az graph query -q "Resources| where resourceGroup=='mcatsandbox'| take 2 " | ConvertFrom-Json).data
# or by resource list
$resources = az resource list | ConvertFrom-Json
# prepare input
$resources | ForEach-Object { $resourceIds += @{'resource-id' = $_.id } }

### create report
az acat report create `
    --report-name $reportName `
    # --offer-guid is optional`
    --resources ($resourceIds | ConvertTo-Json -Compress)
# or from a resoure list json file
az acat report create `
    --report-name $reportName `
    --resources resourceList.json
# show report
az acat report list | ConvertFrom-Json 
az acat report show --report-name $reportName

### update report

az acat report update `
    --report-name $reportName `
    --offer-guid "your-offer-guid" | ConvertFrom-Json

### delete report
az acat report delete   --report-name $reportName

## download report
az acat report download --report-name $reportName --download-type "ResourceList"
# --download-type= enum[ResourceList,ComplianceReport,CompliancePdfReport]

# or specify path and file name
az acat report download `
    --report-name $reportName `
    --download-type "CompliancePdfReport"`
    --path "C:\workspace"`
    --name "acatReport"

# get control assessments from a report
az acat report get-control-assessments --report-name $reportName
# apply filters to the assessments
az acat report get-control-assessments --report-name $reportName --compliance-status "failed"

# trigger quick evaluation on specified resource lists
az acat quick-evaluation --resource-ids $resources.id
```
## Manage ACAT webhooks on reports
```powershell
# create a report before running following commands
$hookName="yourHookName"
$reportName = "yourReportName"
az acat report webhook create `
    --report-name $reportName `
    --webhook-name $hookName `
    --trigger-mode all `
    --payload-url "https://" `
    --enable-ssl "true"

# check if the webhook is configured correctly
az acat report webhook list --report-name $reportName | ConvertFrom-Json
az acat report webhook show --report-name $reportName --webhook-name $hookName
```