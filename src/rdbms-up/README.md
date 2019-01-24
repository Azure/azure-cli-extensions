# Azure CLI RDBMS Up Extension #
This is a extension for simplified RDBMS flows.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name rdbms-up
```

### Included Features
#### MySQL Up:
Ensures a Azure Database for MySQL Server is up and running and configured for immediate use in one easy command:\
*Examples:*\
If needed, the following creates the resource group, MySql server and a sample database. It will also configure firewall-rules to allow for Azure IP addresses as well as that of your local dev box. Information generated from this command is saved, so that when used in the future, the existing resources will be detected.
```
az mysql up
```

Avoid generated default resource names by specifying various parameters/existing resources.
```
az mysql up \
    -g groupName \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```
