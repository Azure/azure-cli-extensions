# Azure CLI postgresqlhsc Extension #
This is the extension for postgresqlhsc

### How to use ###
Install this extension using the below CLI command
```
az extension add --name postgresqlhsc
```

### Included Features ###
#### postgresqlhsc server-group ####
##### Create #####
```
az postgresqlhsc server-group create --location "westus" --administrator-login "citus" \
    --administrator-login-password "password" --availability-zone "1" --backup-retention-days 35 --citus-version "9.5" \
    --enable-mx true --enable-zfs false --postgresql-version "12" \
    --server-role-groups name="" enable-ha=true role="Coordinator" server-count=1 server-edition="GeneralPurpose" storage-quota-in-mb=524288 v-cores=4 \
    --server-role-groups name="" enable-ha=false role="Worker" server-count=3 server-edition="MemoryOptimized" storage-quota-in-mb=524288 v-cores=4 \
    --standby-availability-zone "2" --tags ElasticServer="1" --resource-group "TestGroup" --name "hsctestsg" 
```
##### Create #####
```
az postgresqlhsc server-group create --location "westus" --create-mode "PointInTimeRestore" --enable-mx true \
    --enable-zfs false --point-in-time-utc "2017-12-14T00:00:37.467Z" --source-location "eastus" \
    --source-resource-group-name "SourceGroup" --source-server-group-name "pgtests-source-server-group" \
    --source-subscription-id "dddddddd-dddd-dddd-dddd-dddddddddddd" --resource-group "TestGroup" --name "hsctestsg" 
```
##### List #####
```
az postgresqlhsc server-group list --resource-group "TestGroup"
```
##### Show #####
```
az postgresqlhsc server-group show --resource-group "TestGroup" --name "hsctestsg1"
```
##### Update #####
```
az postgresqlhsc server-group update --location "westus" --server-role-groups name="" role="Worker" server-count=10 \
    --resource-group "TestGroup" --name "hsctestsg" 
```
##### Update #####
```
az postgresqlhsc server-group update --location "westus" --server-role-groups name="" role="Coordinator" v-cores=16 \
    --resource-group "TestGroup" --name "hsctestsg" 
```
##### Update #####
```
az postgresqlhsc server-group update --location "westus" \
    --server-role-groups name="" role="Worker" storage-quota-in-mb=8388608 --resource-group "TestGroup" \
    --name "hsctestsg" 
```
##### Update #####
```
az postgresqlhsc server-group update \
    --maintenance-window custom-window="Enabled" day-of-week=0 start-hour=8 start-minute=0 \
    --resource-group "TestGroup" --name "hsctestsg" 
```
##### Update #####
```
az postgresqlhsc server-group update --administrator-login-password "secret" --backup-retention-days 30 \
    --postgresql-version "12" \
    --server-role-groups name="" enable-ha=false role="Coordinator" server-count=1 server-edition="GeneralPurpose" storage-quota-in-mb=1048576 v-cores=8 \
    --server-role-groups name="" enable-ha=true role="Worker" server-count=4 server-edition="MemoryOptimized" storage-quota-in-mb=524288 v-cores=4 \
    --tags ElasticServer="2" --resource-group "TestGroup" --name "hsctestsg" 
```
##### Restart #####
```
az postgresqlhsc server-group restart --resource-group "TestGroup" --name "hsctestsg1"
```
##### Start #####
```
az postgresqlhsc server-group start --resource-group "TestGroup" --name "hsctestsg1"
```
##### Stop #####
```
az postgresqlhsc server-group stop --resource-group "TestGroup" --name "hsctestsg1"
```
##### Delete #####
```
az postgresqlhsc server-group delete --resource-group "TestGroup" --name "testservergroup"
```
#### postgresqlhsc server ####
##### List #####
```
az postgresqlhsc server list --resource-group "TestGroup" --server-group-name "hsctestsg1"
```
##### Show #####
```
az postgresqlhsc server show --resource-group "TestGroup" --server-group-name "hsctestsg1" --name "hsctestsg1-c"
```
#### postgresqlhsc configuration ####
##### List #####
```
az postgresqlhsc configuration list --resource-group "TestResourceGroup" --server-group-name "hsctestsg" \
    --server-name "testserver" 
```
##### Show #####
```
az postgresqlhsc configuration show --name "array_nulls" --resource-group "TestResourceGroup" \
    --server-group-name "hsctestsg" 
```
##### Update #####
```
az postgresqlhsc configuration update --name "array_nulls" \
    --server-role-group-configurations role="Coordinator" value="on" \
    --server-role-group-configurations role="Worker" value="off" --resource-group "TestResourceGroup" \
    --server-group-name "hsctestsg" 
```
#### postgresqlhsc firewall-rule ####
##### Create #####
```
az postgresqlhsc firewall-rule create --name "rule1" --end-ip-address "255.255.255.255" --start-ip-address "0.0.0.0" \
    --resource-group "TestGroup" --server-group-name "pgtestsvc4" 
```
##### Show #####
```
az postgresqlhsc firewall-rule show --name "rule1" --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### List #####
```
az postgresqlhsc firewall-rule list --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### Delete #####
```
az postgresqlhsc firewall-rule delete --name "rule1" --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
#### postgresqlhsc role ####
##### Create #####
```
az postgresqlhsc role create --password "secret" --resource-group "TestGroup" --name "role1" \
    --server-group-name "pgtestsvc4" 
```
##### List #####
```
az postgresqlhsc role list --resource-group "TestGroup" --server-group-name "pgtestsvc4"
```
##### Delete #####
```
az postgresqlhsc role delete --resource-group "TestGroup" --name "role1" --server-group-name "pgtestsvc4"
```