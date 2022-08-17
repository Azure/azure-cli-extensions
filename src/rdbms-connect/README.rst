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
    az postgres flexible-server connect -n testServer -u username -p password

::
    az mysql flexible-server connect -n testServer -u username -p password

::
    az postgres flexible-server connect -n testServer -u username --interactive

::
    az mysql flexible-server connect -n testServer -u username --interactive

::
    az postgres flexible-server execute -n testServer -u username -p password --querytext "select * from pg_user;" --output table

::
    az mysql flexible-server execute -n testServer -u username -p password --querytext "select host, user from mysql.user;" --output table

::
    az postgres flexible-server execute -n testServer -u username -p password --file-path "./test.sql"

::
    az mysql flexible-server execute -n testServer -u username -p password --file-path "./test.sql"

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

**--querytext -q**
A query to run against the flexible server. 

**--file-path -f**
A sql file to run against the flexible server. 