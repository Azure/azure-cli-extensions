Microsoft Azure CLI 'hack' extension
=========================================

A bootstrapping application for quickly creating `web space <https://azure.microsoft.com/en-us/services/app-service/>`_, a database (Cosmos DB, SQL Server, or MySQL), and a `Cognitive Services <https://azure.microsoft.com/en-us/services/cognitive-services/>`_ key.

Creates an Resource Group, an App Service Plan and App Service, database server and database, and optionally enables Cognitive Services. All items are placed in a single resource group for easy cleanup post hack. Uses **Standard** pricing.

-----
Usage
-----

::
    az hack create -n demoname -d MySQL -r python -ai

--------
Switches
--------

**--name -n**
Name of the application. This will be used to name the Resource Group, App Service Plan, App Service, database server and database. Name must contain only letters and numbers, and start with a letter.

**--runtime -r**
Runtime of the web application. Options are *python*, *php*, *aspnet*, *node*, *tomcat*, *jetty*.

**--database -d**
Database to create. Options are *mysql*, *sql*, or *cosmosdb*.

**--ai -ai**
Create a Cognitive Services key (optional).
