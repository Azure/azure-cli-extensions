# Azure CLI DB Up Extension #
This extension enables single commands to create Azure Database server instances with databases. It currently supports Azure Database for MySQL. 

### How to use ###
Install this extension using the below CLI command
```
az extension add --name db-up
```

#### MySQL
Ensures an Azure Database for MySQL server instance is up and running and configured for immediate use with a single command.

This command can be run without any parameters. This will create the resource group, MySQL server instance and a sample database using generated resource names. It will also configure firewall rules to allow IP addresses from Azure as well as your local dev box to access MySQL. Information generated from this command is saved, so that when used in the future, the existing resources will be detected.
```
az mysql up
```

Avoid generated resource names if existing resources are detected or certain parameters are provided.
```
az mysql up \
    -g groupName \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```
