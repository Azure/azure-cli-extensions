# Azure CLI DB Up Extension #
This extension enables single commands to create Azure Database server instances with databases. It currently supports Azure Database for MySQL and PostgreSQL.

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

Clean up the cache and delete the server. Use the `--delete-group` parameter to also delete the resource group saved in the cache.
```
az mysql down \
    --delete-group
```

Show the connection strings for a database without any server calls.
```
az mysql show-connection-string \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```

#### PostgreSQL
Ensures an Azure Database for PostgreSQL server instance is up and running and configured for immediate use with a single command.

This command can be run without any parameters. This will create the resource group, PostgreSQL server instance and a sample database using generated resource names. It will also configure firewall rules to allow IP addresses from Azure as well as your local dev box to access PostgreSQL. Information generated from this command is saved, so that when used in the future, the existing resources will be detected.
```
az postgres up
```

Avoid generated resource names if existing resources are detected or certain parameters are provided.
```
az postgres up \
    -g groupName \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```

Clean up the cache and delete the server. Use the `--delete-group` parameter to also delete the resource group saved in the cache.
```
az postgres down \
    --delete-group
```

Show the connection strings for a database without any server calls.
```
az postgres show-connection-string \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```

#### SQL
Ensures an Azure Database for SQL server instance is up and running and configured for immediate use with a single command.

This command can be run without any parameters. This will create the resource group, SQL server instance and a sample database using generated resource names. It will also configure firewall rules to allow IP addresses from Azure as well as your local dev box to access SQL. Information generated from this command is saved, so that when used in the future, the existing resources will be detected.
```
az sql up
```

Avoid generated resource names if existing resources are detected or certain parameters are provided.
```
az sql up \
    -g groupName \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```

Clean up the cache and delete the server. Use the `--delete-group` parameter to also delete the resource group saved in the cache.
```
az sql down \
    --delete-group
```

Show the connection strings for a database without any server calls.
```
az sql show-connection-string \
    -s serverName \
    -d databaseName \
    -u adminUsername \
    -p adminPassword
```
