Microsoft Azure CLI 'hack' extension
=========================================

A bootstrapping application for quickly creating `web space <https://azure.microsoft.com/en-us/services/app-service/>`_, a database (Cosmos DB, SQL Server, or MySQL), and a `Cognitive Services <https://azure.microsoft.com/en-us/services/cognitive-services/>`_ key.

------
Create
------

Creates an Resource Group, an App Service Plan and App Service, database server and database, and optionally enables Cognitive Services. All items are placed in a single resource group for easy cleanup post hack. Uses **Standard** pricing.

-----
Usage
-----

::
    az hack create -n demo -d MySQL -r python --ai

--------
Switches
--------

**--name -n**
Name of the application. This will be used to name the Resource Group, App Service Plan, App Service, database server and database. Name must contain only letters and numbers, and start with a letter.

**--runtime -r**
Runtime of the web application. Options are *python*, *php*, *aspnet*, *node*, *tomcat*, *jetty*.

**--location -l**
Location for the resources to be created. Display all by running *az account list-locations*

**--database -d**
Database to create. Options are *mysql*, *sql*, or *cosmosdb*. (optional)

**--ai**
Create a Cognitive Services key. (optional)

------
Show
------

Show settings and URLs for created resources

-----
Usage
-----

::
    az hack show -n demo

--------
Switches
--------

**--name -n**
Name of the application.
