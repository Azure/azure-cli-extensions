.. :changelog:

Release History
===============
3.3.4
++++++
* Some improvements and issue fixes.

3.3.3
++++++
* Add documentation explaining manual steps required for connecting to SQL database in Fabric.
* Fix PostgreSQL flexible server connection not working due to deprecation of `ad-admin` command.

3.3.1
++++++
* Change Fabric SQL token endpoint for Cloud Shell compatibility.

3.3.0
++++++
* Fix issue with params to support interactive mode for Fabric SQL

3.2.0
++++++
* Introduce support for Fabric SQL as a target service. Introduce new `connstr_props` argument to configure Fabric SQL.

3.1.3
++++++
* Fix argument missing

3.1.2
++++++
* Update dependencies

3.1.1
++++++
* Fix issue

3.1.0
++++++
* Add `az aks connection create`

3.0.2
++++++
* Some improvements and security issue fixes.

3.0.1
++++++
* Some improvements and security issue fixes.

3.0.0
++++++
* Add new param --new to override the existing database user and deprecate Postgres single server

2.0.7
++++++
* Fix argument missing

2.0.6
++++++
* Add create permission in postgresql

2.0.5
++++++
* Bump version

2.0.4
++++++
* Fix PostgreSQL connection string format

2.0.3
++++++
* Prompt confirmation when update PostgreSQL server

2.0.2
++++++
* Fix no attribute error

2.0.1
++++++
* Fix old api-version issue

2.0.0
++++++
* Update to be compatible with Azure CLI 2.60.0

1.0.3
++++++
* Fix no attribute error

1.0.2
++++++
* Bypass error of `az postgres flexible-server db show`

1.0.1
++++++
* Make some improvements to fix non-json output issue

1.0.0
++++++
* Support function app

0.3.13
++++++
* AAD rebranding and make some improvements

0.3.12
++++++
* make some improvements and support slot.

0.3.11
++++++
* make some improvements.

0.3.10
++++++
* make some improvements.

0.3.9
++++++
* Support `--customized-keys` and make some improvements.

0.3.8
++++++
* Make some improvements.

0.3.6
++++++
* Make some improvements.

0.3.5
++++++
* Make some improvements.

0.3.4
++++++
* Make some improvements.

0.3.3
++++++
* Make some improvements.

0.3.2
++++++
* Fix some issues and support Service Principal for local connection.

0.3.1
++++++
* Support User-Assigned Managed Identity and Service Principal.

0.3.0
++++++
* Add extension information in API request.

0.2.2
++++++
* Update dependency psycopg2 to psycopg2-binary.

0.2.1
++++++
* Update SQL connection.

0.2.0
++++++
* Fix some security issues. Prompt confirmation before open all IPs. Add param `--yes` to skip the confirmation. 

0.1.0
++++++
* Initial release.
