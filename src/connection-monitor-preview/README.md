# Azure CLI Connection Monitor V2 Extension #
This is an extension to Azure CLI to manage Connection Monitor V2 preview features.  
Connection monitor now supports to create V1 and V2 version of connection monitor.  
- V1 connection monitor supports single source and destination endpoint which comes with V1 argument groups as usual. You can start/stop them.  
- V2 connection monitor supports multiple endpoints and several test protocol which comes with V2 argument groups. You can disable/enable them in test group.  

## How to use ##
First, install the extension:
```
az extension add --name connection-monitor-preview
```

Then, call the help to find out usage:
```
az network watcher connection-monitor -h
```

## Requirements ##
This extension requires `azure-cli >= 2.0.80` and support at most `azure-cli <= 2.0.82`.