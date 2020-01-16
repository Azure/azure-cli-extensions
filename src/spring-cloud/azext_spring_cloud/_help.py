# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['spring-cloud'] = """
    type: group
    short-summary: Commands to manage Azure Spring Cloud.
"""

helps['spring-cloud create'] = """
    type: command
    short-summary: Create an Azure Spring Cloud.
    examples:
    - name: Create a new Azure Spring Cloud in westus.
      text: az spring-cloud create -n MyService -g MyResourceGroup -l westus
"""

helps['spring-cloud delete'] = """
    type: command
    short-summary: Delete an Azure Spring Cloud.
"""

helps['spring-cloud list'] = """
    type: command
    short-summary: List all Azure Spring Cloud in the given resource group, otherwise list the subscription's.
"""

helps['spring-cloud show'] = """
    type: command
    short-summary: Show the details for an Azure Spring Cloud.
"""

helps['spring-cloud test-endpoint'] = """
    type: group
    short-summary: Commands to manage test endpoint in Azure Spring Cloud.
"""

helps['spring-cloud test-endpoint enable'] = """
    type: command
    short-summary: Enable test endpoint of the Azure Spring Cloud.
"""

helps['spring-cloud test-endpoint disable'] = """
    type: command
    short-summary: Disable test endpoint of the Azure Spring Cloud.
"""

helps['spring-cloud test-endpoint list'] = """
    type: command
    short-summary: List test endpoint keys of the Azure Spring Cloud.
"""

helps['spring-cloud test-endpoint renew-key'] = """
    type: command
    short-summary: Regenerate a test-endpoint key for the Azure Spring Cloud.
"""

helps['spring-cloud app'] = """
    type: group
    short-summary: Commands to manage apps in Azure Spring Cloud.
"""

helps['spring-cloud app create'] = """
    type: command
    short-summary: Create a new app with a default deployment in the Azure Spring Cloud.
    examples:
    - name: Create an app with the default configuration.
      text: az spring-cloud app create -n MyApp -s MyCluster -g MyResourceGroup
    - name: Create an public accessible app with 3 instances and 2 cpu cores and 3 GB of memory per instance.
      text: az spring-cloud app create -n MyApp -s MyCluster -g MyResourceGroup --is-public true --cpu 2 --memory 3 --instance-count 3
"""

helps['spring-cloud app update'] = """
    type: command
    short-summary: Update configurations of an app.
    examples:
    - name: Add an environment variable for the app.
      text: az spring-cloud app update -n MyApp -s MyCluster -g MyResourceGroup --env foo=bar
"""

helps['spring-cloud app delete'] = """
    type: command
    short-summary: Delete an app in the Azure Spring Cloud.
"""

helps['spring-cloud app list'] = """
    type: command
    short-summary: List all apps in the Azure Spring Cloud.
    examples:
    - name: Query status of persistent storage of all apps
      text: az spring-cloud app list -s MyCluster -g MyResourceGroup -o json --query '[].{Name:name, PersistentStorage:properties.persistentDisk}'
"""

helps['spring-cloud app show'] = """
    type: command
    short-summary: Show the details of an app in the Azure Spring Cloud.
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
      text: az spring-cloud app deploy -n MyApp -s MyCluster -g MyResourceGroup
    - name: Deploy a pre-built jar to an app with jvm options and environment variables.
      text: az spring-cloud app deploy -n MyApp -s MyCluster -g MyResourceGroup --jar-path app.jar --jvm-options="-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
    - name: Deploy source code to a specific deployment of an app.
      text: az spring-cloud app deploy -n MyApp -s MyCluster -g MyResourceGroup -d green-deployment
"""

helps['spring-cloud app scale'] = """
    type: command
    short-summary: Manually scale an app or its deployments.
    examples:
    - name: Scale up an app to 4 cpu cores and 8 Gb of memory per instance.
      text: az spring-cloud app scale -n MyApp -s MyCluster -g MyResourceGroup --cpu 3 --memory 8
    - name: Scale out a deployment of the app to 5 instances.
      text: az spring-cloud app scale -n MyApp -s MyCluster -g MyResourceGroup -d green-deployment --instance-count 5
"""

helps['spring-cloud app show-deploy-log'] = """
    type: command
    short-summary: Show build log of the last deploy, only apply to source code deploy, default to production deployment.
"""

helps['spring-cloud app log tail'] = """
    type: command
    short-summary: Show logs of an app or a instance, logs will be streamed when set --follow.
"""

helps['spring-cloud app set-deployment'] = """
    type: command
    short-summary: Set production deployment of an app.
    examples:
    - name: Swap a staging deployment of an app to production.
      text: az spring-cloud app set-deployment -d green-deployment -n MyApp -s MyCluster -g MyResourceGroup
"""


helps['spring-cloud app log'] = """
    type: group
    short-summary: Commands to tail app instances logs with multiple options. If the app has only one instance, the instance name is optional.
"""


helps['spring-cloud app deployment'] = """
    type: group
    short-summary: Commands to manage life cycle of deployments of an app in Azure Spring Cloud. More operations on deployments can be done on app level with parameter --deployment. e.g. az spring-cloud app deploy --deployment <staging deployment>
"""

helps['spring-cloud app deployment list'] = """
    type: command
    short-summary: List all deployments in an app.
"""

helps['spring-cloud app deployment show'] = """
    type: command
    short-summary: Show details of a deployment.
"""

helps['spring-cloud app deployment delete'] = """
    type: command
    short-summary: Delete a deployment of the app.
"""

helps['spring-cloud app deployment create'] = """
    type: command
    short-summary: Create a staging deployment for the app. To deploy code or update setting to an existing deployment, use az spring-cloud app deploy/update --deployment <staging deployment>.
    examples:
    - name: Deploy source code to a new deployment of an app. This will pack current directory, build binary with Pivotal Build Service and then deploy.
      text: az spring-cloud app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup
    - name: Deploy a pre-built jar to an app with jvm options and environment variables.
      text: az spring-cloud app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --jar-path app.jar --jvm-options="-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
"""

helps['spring-cloud config-server'] = """
    type: group
    short-summary: Commands to manage Config Server in Azure Spring Cloud.
"""

helps['spring-cloud config-server show'] = """
    type: command
    short-summary: Show Config Server.
"""

helps['spring-cloud config-server set'] = """
    type: command
    short-summary: Set Config Server from a yaml file.
"""

helps['spring-cloud config-server clear'] = """
    type: command
    short-summary: Erase all settings in Config Server.
"""

helps['spring-cloud config-server git'] = """
    type: group
    short-summary: Commands to manage Config Server git property in Azure Spring Cloud.
"""

helps['spring-cloud config-server git repo'] = """
    type: group
    short-summary: Commands to manage Config Server git repository in Azure Spring Cloud.
"""

helps['spring-cloud config-server git set'] = """
    type: command
    short-summary: Set git property of Config Server, will totally override the old one.
"""

helps['spring-cloud config-server git repo add'] = """
    type: command
    short-summary: Set add a new repositry of git property of Config Server.
"""

helps['spring-cloud config-server git repo remove'] = """
    type: command
    short-summary: Remove an existing repositry of git property of Config Server.
"""

helps['spring-cloud config-server git repo update'] = """
    type: command
    short-summary: Override an existing repositry of git property of Config Server, will totally override the old one.
"""

helps['spring-cloud config-server git repo list'] = """
    type: command
    short-summary: List all repositries of git property of Config Server.
"""

helps['spring-cloud app binding'] = """
    type: group
    short-summary: Commands to manage bindings with Azure Data Services, you need to manually restart app to make settings take effect.
"""

helps['spring-cloud app binding cosmos'] = """
    type: group
    short-summary: Commands to manage Azure Cosmos DB bindings.
"""

helps['spring-cloud app binding mysql'] = """
    type: group
    short-summary: Commands to manage Azure Database for MySQL bindings.
"""

helps['spring-cloud app binding redis'] = """
    type: group
    short-summary: Commands to manage Azure Cache for Redis bindings.
"""
helps['spring-cloud app binding list'] = """
    type: command
    short-summary: List all service bindings in an app.
"""

helps['spring-cloud app binding show'] = """
    type: command
    short-summary: Show the details of a service binding.
"""
helps['spring-cloud app binding remove'] = """
    type: command
    short-summary: Remove a service binding of the app.
"""

helps['spring-cloud app binding cosmos add'] = """
    type: command
    short-summary: Bind an Azure Cosmos DB with the app.
    examples:
    - name: Bind an Azure Cosmos DB.
      text: az spring-cloud app binding cosmos add -n cosmosProduction --app MyApp --resource-id ${COSMOSDB_ID} --api-type mongo --database mymongo -g MyResourceGroup -s MyService
"""

helps['spring-cloud app binding cosmos update'] = """
    type: command
    short-summary: Update an Azure Cosmos DB service binding of the app.
"""

helps['spring-cloud app binding mysql add'] = """
    type: command
    short-summary: Bind an Azure Database for MySQL with the app.
"""

helps['spring-cloud app binding mysql update'] = """
    type: command
    short-summary: Update an Azure Database for MySQL service binding of the app.
"""

helps['spring-cloud app binding redis add'] = """
    type: command
    short-summary: Bind an Azure Cache for Redis with the app.
"""

helps['spring-cloud app binding redis update'] = """
    type: command
    short-summary: Update an Azure Cache for Redis service binding of the app.
"""
