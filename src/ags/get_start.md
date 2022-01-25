There 2 ways to use it

- If you have an existing CLI, install the extension: `az extension add  --source https://github.com/yugangw-msft/azure-cli-extensions/raw/ags/src/ags/dist/ags-0.1.0-py3-none-any.whl`
- If you have docker, run `docker run -it graazurecli.azurecr.io/azure-cli`
 


The test script below should explain command flows. Everything is under “az grafana”. Using “az grafana -h” should guide you through easily

```bash
    #!/bin/bash

    set -e
    RG=test
    LOCATION=westeurope
    AGS=ygtestgrafana
    az group create -g $RG -l $LOCATION

    # Create a grafana instance. Managed Identity is enabled by default. Roles assignments are created for both the command user and managed identity
    # Use "--skip-system-assigned-identity" and "--skip-role-assignments" to skip them, and use "az role assignment create" for finer control
    az grafana create -g $RG -n $AGS
    az grafana show -n $AGS

    # wait for 2 minutes for RBAC to propagate the change
    sleep 2m

    # Create a folder
    FOLDER=testSQL
    folder_id=$(az grafana folder create -n $AGS --title $FOLDER --query "id" -otsv)
    az grafana folder show -n $AGS --folder $folder_id

    # Configure a Azure SQL data source and test the connection
    data_source_id=$(az grafana data-source create -n $AGS --definition /mnt/d/work/cli/data-source-sql.json --query "id" -o tsv)
    az grafana data-source show -n $AGS --data-source $data_source_id
    az grafana data-source query -n $AGS --data-source $data_source_id --query-format table  --conditions rawSql="SELECT 1"

    # Configure data dashboard under the folder
    data_dashboard_uid=$(az grafana dashboard create -n $AGS --folder $FOLDER --title "test dashboard" --definition /mnt/d/work/cli/dashboard-sql.json --query "uid" -o tsv)
    ## Please note the "=" between arg name and parameter. This is to avoid a CLI bug caused by potential leading "-" in uid
    az grafana dashboard show -n $AGS --dashboard="$data_dashboard_uid"

    ## tear down
    az grafana dashboard delete -n $AGS --dashboard="$data_dashboard_uid"
    az grafana folder delete -n $AGS --folder $FOLDER

    az grafana delete -n $AGS --yes
```

Notes:
1.	I didn’t strictly follow the APIs; rather do what are needed for users to set up managed Grafana instances during infra built out. Do let me know any coverage gap
2.	Dashboard provisioning is the hard part as Grafana doesn’t have strong schema to support scaffolding through CLI, though it is being improved. So current commands provide the bare minimum by letting you provide a json model. Realistically, you can use “show” command or capture payload in the browser and use it as baseline to apply you change. 
3.	The “uid” of Grafana artifact exposes a CLI bug that the leading “-” will break the command parser. For now, either follow the workaround mentioned above by using "=" between arg and parameter, or use other identifier such as id or name which CLI supports
4.	Grafana list/show commands output a few empty fields. This will be fixed through Grafana Python SDK which will be ready in March
