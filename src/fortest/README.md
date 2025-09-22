# Azure CLI fortest Extension #
This is an extension to Azure CLI to manage fortest resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name fortest
```
### Included Features

##### Get emission data available date range.
```
az fortest get-emission-data-available-date-range
```

##### Get emission report - overall summary.

```
az fortest get-emission-report --subscription-list [00000000-0000-0000-0000-000000000000] --date-range '{start:2024-04-01,end:2025-04-01}' --fortest-scope-list [Scope1,Scope2,Scope3] --overall-summary
```

##### Get emission report - monthly summary

```
az fortest get-emission-report --subscription-list [00000000-0000-0000-0000-000000000000] --date-range '{start:2024-04-01,end:2025-04-01}' --fortest-scope-list [Scope1,Scope2,Scope3] --monthly-summary
```

##### Get emission report - item details

```
az fortest get-emission-report --subscription-list [00000000-0000-0000-0000-000000000000] --date-range '{start:2025-04-01,end:2025-04-01}' --fortest-scope-list [Scope1,Scope2,Scope3] --item-details "{category-type:ResourceType,order-by:ItemName,page-size:10,sort-direction:desc}"
```

##### Get emission report - top items summary

```
az fortest get-emission-report --subscription-list [00000000-0000-0000-0000-000000000000] --date-range '{start:2025-04-01,end:2025-04-01}' --fortest-scope-list [Scope1,Scope2,Scope3] --top-items-summary "{category-type:ResourceType,top-items:5}"
```

##### Get emission report - top items monthly summary

```
az fortest get-emission-report --subscription-list [00000000-0000-0000-0000-000000000000] --date-range '{start:2024-04-01,end:2025-04-01}' --fortest-scope-list [Scope1,Scope2,Scope3] --top-items-monthly "{category-type:ResourceType,top-items:5}"
```