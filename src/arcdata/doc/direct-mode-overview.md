

## Supported Direct / ARM commands


### Known / Pending issues

1. No `az sql mi-arc upgrade` or `az arcdata dc upgrade` for **direct-mode** current, only indirect. This feature will come is this week.
2. You **must** first create a `--custom-location`. We will also be fixing this as well post bug-bash
3. `az arcdata dc upload` STILL uses SPN to authenticate. We also will be fixing this to use our new auth-workflow that does not require the tuple.
4. Mutually exclusive argument validation is not in place meaning some commands are only applicable to `direct` or `indirect` but not both. In this case they are just ignored. We will fix this to raise mutually exclusive argument errors.
5. We have not deprecated/routed `az sql mi-arc edit` to `az sql mi-arc update` yet.
6. Add better [--help] examples for direct mode.

### Command Overview


- [--use-k8s] implies indirect local kubernetes 
- If you leave off [--use-k8s] it will execute against direct / ARM

> NOTE: To use az direct mode commands, run `az login` first.

> NOTE: You must have the [--custom-location] previously created. We will be fixing this to handel the 3 in 1 usecase.

> NOTE: Mutually exclusive arguments are identified via [--help] in their own group, for example:
```
>  az arcdata dc create --help

Direct mode Arguments
    --custom-location              : Custom location.
    --enable-auto-upload-logs      : Enable auto upload logs.
    --enable-auto-upload-metrics   : Enable auto upload metrics.

Indirect mode Arguments
    --k8s-namespace -k             : The Kubernetes namespace to deploy the data controller into. If
                                     it exists already it will be used. If it does not exist, an
                                     attempt will be made to create it first.
    --use-k8s                      : Create data controller using local Kubernetes APIs.

...
...
...

```


**DC:**
```
az login
az arcdata dc create -n <your_dc_instance_name> --connectivity-mode direct --resource-group <your_resource_group_name> -l <your_instance_location_name> --custom-location <your_custom_location_name>
az arcdata dc delete -n <your_dc_instance_name> --resource-group <your_resource_group_name>
az arcdata dc status show  -n <your_dc_instance_name> --resource-group <your_resource_group_name>
```

**SQLMI**
```
az login
az sql mi-arc create -n <your_sqlmi_instance_name> --resource-group <your_resource_group_name> --location <your_instance_location_name>  --custom-location <your_custom_location_name> 
az sql mi-arc delete -n <your_sqlmi_instance_name> --resource-group <your_resource_group_name>
az sql mi-arc show -n <your_sqlmi_instance_name> --resource-group <your_resource_group_name>
az sql mi-arc list --resource-group <your_resource_group_name> 
az sql mi-arc edit --resource-group <your_resource_group_name> -n <your_dc_instance_name> --custom-location <your_custom_location_name> --tag-name <your_tag_name>--tag-value <your_tag_value> 
```

#### Full argument permutation for sql mi-arc create/edit

 
Command example with full args for `az sql mi-arc create`:
 
```
az sql mi-arc create -n <your_sqlmi_instance_name> --resource-group <your_resource_group_name> --location <your_instance_location_name>  --custom-location <your_custom_location_name> --cores-limit 4 --cores-request 2 --memory-limit 8Gi --memory-request 4Gi --storage-class-data slow --storage-class-logs slow --storage-class-datalogs slow --storage-class-backups slow --volume-size-data 5Gi --volume-size-logs 5Gi --volume-size-datalogs 5Gi --no-wait --no-external-endpoint --cert-public-key-file  xxx --cert-private-key-file xxx --service-cert-secret xxx --admin-login-secret xxx --license-type LicenseIncluded --tier GeneralPurpose --dev --labels testlable --annotations testAnno --service-labels serviceLabel --service-annotations serviceAnno --storage-labels storeLable --storage-annotations storeAnno --collation coll --language English --agent-enabled True --trace-flags True --time-zone <your_instance_location_time> --retention-days rd 
```

Full function of az `sql mi-arc edit`:


```
az sql mi-arc edit --resource-group  <> -n <your_sqlmi_instance_name> --location <location> --custom-location <custom-location > --tag-name <> --tag-value <> --cores-limit <> --cores-request 2 --memory-limit 8Gi --memory-request 4Gi --labels testlable --annotations testAnno --service-labels serviceLabel --service-annotations serviceAnno --trace-flags True --time-zone eastus --retention-days rd --preferred-primary-replica <sqlexample1-0> --primary-replica-failover-interval <600>
```
