# Azure CLI Workloads Extension #
This is an extension to Azure CLI to manage Workloads resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name workloads
```

### Included Features ###
#### workloads ####
##### sap-disk-configuration #####
```
az workloads sap-disk-configuration --app-location "northeurope" --database-type "HANA" --db-vm-sku "Standard_M32ts" --deployment-type "SingleServer" --environment "NonProd" --sap-product "S4HANA" --location "northeurope"

```

##### sap-sizing-recommendation #####
```
az workloads sap-sizing-recommendation --app-location "northeurope" --database-type "HANA" --db-memory 2000 --deployment-type "SingleServer" --environment "NonProd" --sap-product "S4HANA" --saps 60000 --location "northeurope"

```
##### sap-supported-sku #####
```
az workloads sap-supported-sku --app-location "eastus2" --database-type "HANA" --deployment-type "SingleServer" --environment "NonProd" --sap-product "S4HANA" --location "eastus2"

```

#### sap-virtual-instance ####
##### Create #####
```
az workloads sap-virtual-instance create -g rg -n instance-name --environment Nonprod --sap-product s4hana --configuration D:\create_infra_distributed_non_ha_config.json

```

##### Delete #####
```
az workloads sap-virtual-instance delete -g rg -n instance-name -y

```

##### List #####
```
az workloads sap-virtual-instance list -g rg

```

##### Show #####
```
az workloads sap-virtual-instance show -g rg -n instance-name

```

##### Start #####
```
az workloads sap-virtual-instance start -g rg --vis-name name

```

##### Stop #####
```
az workloads sap-virtual-instance stop -g rg --vis-name name

```

##### update #####
```
az workloads sap-virtual-instance update -g rg -n instance-name --tags "{tag:tag}"

```

#### sap-database-instance ####
##### List #####
```
az workloads sap-database-instance list -g rg --vis-name name

```

##### Show #####
```
az workloads sap-database-instance show -g rg -n instance-name --vis-name name

```

##### Start #####
```
az workloads sap-database-instance start -g rg -n instance-name --vis-name name

```

##### Stop #####
```
az workloads sap-database-instance stop -g rg -n instance-name --vis-name name

```

##### Update #####
```
az workloads sap-database-instance update -g rg -n instance-name --vis-name name --tags "{tag:tag}"

```

#### sap-central-instance ####
##### List #####
```
az workloads sap-central-instance list -g rg --vis-name name

```

##### Show #####
```
az workloads sap-central-instance show -g rg -n instance-name --vis-name name

```

##### Start #####
```
az workloads sap-central-instance start -g rg -n instance-name --vis-name name

```

##### Stop #####
```
az workloads sap-central-instance stop -g rg -n instance-name --vis-name name

```

##### Update #####
```
az workloads sap-central-instance update -g rg -n instace-name --vis-name name --tags "{tag:tag}"

```

#### sap-application-server-instance ####
##### List #####
```
az workloads sap-application-server-instance list -g rg --vis-name name

```

##### Show #####
```
az workloads sap-application-server-instance show -g rg -n instance-name --vis-name name

```

##### Start #####
```
az workloads sap-application-server-instance start -g rg -n instance-name --vis-name name

```

##### Stop #####
```
az workloads sap-application-server-instance stop -g rg -n instance-name --vis-name name

```

##### Update #####
```
az workloads sap-application-server-instance update -g rg -n instance-name --vis-name name --tags "{tag:tag}"

```

#### monitor ####
##### Create #####
```
az workloads monitor create -n monitor-name -g rg --app-location westus --managed-rg-name rg-name

```

##### Celete #####
```
az workloads monitor delete -n monitor-name -g rg -y

```

##### List #####
```
az workloads monitor list -g rg

```

##### Show #####
```
az workloads monitor show -g rg -n monitor-name

```

##### Update #####
```
az workloads monitor update -g rg -n monitor-name --tags "{tag:tag1}"

```

#### provider-instance ####
##### Create #####
```
az workloads monitor provider-instance create -g rg --mointor-name name -n instance-name --provider-settings "{sapHana:{hostname:name,dbName:db,sqlPort:0000,instanceNumber:00,dbUsername:user,dbPassword:****,sslPreference:ServerCertificate,sslCertificateUri:'https://storageaccount.blob.core.windows.net/containername/filename',sslHostNameInCertificate:xyz.domain.com,sapSid:SID}}"

```

##### Delete #####
```
az workloads monitor provider-instance delete -g rg --monitor-name name -n instance-name -y

```

##### List #####
```
az workloads monitor provider-instance list -g rg --monitor-name name

```

##### Show #####
```
az workloads monitor provider-instance show -g rg --monitor-name name -n instance-name

```

#### sap-landscape-monitor ####
##### Create #####
```
az workloads monitor sap-landscape-monitor create -g rg --monitor-name name --grouping "{landscape:[{name:Prod,topSid:[SID1,SID2]}],sapApplication:[{name:ERP1,topSid:[SID1,SID2]}]}" --top-metrics-thresholds "[{name:Inscane, green:90,yellow:75,red:50}]"

```

##### Delete #####
```
az workloads monitor sap-landscape-monitor delete -g rg --monitor-name name -y

```

##### List #####
```
az workloads monitor sap-landscape-monitor list -g rg --monitor-name name

```

##### Show #####
```
az workloads monitor sap-landscape-monitor show -g rg --monitor-name name

```

##### Update #####
```
az workloads monitor sap-landscape-monitor update -g rg --monitor-name name --grouping "{landscape:[{name:Prod,topSid:[SID1,SID2]}],sapApplication:[{name:ERP1,topSid:[SID1,SID2]}]}" --top-metrics-thresholds "[{name:Inscane, green:90,yellow:75,red:50}]"

```
