.. :changelog:

 Release History
===============

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
