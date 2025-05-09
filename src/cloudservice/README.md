# Azure CLI cloud-service Extension #
This is the extension for cloud-service. Refer to https://azure.microsoft.com/en-us/services/cloud-services/.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name cloud-service
```

Get help of commands and subgroups.
```
az cloud-service -h
az cloud-service role -h
az cloud-service role-instance -h
az cloud-service update-domain -h
```

Create a cloud service.
```
az cloud-service create -g rg -n cs --roles ContosoFrontend:Standard_D1_v2:1:Standard ContosoBackend:Standard_D1_v2:1:Standard --package-url packageurl --configuration config --load-balancer-configurations myLoadBalancer:myfe:publicip:subnetid: myLoadBalancer2:myfe2:::privateip --secrets vault0:cert0:cert1 vault1:cert2:cert3:cert4 --extensions "@extensions.json"
```

`extensions.json` is a file that has the following content. Please replace values with your real values.
```
[
  {
    "properties": {
      "type": "RDP",
      "autoUpgradeMinorVersion": false,
      "protectedSettings": "settings",
      "publisher": "Microsoft.Windows.Azure.Extensions",
      "settings": "settings",
      "typeHandlerVersion": "1.2.1"
    },
    "name": "RDPExtension"
  }
]
```
