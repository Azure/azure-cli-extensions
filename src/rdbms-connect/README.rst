Microsoft Azure CLI 'rdbms-connect' Extension
==========================================

This extension enables the command to connect to Azure Database for MySQL and Azure Database for PostgreSQL flexible server instances. .  

-----
Usage
-----

To install the extension separately can run:

:: 
    az extension add --name rdbms-connect

Then can run connect commands:

::
    az postgres flexible-server connect -n testServer -u username -p password --postgres-query "select * from pg_user;" --output table

::
    az mysql flexible-server connect -n testServer -u username -p password --mysql-query "select host, user from mysql.user;" --output table

--------
Switches
--------

**--name -n**
Name of the server. The name can contain only lowercase letters, numbers, and the hyphen (-) character. Minimum 3 characters and maximum 63 characters.
Can be pulled from local context.

**--admin-user -u**
The login username of the administrator.
Can be pulled from local context.

**--admin-password -p**
The login password of the administrator. 

**--database-name -d**
(Optional) The name of the database.  Uses default database if no value provided. 

**--postgres-query / --mysql-query -c**
(Optional) A query to run against the flexible server. 