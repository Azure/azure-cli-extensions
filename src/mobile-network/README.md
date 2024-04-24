# Azure CLI Mobile Network #
This is an extension to Azure CLI to manage mobile network resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name mobile-network
```

### Included Features ###
#### mobile-network ####
##### Create #####
```
az mobile-network create -n mobile-network-name -g rg --identifier "{mcc:001,mnc:01}"

```
##### Show #####
```
az mobile-network show -n mobile-network-name -g rg
```
##### List #####
```
az mobile-network list -g rg
```
##### Update #####
```
az mobile-network update -n mobile-network-name -g rg --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network delete -n mobile-network-name -g rg -y

```

#### attached-data-network ####
##### Create #####
```
az mobile-network attached-data-network create -n data-network-name -g rg --pccp-name pccp-name --pcdp-name pcdp-name --dns-addresses "[1.1.1.1]" --data-interface " {name:N2,ipv4Address:10.28.128.2,ipv4Subnet:10.28.128.0/24,ipv4Gateway:10.28.128.1}"

```
##### Show #####
```
az mobile-network attached-data-network show -n data-network-name --pccp-name pccp-name --pcdp-name pcdp-name -g rg
```
##### List #####
```
az mobile-network attached-data-network list -g rg --pccp-name pccp-name --pcdp-name pcdp-name
```
##### Update #####
```
az mobile-network attached-data-network update -n data_network-name -g rg --pccp-name pccp-name --pcdp-name pcdp-name --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network attached-data-network delete -n data-network-name --pccp-name pccp-name --pcdp-name pcdp-name -g rg -y

```

#### data-network ####
##### Create #####
```
az mobile-network data-network create -n data-network-name -g rg --mobile-network-name mobile-network-name

```
##### Show #####
```
az mobile-network data-network show -n data-network-name --mobile-network-name mobile-network-name -g rg
```
##### List #####
```
az mobile-network data-network list --mobile-network-name mobile-network-name -g rg
```
##### Update #####
```
az mobile-network data-network update -n data-network-name -g rg --mobile-network-name mobile-network-name --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network data-network delete -n data_network-name --mobile-network-name mobile-network-name -g rg -y

```


#### Packet Core Control Plane ####
##### Create #####
```
az mobile-network pccp create -n pccp-name -g rg --access-interface "{name:N2,ipv4Address:10.28.128.2,ipv4Subnet:10.28.128.0/24,ipv4Gateway:10.28.128.1}" --local-diagnostics "{authentication-type:AAD}" --platform "{type:AKS-HCI}" --sites "[{id:site-id}]" --sku G0

```
##### Show #####
```
az mobile-network pccp show -n pccp-name -g rg
```
##### List #####
```
az mobile-network pccp list -g rg
```
##### Update #####
```
az mobile-network pccp update -n pccp-name -g rg --ue-mtu 1500 --tags "{tag:test,tag2:test2}"
```

##### collect-diagnostics-package #####
```
az mobile-network pccp collect-diagnostics-package --pccp-name pccp -g rg --blob-url https://contosoaccount.blob.core.windows.net/container/diagnosticsPackage.zip
```

##### reinstall #####
```
az mobile-network pccp reinstall --pccp-name pccp-name -g rg
```

##### rollback #####
```
az mobile-network pccp rollback --pccp-name pccp-name -g rg
```

##### Delete #####
```
az mobile-network pccp delete -n pccp-name -g rg -y

```

#### Packet Core Data Plane ####
##### Create #####
```
az mobile-network pcdp create -n pcdp-name -g rg --pccp-name pccp-name --access-interface "{name:N2,ipv4Address:10.28.128.2,ipv4Subnet:10.28.128.0/24,ipv4Gateway:10.28.128.1}"

```
##### Show #####
```
az mobile-network pcdp show -g rg -n pcdp-name --pccp-name pccp-name
```
##### List #####
```
az mobile-network pcdp list -g rg --pccp-name pccp_name
```
##### Update #####
```
az mobile-network pcdp update -n pcdp_name -g rg --pccp-name pccp-name --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network pcdp delete -g rg -n pcdp-name --pccp-name pccp-name -y

```

#### service ####
##### Create #####
```
az mobile-network service create -n service-name -g rg --mobile-network-name mobile-network-name --pcc-rules "[{ruleName:default-rule,rulePrecedence:10,serviceDataFlowTemplates:[{templateName:IP-to-server,direction:Uplink,protocol:[ip],remoteIpList:[10.3.4.0/24]}]}]" --service-precedence 10

```
##### Show #####
```
az mobile-network service show --mobile-network-name mobile-network-name -n service -g rg
```
##### List #####
```
az mobile-network service list --mobile-network-name mobile-network-name -g rg
```
##### Update #####
```
az mobile-network service update --mobile-network-name mobile-network-name -g rg -n service-name --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network service delete --mobile-network-name mobile-network-name -n service -g rg -y

```

#### sim ####
##### Create #####
```
az mobile-network sim create -g rg --sim-group-name sim-group-name -n sim-name --international-msi 0000000000 --operator-key-code 00000000000000000000000000000000 --authentication-key 00000000000000000000000000000000

```
##### Show #####
```
az mobile-network sim show -g rg -n sim-name --sim-group-name sim-group-name
```
##### List #####
```
az mobile-network sim list -g rg --sim-group-name sim-group-name
```

##### Delete #####
```
az mobile-network sim delete -g rg -n sim-name --sim-group-name sim-group-name -y

```

#### sim group ####
##### Create #####
```
az mobile-network sim group create -n sim-group-name -g rg --mobile-network "{id:mobile-network-id}"

```
##### Show #####
```
az mobile-network sim group show -n sim-group-name -g rg
```
##### List #####
```
az mobile-network sim group list -g rg
```
##### Update #####
```
az mobile-network sim group update -n sim-group-name -g rg --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network sim group delete -n sim-group-name -g rg -y

```

#### sim policy ####
##### Create #####
```
az mobile-network sim policy create -g rg -n sim-policy-name --mobile-network-name mobile-network-name --default-slice '{id:slice-id}' --slice-config "[{slice:{id:slice-id},defaultDataNetwork:{id:data-network-id},dataNetworkConfigurations:[{dataNetwork:{id:data-network-id},allowedServices:[{id:service-id}],sessionAmbr:{uplink:'500 Mbps',downlink:'1 Gbps'}}]}]" --ue-ambr "{uplink:'500 Mbps',downlink:'1 Gbps'}"

```
##### Show #####
```
az mobile-network sim policy show -g rg -n sim-policy-name --mobile-network-name mobile-network-name
```
##### List #####
```
az mobile-network sim policy list -g rg --mobile-network-name mobile-network-name
```
##### Update #####
```
az mobile-network sim policy update -g rg-n sim-policy-name --mobile-network-name mobile-network-name --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network sim policy delete -g rg -n sim-policy-name --mobile-network-name mobile-network-name

```

#### site ####
##### Create #####
```
az mobile-network create -n mobile-network-name -g rg --identifier "{mcc:001,mnc:01}"

```
##### Show #####
```
az mobile-network site show--mobile-network-name mobile-network-name -n site-name -g rg
```
##### List #####
```
az mobile-network site list --mobile-network-name mobile-network-name -g rg
```
##### Update #####
```
az mobile-network site update --mobile-network-name mobile-network-name -n site-name -g rg --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network site delete --mobile-network-name mobile-network-name -n site-name -g rg -y'

```

#### slice ####
##### Create #####
```
az mobile-network slice create --mobile-network-name mobile-network-name -n slice-name -g rg --snssai "{sst:1,sd:123abc}"

```
##### Show #####
```
az mobile-network slice show --mobile-network-name mobile=network-name -n slice-name -g rg
```
##### List #####
```
az mobile-network slice list --mobile-network-name mobile-network-name -g rg
```
##### Update #####
```
az mobile-network slice update --mobile-network-name mobile-network-name -n slice-name -g rg --tags "{tag:test,tag2:test2}"
```

##### Delete #####
```
az mobile-network slice delete --mobile-network-name mobilenetwork-name -n slice-name -g rg -y

```
