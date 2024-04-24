# Azure CLI Dynatrace Extension #
This is an extension to Azure CLI to manage Dynatrace resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name dynatrace
```

### Included Features ###
#### dynatrace monitor ####
##### Create #####
```
az dynatrace monitor create -g rg -n monitor --user-info "{first-name:Alice,last-name:Bobab,email-address:Alice@microsoft.com,phone-number:1234567890,country:US}"
 --plan-data "{usage-type:committed,billing-cycle:Monthly,plan-details:azureportalintegration_privatepreview@TIDhjdtn7tfnxcy,effective-date:2022-08-20}"
  --environment "{single-sign-on:{aad-domains:['abc']}}"

```
##### Show #####
```
az dynatrace monitor show -g rg -n monitor
```
##### List #####
```
az dynatrace monitor list -g rg
```
##### Update #####
```
az dynatrace monitor update -g {rg} -n {monitor} --tags {{env:dev}}
```

##### Delete #####
```
az dynatrace monitor delete -n monitor -g rg -y

```

##### Get-sso-detail #####
```
az dynatrace monitor get-sso-detail -g rg --monitor-name monitor  --user-principal Alice@microsoft.com

```

##### Get-vm-host-payload #####
```
az dynatrace monitor get-vm-host-payload -g rg --monitor-name monitor

```

##### List-app-service #####
```
az dynatrace monitor list-app-service -g rg --monitor-name monitor

```

##### List-host #####
```
az dynatrace monitor list-host -g rg --monitor-name monitor

```

##### List-linkable-environment #####
```
az dynatrace monitor list-linkable-environment -g rg --monitor-name monitor --user-principal Alice@microsoft.com --region eastus2euap

```

##### List-monitored-resource #####
```
az dynatrace monitor list-monitored-resource -g rg --monitor-name monitor

```

#### dynatrace monitor tag-rule ####
##### Create #####
```
az dynatrace monitor tag-rule create -g rg --monitor-name monitor -n default 
--log-rules "{send-aad-logs:enabled,send-subscription-logs:enabled,send-activity-logs:enabled,filtering-tags:[{name:env,value:prod,action:include},{name:env,value:dev,action:exclude}]}"
--metric-rules "{filtering-tags:[{name:env,value:prod,action:include}]}"

```
##### Show #####
```
az dynatrace monitor tag-rule show -g rg --monitor-name monitor -n default
```
##### List #####
```
az dynatrace monitor tag-rule list -g rg --monitor-name monitor
```
##### Update #####
```
az dynatrace monitor tag-rule update -g rg --monitor-name monitor -n default
```

##### Delete #####
```
az dynatrace monitor tag-rule delete -g rg --monitor-name monitor -n default -y

```

#### dynatrace monitor sso-config ####
##### Create #####
```
az dynatrace monitor sso-config create -g rg --monitor-name monitor -n default 
--aad-domains "['mpliftrdt20210811outlook.onmicrosoft.com']" --single-sign-on-url "https://www.dynatrace.io"

```
##### Show #####
```
az dynatrace monitor sso-config show -g rg --monitor-name monitor -n default
```
##### List #####
```
az dynatrace monitor sso-config list -g rg --monitor-name monitor
```
