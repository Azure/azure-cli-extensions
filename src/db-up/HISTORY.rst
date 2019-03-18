.. :changelog:

 Release History
===============

0.1.8 (2019-3-15)
+++++++++++++++++
* `az mysql/postgres up`: deafult sku to `GP_Gen5_2`.
* `az postgres up`: remove idle transaction session timout config.

0.1.7 (2019-2-28)
+++++++++++++++++
* `az mysql/postgres show-connection-string`: change format to output like `up` commands.

0.1.6 (2019-2-26)
+++++++++++++++++
* `az mysql/postgres show-connection-string` commands to show connection strings without server calls.

0.1.5 (2019-2-1)
++++++++++++++++
* Added Spring JDBC connection string to output.
* Make resource group more apparent in logging.

0.1.4 (2019-1-31)
+++++++++++++++++
* Added `az postgres up` to simplify postgresql server/database creation and configuration
* Added commands: `az mysql/postgres down` to clean up resources and cached information

0.1.3 (2019-1-28)
+++++++++++++++++
* `az mysql up`- minor changes in output

0.1.2 (2019-1-25)
+++++++++++++++++
* `az mysql up`- add host, user and password to table output
* `az mysql up`- adjust connection strings

0.1.1 (2019-1-24)
+++++++++++++++++
* `az mysql up`- create a resource group if a name is provided that is not an existing one
* `az mysql up`- changes to output to only show connection details and enable table format

0.1.0 (2019-1-23)
+++++++++++++++++
* first release with initial `az mysql up` command
