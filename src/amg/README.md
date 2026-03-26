# Microsoft Azure CLI 'amg' Extension
This is an extension to manage Azure Managed Grafana instances

## How to use ##
Install this extension using the below CLI command
```
az extension add --name amg
```

## Included Features
### Create, show, and delete instances

#### create an instance
*Examples:*
```
az grafana create \
    -g MyResourceGroup \
    -n MyGrafanaInstance \
    --tags department=financial
```

#### delete an instance
*Examples:*
```
az grafana delete \
    -n MyGrafanaInstance
```

### Configure folders, data sources, notification channels and dashboards

#### create a folder
*Examples:*
```
az grafana folder create \
     -n MyGrafanaInstance \
     --title "Health KPI"
```

#### configure a data source 
*Examples:*
```
az grafana data-source create \
    -n MyGrafanaInstance \
    --definition ~/data-source-sql.json
```

#### configure a notification channel 
*Examples:*
```
az grafana notification-channel create \
    -n MyGrafanaInstance \
    --definition ~/notification-channel-teams.json
```

#### Create a dashboard
*Examples:*
```
az grafana dashboard create \
    -n MyGrafanaInstance \
    --folder "Health KPI" \
    --title "SQL status" \
    --definition ~/dashboard-sql.json
```