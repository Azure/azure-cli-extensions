# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['spring-cloud'] = """
    type: group
    short-summary: Commands to manage Azure Spring Cloud Service.
"""

helps['spring-cloud create'] = """
    type: command
    short-summary: Create an Azure Spring Cloud Service.
    examples:
    - name: Create a new Azure Spring Cloud Service in westus.
      text: az spring-cloud create -n MyService -g MyResourceGroup -l westus      
"""

helps['spring-cloud delete'] = """
    type: command
    short-summary: Delete an Azure Spring Cloud Service.
"""

helps['spring-cloud list'] = """
    type: command
    short-summary: List all Azure Spring Cloud Services in the given resource group, otherwise list the subscription's.
"""

helps['spring-cloud show'] = """
    type: command
    short-summary: Show the details for an Azure Spring Cloud Service.
"""

helps['spring-cloud test-endpoint'] = """
    type: group
    short-summary: Commands to manage test-endpoint in Azure Spring Cloud Service.
"""

helps['spring-cloud test-endpoint enable'] = """
    type: command
    short-summary: Enable test endpoint of the Azure Spring Cloud Service.
"""

helps['spring-cloud test-endpoint disable'] = """
    type: command
    short-summary: Disable test endpoint of the Azure Spring Cloud Service.
"""

helps['spring-cloud test-endpoint list'] = """
    type: command
    short-summary: List test endpoint keys of the Azure Spring Cloud Service.
"""

helps['spring-cloud test-endpoint renew-key'] = """
    type: command
    short-summary: Regenerate a test-endpoint key for the Azure Spring Cloud Service.
"""

helps['spring-cloud app'] = """
    type: group
    short-summary: Commands to manage apps in Azure Spring Cloud Service.
"""

helps['spring-cloud app create'] = """
    type: command
    short-summary: Create a new app with a default deployment in the Azure Spring Cloud Service.
    examples:
    - name: Create an app with the default configuration.
      text: az spring-cloud app create -n MyApp -s Myspring-cloud
    - name: Create an public accessible app with 3 instance and 2 cpu cores and 3 Gb of memory per instance.
      text: az spring-cloud app create -n MyApp -s Myspring-cloud --is-public true --cpu 2 --memory 3 --instance-count 3 
"""

helps['spring-cloud app update'] = """
    type: command
    short-summary: Update configurations of an app.
    examples:
    - name: Add an enviroment variable for the app.
      text: az spring-cloud app update --env foo=bar
"""

helps['spring-cloud app delete'] = """
    type: command
    short-summary: Delete an app in the Azure Spring Cloud Service.
"""

helps['spring-cloud app list'] = """
    type: command
    short-summary: List all apps in the Azure Spring Cloud Service.
    examples:
    - name: Query status of persistent storage of all apps
      text: az asc app list -s Myspring-cloud -o json --query '[].{Name:name, PersistentStorage:properties.persistentDisk}'
"""

helps['spring-cloud app show'] = """
    type: command
    short-summary: Show the details of an app in the Azure Spring Cloud Service.
"""

helps['spring-cloud app start'] = """
    type: command
    short-summary: Start instances of the app, default to production deployment.
"""

helps['spring-cloud app stop'] = """
    type: command
    short-summary: Stop instances of the app, default to production deployment.
"""

helps['spring-cloud app restart'] = """
    type: command
    short-summary: Restart instances of the app, default to production deployment.
"""

helps['spring-cloud app deploy'] = """
    type: command
    short-summary: Deploy source code or pre-built binary to an app and update related configurations.
    examples:
    - name: Deploy source code to an app. This will pack current directory, build binary with Pivotal Build Service and then deploy to the app.
      text: az spring-cloud app deploy -n MyApp -s Myspring-cloud
    - name: Deploy a pre-built jar to an app with jvm options and environment variables.
      text: az spring-cloud app deploy -n MyApp -s Myspring-cloud --jar-path app.jar --jvm-options "-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
    - name: Deploy source code to a specific deployment of an app.
      text: az spring-cloud app deploy -n MyApp -s Myspring-cloud -d green-deployment
"""

helps['spring-cloud app scale'] = """
    type: command
    short-summary: Manually scale an app or its deployments.
    examples:
    - name: Scale up an app to 4 cpu cores and 8 Gb of memory per instance.
      text: az spring-cloud app scale -n MyApp -s Myspring-cloud --cpu 3 --memory 8
    - name: Scale out a deployment of the app to 5 instances.
      text: az spring-cloud app scale -n MyApp -s Myspring-cloud -d green-deployment --instance-count 5
"""

helps['spring-cloud app show-deploy-log'] = """
    type: command
    short-summary: Show a specificed deployment's log of the app, default to production deployment.
"""

helps['spring-cloud app set-deployment'] = """
    type: command
    short-summary: Set production deployment of an app.
    examples:
    - name: Swap a staging deployment of an app to production.
      text: az spring-cloud app set-deployment -d green-deployment -n MyApp -s Myspring-cloud
"""

helps['spring-cloud app deployment'] = """
    type: group
    short-summary: Commands to manage life cycle of deployments of an app in Azure Spring Cloud service. More operations on deployments can be done on app level with parameter --deployment. e.g. az spring-cloud app deploy --deployment <staging deployment>
"""

helps['spring-cloud app deployment list'] = """
    type: command
    short-summary: List all deployments in an app.
"""

helps['spring-cloud app deployment show'] = """
    type: command
    short-summary: Show the details of a deployment.
"""

helps['spring-cloud app deployment delete'] = """
    type: command
    short-summary: Delete a deployment of the app.
"""

helps['spring-cloud app deployment create'] = """
    type: command
    short-summary: Create a staging deployment for the app. To deploy code or update setting to an existing deployment, use: az spring-cloud app deploy/update --deployment <staging deployment>.
    examples:
    - name: Deploy source code to a new deployment of an app. This will pack current directory, build binary with Pivotal Build Service and then deploy.
      text: az spring-cloud app deployment create -n green-deployment --app MyApp -s Myspring-cloud
    - name: Deploy a pre-built jar to an app with jvm options and environment variables.
      text: az spring-cloud app deployment create -n green-deployment --app MyApp -s Myspring-cloud --jar-path app.jar --jvm-options "-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
"""

helps['spring-cloud config-server'] = """
    type: group
    short-summary: Commands to manage config server in Azure Spring Cloud Service.
"""

helps['spring-cloud config-server show'] = """
    type: command
    short-summary: Commands to show config server.
"""

helps['spring-cloud config-server set'] = """
    type: command
    short-summary: Commands to set config server.
"""

helps['spring-cloud config-server clear'] = """
    type: command
    short-summary: Commands to clear config server.
"""

helps['spring-cloud config-server git'] = """
    type: group
    short-summary: Commands to manage config server git property in Azure Spring Cloud Service.
"""


helps['spring-cloud config-server git set'] = """
    type: command
    short-summary: Commands to set git property of config server, will totally override the old one.
"""

helps['spring-cloud config-server git repo add'] = """
    type: command
    short-summary: Commands to set add a new repositry of git property of config server.
"""

helps['spring-cloud config-server git repo remove'] = """
    type: command
    short-summary: Commands to remove an existing repositry of git property of config server.
"""

helps['spring-cloud config-server  git repo update'] = """
    type: command
    short-summary: Commands to override an existing repositry of git property of config server, will totally override the old one.
"""

helps['spring-cloud config-server git repo list'] = """
    type: command
    short-summary: Commands to list all repositries of git property of config server.
"""

helps['spring-cloud app binding'] = """
    type: group
    short-summary: Commands to manage service bindings of an app in Azure Spring Cloud Service, and only restart app can make settings take effect.
"""

helps['spring-cloud app binding cosmos'] = """
    type: group
    short-summary: Commands to manage cosmosdb bindings.
"""

helps['spring-cloud app binding mysql'] = """
    type: group
    short-summary: Commands to manage mysql bindings.
"""

helps['spring-cloud app binding redis'] = """
    type: group
    short-summary: Commands to manage redis bindings.
"""
helps['spring-cloud app binding list'] = """
    type: command
    short-summary: List all service bindings in an app.
"""

helps['spring-cloud app binding show'] = """
    type: command
    short-summary: Show the details of a service binding.
"""
helps['spring-cloud app binding delete'] = """
    type: command
    short-summary: Delete a service binding of the app.
"""

helps['spring-cloud app binding cosmos add'] = """
    type: command
    short-summary: Bind an Azure Cosmos DB service with the app.
    examples:
    - name: Bind an Azure Cosmos DB service.
      text: az spring-cloud app binding cosmos create -n mysqlProduction --app MyApp --resource-id ${COSMOSDB_ID} --api-type mongo --database mymongo
"""

helps['spring-cloud app binding cosmos update'] = """
    type: command
    short-summary: Update an Azure Cosmos DB service binding of the app.
"""

helps['spring-cloud app binding mysql add'] = """
    type: command
    short-summary: Bind an Azure DB for MySQL service with the app.
"""

helps['spring-cloud app binding mysql update'] = """
    type: command
    short-summary: Update an Azure DB for MySQL service binding of the app.
"""

helps['spring-cloud app binding redis add'] = """
    type: command
    short-summary: Bind an Azure Redis Cache service with the app.
"""

helps['spring-cloud app binding redis update'] = """
    type: command
    short-summary: Update an Azure Redis Cache service binding of the app.
"""
