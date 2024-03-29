# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['spring'] = """
    type: group
    short-summary: Commands to manage Azure Spring Apps.
"""

helps['spring create'] = """
    type: command
    short-summary: Create an Azure Spring Apps instance.
    examples:
    - name: Create a new Azure Spring Apps in westus.
      text: az spring create -n MyService -g MyResourceGroup -l westus
    - name: Create a new Azure Spring Apps in westus with an existing Application Insights by using the Connection string (recommended) or Instrumentation key.
      text: az spring create -n MyService -g MyResourceGroup -l westus --app-insights-key \"MyConnectionString\"
    - name: Create a new Azure Spring Apps in westus with an existing Application Insights.
      text: az spring create -n MyService -g MyResourceGroup -l westus --app-insights appInsightsName
    - name: Create a new Azure Spring Apps in westus with an existing Application Insights and specify the sampling rate.
      text: az spring create -n MyService -g MyResourceGroup -l westus --app-insights appInsightsName --sampling-rate 10
    - name: Create a new Azure Spring Apps with Application Insights disabled.
      text: az spring create -n MyService -g MyResourceGroup --disable-app-insights
    - name: Create a new Azure Spring Apps with VNet-injected via giving VNet name in current resource group
      text: az spring create -n MyService -g MyResourceGroup --vnet MyVNet --app-subnet MyAppSubnet --service-runtime-subnet MyServiceRuntimeSubnet
    - name: Create a new Azure Spring Apps with VNet-injected via giving subnets resource ID
      text: az spring create -n MyService -g MyResourceGroup --app-subnet /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyVnetRg/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/app --service-runtime-subnet /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyVnetRg/providers/Microsoft.Network/VirtualNetworks/test-vnet/subnets/svc --reserved-cidr-range 10.0.0.0/16,10.1.0.0/16,10.2.0.1/16
    - name: Create a Azure Spring Apps Enterprise instance if the Azure Subscription never hosts Azure Spring Apps Enterprise instance
      text: |
        az provider register -n Microsoft.SaaS
        az term accept --publisher vmware-inc --product azure-spring-cloud-vmware-tanzu-2 --plan asa-ent-hr-mtr
        az spring create -n MyService -g MyResourceGroup --sku Enterprise
    - name: Create a Azure Spring Apps Enterprise instance with Tanzu components enabled.
      text: |
        az provider register -n Microsoft.SaaS
        az term accept --publisher vmware-inc --product azure-spring-cloud-vmware-tanzu-2 --plan asa-ent-hr-mtr
        az spring create -n MyService -g MyResourceGroup --sku Enterprise --enable-application-configuration-service --enable-service-registry --enable-gateway --enable-api-portal --enable-application-live-view  --enable-application-accelerator
"""

helps['spring list-marketplace-plan'] = """
    type: command
    short-summary: (Enterprise Tier Only) List Marketplace plan to be purchased.
    examples:
    - name: List all plans.
      text: az spring list-marketplace-plan -o table
"""

helps['spring list-support-server-versions'] = """
    type: command
    short-summary: (Standard and Basic Tier Only) List supported server versions.
    examples:
    - name: List supported server versions.
      text: az spring list-support-server-versions -o table -s MyService -g MyResourceGroup
"""

helps['spring update'] = """
    type: command
    short-summary: Update an Azure Spring Apps.
    examples:
    - name: Update pricing tier.
      text: az spring update -n MyService --sku Standard -g MyResourceGroup
    - name: Update the tags of the existing Azure Spring Apps.
      text: az spring update -n MyService -g MyResourceGroup --tags key1=value1 key2=value2
    - name: Configure planned maintenance
      text: az spring update -n MyService -g MyResourceGroup --enable-planned-maintenance --planned-maintenance-day Friday --planned-maintenance-start-hour 10
"""

helps['spring delete'] = """
    type: command
    short-summary: Delete an Azure Spring Apps.
"""

helps['spring start'] = """
    type: command
    short-summary: Start an Azure Spring Apps.
"""

helps['spring stop'] = """
    type: command
    short-summary: Stop an Azure Spring Apps.
"""

helps['spring list'] = """
    type: command
    short-summary: List all Azure Spring Apps in the given resource group, otherwise list the subscription's.
"""

helps['spring show'] = """
    type: command
    short-summary: Show the details for an Azure Spring Apps.
"""

helps['spring test-endpoint'] = """
    type: group
    short-summary: Commands to manage test endpoint in Azure Spring Apps.
"""

helps['spring test-endpoint enable'] = """
    type: command
    short-summary: Enable test endpoint of the Azure Spring Apps.
"""

helps['spring test-endpoint disable'] = """
    type: command
    short-summary: Disable test endpoint of the Azure Spring Apps.
"""

helps['spring test-endpoint list'] = """
    type: command
    short-summary: List test endpoint keys of the Azure Spring Apps.
"""

helps['spring test-endpoint renew-key'] = """
    type: command
    short-summary: Regenerate a test-endpoint key for the Azure Spring Apps.
"""

helps['spring flush-virtualnetwork-dns-settings'] = """
    type: command
    short-summary: (Standard and Enterprise Tier Only) Flush Virtual network DNS setting for Azure Spring Apps.
"""

helps['spring storage'] = """
    type: group
    short-summary: Commands to manage Storages in Azure Spring Apps.
"""

helps['spring storage add'] = """
    type: command
    short-summary: Create a new storage in the Azure Spring Apps.
    examples:
    - name: Create a Storage resource with your own storage account.
      text: az spring storage add --storage-type StorageAccount --account-name MyAccountName --account-key MyAccountKey  -g MyResourceGroup -s MyService -n MyStorageName
"""

helps['spring storage update'] = """
    type: command
    short-summary: Update an existing storage in the Azure Spring Apps.
    examples:
    - name: Update a Storage resource with new name or new key.
      text: az spring storage update --storage-type StorageAccount --account-name MyAccountName --account-key MyAccountKey  -g MyResourceGroup -s MyService -n MyStorageName
"""

helps['spring storage show'] = """
    type: command
    short-summary: Get an existing storage in the Azure Spring Apps.
    examples:
    - name: Get a Storage resource.
      text: az spring storage show -g MyResourceGroup -s MyService -n MyStorageName
"""

helps['spring storage list'] = """
    type: command
    short-summary: List all existing storages in the Azure Spring Apps.
    examples:
    - name: List all Storage resources.
      text: az spring storage list -g MyResourceGroup -s MyService
"""

helps['spring storage remove'] = """
    type: command
    short-summary: Remove an existing storage in the Azure Spring Apps.
    examples:
    - name: Remove a Storage resource.
      text: az spring storage remove -g MyResourceGroup -s MyService -n MyStorageName
"""

helps['spring storage list-persistent-storage'] = """
    type: command
    short-summary: List all the persistent storages related to an existing storage in the Azure Spring Apps.
    examples:
    - name: list all the persistent-storage related to an existing storage.
      text: az spring storage list-persistent-storage -g MyResourceGroup -s MyService -n MyStorageName
"""

helps['spring app'] = """
    type: group
    short-summary: Commands to manage apps in Azure Spring Apps.
"""

helps['spring app create'] = """
    type: command
    short-summary: Create a new app with a default deployment in the Azure Spring Apps instance.
    examples:
    - name: Create an app with the default configuration.
      text: az spring app create -n MyApp -s MyCluster -g MyResourceGroup
    - name: Create an public accessible app with 3 instances and 2 cpu cores and 3 GB of memory per instance.
      text: az spring app create -n MyApp -s MyCluster -g MyResourceGroup --assign-endpoint true --cpu 2 --memory 3 --instance-count 3
    - name: Create an app binding to the default Service Registry and Application Configuration Service.
      text: az spring app create -n MyApp -s MyCluster -g MyResourceGroup --bind-service-registry --bind-application-configuration-service
"""

helps['spring app append-persistent-storage'] = """
    type: command
    short-summary: Append a new persistent storage to an app in the Azure Spring Apps.
    examples:
    - name: Append a new persistent storage to an app.
      text: az spring app append-persistent-storage --persistent-storage-type AzureFileVolume --share-name MyShareName --mount-path /MyMountPath --storage-name MyStorageName -n MyApp -g MyResourceGroup -s MyService
"""

helps['spring app update'] = """
    type: command
    short-summary: Update configurations of an app.
    examples:
    - name: Add an environment variable for the app.
      text: az spring app update -n MyApp -s MyCluster -g MyResourceGroup --env foo=bar
"""

helps['spring app delete'] = """
    type: command
    short-summary: Delete an app in the Azure Spring Apps.
"""

helps['spring app list'] = """
    type: command
    short-summary: List all apps in the Azure Spring Apps.
    examples:
    - name: Query status of persistent storage of all apps
      text: az spring app list -s MyCluster -g MyResourceGroup -o json --query '[].{Name:name, PersistentStorage:properties.persistentDisk}'
"""

helps['spring app show'] = """
    type: command
    short-summary: Show the details of an app in the Azure Spring Apps.
"""

helps['spring app start'] = """
    type: command
    short-summary: Start instances of the app, default to production deployment.
"""

helps['spring app stop'] = """
    type: command
    short-summary: Stop instances of the app, default to production deployment.
"""

helps['spring app restart'] = """
    type: command
    short-summary: Restart instances of the app, default to production deployment.
"""

helps['spring app enable-remote-debugging'] = """
    type: command
    short-summary: Enable remote debugging for a deployment.
"""

helps['spring app disable-remote-debugging'] = """
    type: command
    short-summary: Disable remote debugging for a deployment.
"""

helps['spring app get-remote-debugging-config'] = """
    type: command
    short-summary: Get the remote debugging configuration of a deployment.
"""

helps['spring app deploy'] = """
    type: command
    short-summary: Deploy source code or pre-built binary to an app and update related configurations.
    examples:
    - name: Deploy source code to an app. This will pack current directory, build binary with Pivotal Build Service and then deploy to the app.
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --source-path
    - name: Deploy a pre-built jar to an app with jvm options and environment variables.
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --artifact-path app.jar --jvm-options="-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
    - name: Deploy a pre-built war to an app with server version, jvm options and environment variables (Standard and Basic Tiers Only).
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --artifact-path app.war --server-version Tomcat_10 --jvm-options="-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
    - name: Deploy source code to a specific deployment of an app.
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup -d green-deployment --source-path
    - name: Deploy a container image on Docker Hub to an app.
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1
    - name: Deploy a container image on a private registry to an app.
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1 --container-registry myacr.azurecr.io --registry-username <username> --registry-password <password>
    - name: Deploy with Application Configuration Service config file patterns to an app.
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --config-file-patterns MyPatterns --artifact-path app.jar
    - name: Deploy a pre-built jar to an app with build env (For Enterprise tier only).
      text: az spring app deploy -n MyApp -s MyCluster -g MyResourceGroup --artifact-path app.jar --build-env BP_JVM_VERSION=11.*
"""

helps['spring app scale'] = """
    type: command
    short-summary: Manually scale an app or its deployments.
    examples:
    - name: Scale up an app to 4 cpu cores and 8 Gb of memory per instance.
      text: az spring app scale -n MyApp -s MyCluster -g MyResourceGroup --cpu 3 --memory 8
    - name: Scale out a deployment of the app to 5 instances.
      text: az spring app scale -n MyApp -s MyCluster -g MyResourceGroup -d green-deployment --instance-count 5
"""

helps['spring app show-deploy-log'] = """
    type: command
    short-summary: Show build log of the last deploy, only apply to source code deploy, default to production deployment.
"""

helps['spring app log tail'] = """
    type: command
    short-summary: Show logs of an app instance, logs will be streamed when setting '-f/--follow'.
"""

helps['spring app identity'] = """
    type: group
    short-summary: Manage an app's managed identities.
"""

helps['spring app identity assign'] = """
    type: command
    short-summary: Enable system-assigned managed identity or assign user-assigned managed identities to an app.
    examples:
    - name: Enable the system assigned identity.
      text: az spring app identity assign -n MyApp -s MyCluster -g MyResourceGroup --system-assigned
    - name: Enable the system assigned identity on an app with the 'Reader' role.
      text: az spring app identity assign -n MyApp -s MyCluster -g MyResourceGroup --system-assigned --role Reader --scope /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/xxxxx/providers/Microsoft.KeyVault/vaults/xxxxx
    - name: Assign two user-assigned managed identities to an app.
      text: az spring app identity assign -n MyApp -s MyCluster -g MyResourceGroup --user-assigned IdentityResourceId1 IdentityResourceId2
"""

helps['spring app identity remove'] = """
    type: command
    short-summary: Remove managed identity from an app.
    examples:
    - name: Remove the system-assigned managed identity from an app.
      text: az spring app identity remove -n MyApp -s MyCluster -g MyResourceGroup --system-assigned
    - name: Remove the system-assigned and user-assigned managed identities from an app.
      text: az spring app identity remove -n MyApp -s MyCluster -g MyResourceGroup --system-assigned --user-assigned IdentityResourceId1 IdentityResourceId2
    - name: Remove ALL user-assigned managed identities from an app.
      text: az spring app identity remove -n MyApp -s MyCluster -g MyResourceGroup --user-assigned
"""

helps['spring app identity show'] = """
    type: command
    short-summary: Display app's managed identity info.
    examples:
    - name: Display an app's managed identity info.
      text: az spring app identity show -n MyApp -s MyCluster -g MyResourceGroup
"""

helps['spring app identity force-set'] = """
    type: command
    short-summary: Force set managed identities on an app.
    examples:
    - name: Force remove all managed identities on an app.
      text: az spring app identity force-set -n MyApp -s MyCluster -g MyResourceGroup --system-assigned disable --user-assigned disable
    - name: Force remove all user-assigned managed identities on an app, and enable or keep system-assigned managed identity.
      text: az spring app identity force-set -n MyApp -s MyCluster -g MyResourceGroup --system-assigned enable --user-assigned disable
    - name: Force remove system-assigned managed identity on an app, and assign or keep user-assigned managed identities.
      text: az spring app identity force-set -n MyApp -s MyCluster -g MyResourceGroup --system-assigned disable --user-assigned IdentityResourceId1 IdentityResourceId2
"""

helps['spring app set-deployment'] = """
    type: command
    short-summary: Set production deployment of an app.
    examples:
    - name: Swap a staging deployment of an app to production.
      text: az spring app set-deployment -d green-deployment -n MyApp -s MyCluster -g MyResourceGroup
"""

helps['spring app unset-deployment'] = """
    type: command
    short-summary: Unset production deployment of an app.
    examples:
    - name: Swap the production deployment of an app to staging if the app has the production deployment.
      text: az spring app unset-deployment -n MyApp -s MyCluster -g MyResourceGroup
"""

helps['spring app log'] = """
    type: group
    short-summary: Commands to tail app instances logs with multiple options. If the app has only one instance, the instance name is optional.
"""

helps['spring app logs'] = """
    type: command
    short-summary: Show logs of an app instance, logs will be streamed when setting '-f/--follow'.
"""

helps['spring app connect'] = """
    type: command
    short-summary: Connect to the interactive shell of an app instance for troubleshooting'.
"""

helps['spring app deployment'] = """
    type: group
    short-summary: Commands to manage life cycle of deployments of an app in Azure Spring Apps. More operations on deployments can be done on app level with parameter --deployment. e.g. az spring app deploy --deployment <staging deployment>
"""

helps['spring app deployment list'] = """
    type: command
    short-summary: List all deployments in an app.
"""

helps['spring app deployment show'] = """
    type: command
    short-summary: Show details of a deployment.
"""

helps['spring app deployment delete'] = """
    type: command
    short-summary: Delete a deployment of the app.
"""

helps['spring app deployment create'] = """
    type: command
    short-summary: Create a staging deployment for the app. To deploy code or update setting to an existing deployment, use `az spring app deploy/update --deployment <staging deployment>`.
    examples:
    - name: Deploy source code to a new deployment of an app. This will pack current directory, build binary with Pivotal Build Service and then deploy.
      text: az spring app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --source-path
    - name: Deploy a pre-built jar to an app with jvm options and environment variables.
      text: az spring app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --artifact-path app.jar --jvm-options="-XX:+UseG1GC -XX:+UseStringDeduplication" --env foo=bar
    - name: Deploy a container image on Docker Hub to an app.
      text: az spring app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1
    - name: Deploy a container image on a private registry to an app.
      text: az spring app deployment create -n green-deployment --app MyApp -s MyCluster -g MyResourceGroup --container-image contoso/your-app:v1 --container-registry myacr.azurecr.io --registry-username <username> --registry-password <password>
"""

helps['spring app deployment generate-heap-dump'] = """
    type: command
    short-summary: Generate a heap dump of your target app instance to given file path.
"""

helps['spring app deployment generate-thread-dump'] = """
    type: command
    short-summary: Generate a thread dump of your target app instance to given file path.
"""

helps['spring app deployment start-jfr'] = """
    type: command
    short-summary: Start a JFR on your target app instance to given file path.
"""

helps['spring config-server'] = """
    type: group
    short-summary: (Support Standard Tier and Basic Tier) Commands to manage Config Server in Azure Spring Apps.
"""

helps['spring config-server show'] = """
    type: command
    short-summary: Show Config Server.
"""

helps['spring config-server set'] = """
    type: command
    short-summary: Set Config Server from a yaml file.
"""

helps['spring config-server clear'] = """
    type: command
    short-summary: Erase all settings in Config Server.
"""

helps['spring config-server git'] = """
    type: group
    short-summary: Commands to manage Config Server git property in Azure Spring Apps.
"""

helps['spring config-server git repo'] = """
    type: group
    short-summary: Commands to manage Config Server git repository in Azure Spring Apps.
"""

helps['spring config-server git set'] = """
    type: command
    short-summary: Set git property of Config Server, will totally override the old one.
"""

helps['spring config-server git repo add'] = """
    type: command
    short-summary: Add a new repository of git property of Config Server.
"""

helps['spring config-server git repo remove'] = """
    type: command
    short-summary: Remove an existing repository of git property of Config Server.
"""

helps['spring config-server git repo update'] = """
    type: command
    short-summary: Override an existing repository of git property of Config Server, will totally override the old one.
"""

helps['spring config-server git repo list'] = """
    type: command
    short-summary: List all repositories of git property of Config Server.
"""

helps['spring config-server enable'] = """
    type: command
    short-summary: (Support Standard consumption Tier) Enable Config Server.
"""

helps['spring config-server disable'] = """
    type: command
    short-summary: (Support Standard consumption Tier) Disable Config Server.
"""

helps['spring eureka-server'] = """
    type: group
    short-summary: (Support Standard consumption Tier) Commands to manage Eureka Server in Azure Spring Apps.
"""

helps['spring eureka-server enable'] = """
    type: command
    short-summary: (Support Standard consumption Tier) Enable Eureka Server.
"""

helps['spring eureka-server disable'] = """
    type: command
    short-summary: (Support Standard consumption Tier) Disable Eureka Server.
"""

helps['spring eureka-server show'] = """
    type: command
    short-summary: (Support Standard consumption Tier) Show Eureka Server.
"""

helps['spring app binding'] = """
    type: group
    short-summary: Commands to manage bindings with Azure Data Services, you need to manually restart app to make settings take effect.
"""

helps['spring app binding cosmos'] = """
    type: group
    short-summary: Commands to manage Azure Cosmos DB bindings.
"""

helps['spring app binding mysql'] = """
    type: group
    short-summary: Commands to manage Azure Database for MySQL bindings.
"""

helps['spring app binding redis'] = """
    type: group
    short-summary: Commands to manage Azure Cache for Redis bindings.
"""
helps['spring app binding list'] = """
    type: command
    short-summary: List all service bindings in an app.
"""

helps['spring app binding show'] = """
    type: command
    short-summary: Show the details of a service binding.
"""
helps['spring app binding remove'] = """
    type: command
    short-summary: Remove a service binding of the app.
"""

helps['spring app binding cosmos add'] = """
    type: command
    short-summary: Bind an Azure Cosmos DB with the app.
    examples:
    - name: Bind an Azure Cosmos DB.
      text: az spring app binding cosmos add -n cosmosProduction --app MyApp --resource-id ${COSMOSDB_ID} --api-type mongo --database mymongo -g MyResourceGroup -s MyService
"""

helps['spring app binding cosmos update'] = """
    type: command
    short-summary: Update an Azure Cosmos DB service binding of the app.
"""

helps['spring app binding mysql add'] = """
    type: command
    short-summary: Bind an Azure Database for MySQL with the app.
"""

helps['spring app binding mysql update'] = """
    type: command
    short-summary: Update an Azure Database for MySQL service binding of the app.
"""

helps['spring app binding redis add'] = """
    type: command
    short-summary: Bind an Azure Cache for Redis with the app.
"""

helps['spring app binding redis update'] = """
    type: command
    short-summary: Update an Azure Cache for Redis service binding of the app.
"""

helps['spring app append-loaded-public-certificate'] = """
    type: command
    short-summary: Append a new loaded public certificate to an app in the Azure Spring Apps.
    examples:
    - name: Append a new loaded public certificate to an app.
      text: az spring app append-loaded-public-certificate --name MyApp --service MyCluster --resource-group MyResourceGroup --certificate-name MyCertName --load-trust-store true
"""

helps['spring certificate'] = """
    type: group
    short-summary: Commands to manage certificates.
"""

helps['spring certificate add'] = """
    type: command
    short-summary: Add a certificate in Azure Spring Apps.
    examples:
    - name: Import certificate from key vault.
      text: az spring certificate add --name MyCertName --vault-uri MyKeyVaultUri --vault-certificate-name MyKeyVaultCertName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring certificate update'] = """
    type: command
    short-summary: Update a certificate in Azure Spring Apps.
    examples:
    - name: Enable auto sync feature of a key vault certificate in Azure Spring Apps.
      text: az spring certificate update --name MyCertName --service MyCluster --resource-group MyResourceGroup --enable-auto-sync true
    - name: Disable auto sync feature of a key vault certificate in Azure Spring Apps.
      text: az spring certificate update --name MyCertName --service MyCluster --resource-group MyResourceGroup --enable-auto-sync false
"""

helps['spring certificate show'] = """
    type: command
    short-summary: Show a certificate in Azure Spring Apps.
"""

helps['spring certificate list'] = """
    type: command
    short-summary: List all certificates in Azure Spring Apps.
    examples:
    - name: List all certificates in Spring service.
      text: az spring certificate list --service MyCluster --resource-group MyResourceGroup -o table
"""

helps['spring certificate remove'] = """
    type: command
    short-summary: Remove a certificate in Azure Spring Apps.
"""

helps['spring certificate list-reference-app'] = """
    type: command
    short-summary: List all the apps reference an existing certificate in the Azure Spring Apps.
    examples:
    - name: List all the apps reference an existing certificate in Spring service.
      text: az spring certificate list-reference-app --service MyCluster --resource-group MyResourceGroup --name MyCertName
"""

helps['spring app custom-domain'] = """
    type: group
    short-summary: Commands to manage custom domains.
"""

helps['spring app custom-domain bind'] = """
    type: command
    short-summary: Bind a custom domain with the app.
    examples:
    - name: Bind a custom domain to app.
      text: az spring app custom-domain bind --domain-name MyDomainName --certificate MyCertName --app MyAppName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring app custom-domain show'] = """
    type: command
    short-summary: Show details of a custom domain.
"""

helps['spring app custom-domain list'] = """
    type: command
    short-summary: List all custom domains of the app.
    examples:
    - name: List all custom domains of the app.
      text: az spring app custom-domain list --app MyAppName --service MyCluster --resource-group MyResourceGroup -o table
"""

helps['spring app custom-domain update'] = """
    type: command
    short-summary: Update a custom domain of the app.
    examples:
    - name: Bind custom domain with a specified certificate.
      text: az spring app custom-domain update --domain-name MyDomainName --certificate MCertName --app MyAppName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring app custom-domain unbind'] = """
    type: command
    short-summary: Unbind a custom-domain of the app.
"""

helps['spring app-insights'] = """
    type: group
    short-summary: Commands to management Application Insights in Azure Spring Apps.
"""

helps['spring app-insights show'] = """
    type: command
    short-summary: Show Application Insights settings.
"""

helps['spring app-insights update'] = """
    type: command
    short-summary: Update Application Insights settings.
    examples:
        - name: Enable Application Insights by using the Connection string (recommended) or Instrumentation key.
          text: az spring app-insights update -n MyService -g MyResourceGroup --app-insights-key \"MyConnectionString\" --sampling-rate 100
        - name: Disable Application Insights.
          text: az spring app-insights update -n MyService -g MyResourceGroup --disable
"""

helps['spring service-registry'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Service Registry in Azure Spring Apps.
"""

helps['spring service-registry create'] = """
    type: command
    short-summary: Create Service Registry.
    examples:
        - name: Create Service Registry.
          text: az spring service-registry create -s MyService -g MyResourceGroup
"""

helps['spring service-registry delete'] = """
    type: command
    short-summary: Delete Service Registry.
"""

helps['spring service-registry show'] = """
    type: command
    short-summary: Show the provisioning status and runtime status of Service Registry.
"""

helps['spring service-registry bind'] = """
    type: command
    short-summary: Bind an app to Service Registry.
    examples:
        - name: Bind an app to Service Registry.
          text: az spring service-registry bind --app MyApp -s MyService -g MyResourceGroup
"""

helps['spring service-registry unbind'] = """
    type: command
    short-summary: Unbind an app from Service Registry.
    examples:
        - name: Unbind an app from Service Registry.
          text: az spring service-registry unbind --app MyApp -s MyService -g MyResourceGroup
"""

helps['spring build-service'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Build Service
"""

helps['spring build-service update'] = """
    type: command
    short-summary: Update the build service.
    examples:
        - name: Update the build service when using your own container registry.
          text: az spring build-service update --registry-name my-acr --service clitest --resource-group cli
        - name: Update the build service when using ASA own container registry.
          text: az spring build-service update --service clitest --resource-group cli
"""

helps['spring build-service show'] = """
    type: command
    short-summary: Show the build service.
    examples:
        - name: Show the build service.
          text: az spring build-service show --service clitest --resource-group cli
"""

helps['spring build-service builder'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Builder Resource
"""

helps['spring build-service builder create'] = """
    type: command
    short-summary: Create a builder.
    examples:
        - name: Create a builder using JSON file.
          text: az spring build-service builder create --name my-builder --builder-file MyJson.json --service clitest --resource-group cli
"""

helps['spring build-service builder update'] = """
    type: command
    short-summary: Update a builder.
    examples:
        - name: Update a builder using JSON file.
          text: az spring build-service builder update --name my-builder --builder-file MyJson.json --service clitest --resource-group cli
"""

helps['spring build-service builder show'] = """
    type: command
    short-summary: Show a builder.
    examples:
        - name: Show a builder.
          text: az spring build-service builder show --name my-builder --service clitest --resource-group cli
"""

helps['spring build-service builder show-deployments'] = """
    type: command
    short-summary: Show deployments.
    examples:
        - name: Show the list of deployments using this builder.
          text: az spring build-service builder show-deployments --name my-builder --service clitest --resource-group cli
"""

helps['spring build-service builder delete'] = """
    type: command
    short-summary: Delete a builder.
    examples:
        - name: Delete a builder.
          text: az spring build-service builder delete --name my-builder --service clitest --resource-group cli
"""

helps['spring build-service build'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Build Resource
"""

helps['spring build-service build create'] = """
    type: command
    short-summary: Create a build.
    examples:
        - name: Create a build using a jar.
          text: az spring build-service build create --name my-build --artifact-path hello.jar --service clitest --resource-group cli
"""

helps['spring build-service build update'] = """
    type: command
    short-summary: Update a build.
    examples:
        - name: Update a build using the source code.
          text: az spring build-service build update --name my-build --source-path ./hello --service clitest --resource-group cli
"""

helps['spring build-service build show'] = """
    type: command
    short-summary: Show a build.
    examples:
        - name: Show a build.
          text: az spring build-service build show --name my-build --service clitest --resource-group cli
"""

helps['spring build-service build list'] = """
    type: command
    short-summary: List builds.
    examples:
        - name: List builds.
          text: az spring build-service build list --service clitest --resource-group cli
"""

helps['spring build-service build delete'] = """
    type: command
    short-summary: Delete a build.
    examples:
        - name: Delete a build.
          text: az spring build-service build delete --name my-build --service clitest --resource-group cli
"""

helps['spring build-service build result'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to view Build Result Resource
"""

helps['spring build-service build result show'] = """
    type: command
    short-summary: Show a build result.
    examples:
        - name: Show a build result.
          text: az spring build-service build result show --name 2 --build-name my-build --service clitest --resource-group cli
"""

helps['spring build-service build result list'] = """
    type: command
    short-summary: List build results.
    examples:
        - name: List build results by the build name.
          text: az spring build-service build result list --build-name my-build --service clitest --resource-group cli
"""

helps['spring container-registry'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Container Registry Resource
"""

helps['spring container-registry create'] = """
    type: command
    short-summary: Create a container registry.
    examples:
        - name: Create a container registry.
          text: az spring container-registry create --name my-acr --server test.azurecr.io --username test --password xxx --service clitest --resource-group cli
"""

helps['spring container-registry update'] = """
    type: command
    short-summary: Update a container registry.
    examples:
        - name: Update a container registry.
          text: az spring container-registry update --name my-acr --server test.azurecr.io --username test --password xxx --service clitest --resource-group cli
"""

helps['spring container-registry delete'] = """
    type: command
    short-summary: Delete a container registry.
    examples:
        - name: Delete a container registry.
          text: az spring container-registry delete --name my-acr --service clitest --resource-group cli
"""

helps['spring container-registry show'] = """
    type: command
    short-summary: Show a container registry.
    examples:
        - name: Show a container registry.
          text: az spring container-registry show --name my-acr --service clitest --resource-group cli
"""

helps['spring container-registry list'] = """
    type: command
    short-summary: List all container registries.
    examples:
        - name: List all container registries.
          text: az spring container-registry list --service clitest --resource-group cli
"""

helps['spring application-live-view'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Application Live View in Azure Spring Apps. Application Live View presents application instance metrics, and makes it easy for developers to monitor application runtimes.
"""

helps['spring application-live-view show'] = """
    type: command
    short-summary: Show the provisioning state, running status and settings of Application Live View.
"""

helps['spring application-live-view create'] = """
    type: command
    short-summary: Create Application Live View.
    examples:
        - name: Create Application Live View
          text: az spring application-live-view create -s MyService -g MyResourceGroup
"""

helps['spring application-live-view delete'] = """
    type: command
    short-summary: Delete Application Live View.
"""

helps['spring dev-tool'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Dev Tools in Azure Spring Apps. The Dev Tools Portal is an underlying application that hosts the developer tools.
"""

helps['spring dev-tool show'] = """
    type: command
    short-summary: Show the provisioning state, running status and settings of Dev Tool Portal.
"""

helps['spring dev-tool create'] = """
    type: command
    short-summary: Create Dev Tool Portal.
    examples:
        - name: Create Dev Tool Portal with public endpoint exposed
          text: az spring dev-tool create -s MyService -g MyResourceGroup --assign-endpoint
        - name: Create Dev Tool Portal with SSO enabled
          text: az spring dev-tool create -s MyService -g MyResourceGroup --client-id 00000000-0000-0000-000000000000 --scopes scope1,scope2  --client-secret MySecret --metadata-url "https://example.com/.well-known/openid-configuration" --assign-endpoint
"""

helps['spring dev-tool update'] = """
    type: command
    short-summary: Update Dev Tool Portal.
    examples:
        - name: Update Dev Tool Portal with public endpoint exposed
          text: az spring dev-tool update -s MyService -g MyResourceGroup --assign-endpoint
        - name: Update Dev Tool Portal with SSO enabled
          text: az spring dev-tool update -s MyService -g MyResourceGroup --client-id 00000000-0000-0000-000000000000 --scopes scope1,scope2  --client-secret MySecret --metadata-url "https://example.com/.well-known/openid-configuration" --assign-endpoint
"""

helps['spring dev-tool delete'] = """
    type: command
    short-summary: Delete Dev Tool Portal.
"""

helps['spring application-configuration-service'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Application Configuration Service in Azure Spring Apps.
"""

helps['spring application-configuration-service create'] = """
    type: command
    short-summary: Create Application Configuration Service.
    examples:
        - name: Create Application Configuration Service.
          text: az spring application-configuration-service create -s MyService -g MyResourceGroup
"""

helps['spring application-configuration-service update'] = """
    type: command
    short-summary: Update Application Configuration Service.
    examples:
        - name: Update Application Configuration Service.
          text: az spring application-configuration-service update -s MyService -g MyResourceGroup --generation Gen2
"""

helps['spring application-configuration-service delete'] = """
    type: command
    short-summary: Delete Application Configuration Service.
"""

helps['spring application-configuration-service show'] = """
    type: command
    short-summary: Show the provisioning status, runtime status, and settings of Application Configuration Service.
"""

helps['spring application-configuration-service clear'] = """
    type: command
    short-summary: Reset all Application Configuration Service settings.
"""

helps['spring application-configuration-service git'] = """
    type: group
    short-summary: Commands to manage Application Configuration Service git property in Azure Spring Apps.
"""

helps['spring application-configuration-service git repo'] = """
    type: group
    short-summary: Commands to manage Application Configuration Service git repository in Azure Spring Apps.
"""

helps['spring application-configuration-service git repo add'] = """
    type: command
    short-summary: Add a Git property to the Application Configuration Service settings.
    examples:
        - name: Add a Git property.
          text: az spring application-configuration-service git repo add -s MyService -g MyResourceGroup --name MyName --patterns MyPattern --uri https://MyURI --label master
"""

helps['spring application-configuration-service git repo update'] = """
    type: command
    short-summary: Update an existing Git property in the Application Configuration Service settings.
    examples:
        - name: Update a Git property.
          text: az spring application-configuration-service git repo update -s MyService -g MyResourceGroup --name MyName --patterns MyPattern
"""

helps['spring application-configuration-service git repo remove'] = """
    type: command
    short-summary: Delete an existing Git property from the Application Configuration Service settings.
    examples:
        - name: Delete a Git property.
          text: az spring application-configuration-service git repo remove -s MyService -g MyResourceGroup --name MyName
"""

helps['spring application-configuration-service git repo list'] = """
    type: command
    short-summary: List all Git settings of Application Configuration Service.
"""

helps['spring application-configuration-service bind'] = """
    type: command
    short-summary: Bind an app to Application Configuration Service.
    examples:
        - name: Bind an app to Application Configuration Service.
          text: az spring application-configuration-service bind --app MyApp -s MyService -g MyResourceGroup
"""

helps['spring application-configuration-service unbind'] = """
    type: command
    short-summary: Unbind an app from Application Configuration Service.
    examples:
        - name: Unbind an app from Application Configuration Service.
          text: az spring application-configuration-service unbind --app MyApp -s MyService -g MyResourceGroup
"""

helps['spring application-configuration-service config'] = """
    type: group
    short-summary: Commands to manage the configurations pulled by Application Configuration Service from upstream Git repositories.
"""

helps['spring application-configuration-service config show'] = """
    type: command
    short-summary: Command to show the configurations pulled by Application Configuration Service from upstream Git repositories.
"""

helps['spring gateway'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage gateway in Azure Spring Apps.
"""

helps['spring gateway create'] = """
    type: command
    short-summary: Create Spring Cloud Gateway.
    examples:
        - name: Create Spring Cloud Gateway.
          text: az spring gateway create -s MyService -g MyResourceGroup --instance-count 2
"""

helps['spring gateway delete'] = """
    type: command
    short-summary: Delete Spring Cloud Gateway.
"""

helps['spring gateway clear'] = """
    type: command
    short-summary: Clear all settings of gateway.
"""

helps['spring gateway show'] = """
    type: command
    short-summary: Show the settings, provisioning status and runtime status of gateway.
"""

helps['spring gateway update'] = """
    type: command
    short-summary: Update an existing gateway properties.
    examples:
        - name: Update gateway property.
          text: az spring gateway update -s MyService -g MyResourceGroup --assign-endpoint true --https-only true
        - name: Enable and configure response cache at Route level and set ttl to 5 minutes.
          text: az spring gateway update -s MyService -g MyResourceGroup --enable-response-cache --response-cache-scope Route --response-cache-ttl 5m
        - name: When response cache is enabled, update ttl to 3 minutes.
          text: az spring gateway update -s MyService -g MyResourceGroup --response-cache-ttl 3m
        - name: Disable response cache.
          text: az spring gateway update -s MyService -g MyResourceGroup --enable-response-cache false
"""

helps['spring gateway restart'] = """
    type: command
    short-summary: Restart Spring Cloud Gateway.
    examples:
        - name: Restart Spring Cloud Gateway.
          text: az spring gateway restart -s MyService -g MyResourceGroup
"""

helps['spring gateway sync-cert'] = """
    type: command
    short-summary: Sync certificate of gateway.
    examples:
        - name: Sync certificate of gateway.
          text: az spring gateway sync-cert -s MyService -g MyResourceGroup
"""

helps['spring gateway route-config'] = """
    type: group
    short-summary: Commands to manage gateway route configs in Azure Spring Apps.
"""

helps['spring gateway route-config create'] = """
    type: command
    short-summary: Create a gateway route config with routing rules of Json array format.
    examples:
        - name: Create a gateway route config targeting the app in Azure Spring Apps.
          text: az spring gateway route-config create -s MyService -g MyResourceGroup --name MyName --app-name MyApp --routes-file MyJson.json
"""

helps['spring gateway route-config update'] = """
    type: command
    short-summary: Update an existing gateway route config with routing rules of Json array format.
    examples:
        - name: Update an existing gateway route config targeting the app in Azure Spring Apps.
          text: az spring gateway route-config update -s MyService -g MyResourceGroup --name MyName --app-name MyApp --routes-file MyJson.json
"""

helps['spring gateway route-config remove'] = """
    type: command
    short-summary: Delete an existing gateway route config.
    examples:
        - name: Delete an existing gateway route config.
          text: az spring gateway route-config remove -s MyService -g MyResourceGroup --name MyName
"""

helps['spring gateway route-config show'] = """
    type: command
    short-summary: Get an existing gateway route config.
    examples:
        - name: Get an existing gateway route config.
          text: az spring gateway route-config show -s MyService -g MyResourceGroup --name MyName
"""

helps['spring gateway route-config list'] = """
    type: command
    short-summary: List all existing gateway route configs.
    examples:
        - name: List all existing gateway route configs.
          text: az spring gateway route-config list -s MyService -g MyResourceGroup
"""

helps['spring gateway custom-domain'] = """
    type: group
    short-summary: Commands to manage custom domains for gateway.
"""

helps['spring gateway custom-domain bind'] = """
    type: command
    short-summary: Bind a custom domain with the gateway.
    examples:
    - name: Bind a custom domain to gateway.
      text: az spring gateway custom-domain bind --domain-name MyDomainName --certificate MyCertName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring gateway custom-domain show'] = """
    type: command
    short-summary: Show details of a custom domain.
"""

helps['spring gateway custom-domain list'] = """
    type: command
    short-summary: List all custom domains of the gateway.
    examples:
    - name: List all custom domains of the gateway.
      text: az spring gateway custom-domain list --service MyCluster --resource-group MyResourceGroup
"""

helps['spring gateway custom-domain update'] = """
    type: command
    short-summary: Update a custom domain of the gateway.
    examples:
    - name: Bind custom domain with a specified certificate.
      text: az spring gateway custom-domain update --domain-name MyDomainName --certificate MCertName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring gateway custom-domain unbind'] = """
    type: command
    short-summary: Unbind a custom-domain of the gateway.
"""

helps['spring api-portal'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage API portal in Azure Spring Apps.
"""

helps['spring api-portal create'] = """
    type: command
    short-summary: Create API portal.
    examples:
        - name: Create API portal.
          text: az spring api-portal create -s MyService -g MyResourceGroup --instance-count 1
"""

helps['spring api-portal delete'] = """
    type: command
    short-summary: Delete API portal.
"""


helps['spring api-portal clear'] = """
    type: command
    short-summary: Clear all settings of API portal.
"""

helps['spring api-portal show'] = """
    type: command
    short-summary: Show the settings, provisioning status and runtime status of API portal.
"""

helps['spring api-portal update'] = """
    type: command
    short-summary: Update an existing API portal properties.
    examples:
        - name: Update API portal property.
          text: az spring api-portal update -s MyService -g MyResourceGroup --assign-endpoint true --https-only true
"""

helps['spring api-portal custom-domain'] = """
    type: group
    short-summary: Commands to manage custom domains for API portal.
"""

helps['spring api-portal custom-domain bind'] = """
    type: command
    short-summary: Bind a custom domain with the API portal.
    examples:
    - name: Bind a custom domain to API portal.
      text: az spring api-portal custom-domain bind --domain-name MyDomainName --certificate MyCertName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring api-portal custom-domain show'] = """
    type: command
    short-summary: Show details of a custom domain.
"""

helps['spring api-portal custom-domain list'] = """
    type: command
    short-summary: List all custom domains of the API portal.
    examples:
    - name: List all custom domains of the API portal.
      text: az spring api-portal custom-domain list --service MyCluster --resource-group MyResourceGroup
"""

helps['spring api-portal custom-domain update'] = """
    type: command
    short-summary: Update a custom domain of the API portal.
    examples:
    - name: Bind custom domain with a specified certificate.
      text: az spring api-portal custom-domain update --domain-name MyDomainName --certificate MCertName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring api-portal custom-domain unbind'] = """
    type: command
    short-summary: Unbind a custom-domain of the API portal.
"""

helps['spring build-service'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage build service in Azure Spring Apps.
"""

helps['spring build-service builder'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage builder of build service.
"""

helps['spring build-service builder buildpack-binding'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage buildpack-binding of builder.
"""

helps['spring build-service builder buildpack-binding create'] = """
    type: command
    short-summary: (Enterprise Tier Only) Create a buildpack binding.
    examples:
        - name: Create a buildpack binding without properties or secrets.
          text: az spring build-service builder buildpack-binding create --name first-binding --builder-name first-builder --type ApplicationInsights --service MyCluster --resource-group MyResourceGroup
        - name: Create a buildpack binding with only secrets.
          text: az spring build-service builder buildpack-binding create --name first-binding --builder-name first-builder --type ApplicationInsights --secrets k1=v1 k2=v2 --service MyCluster --resource-group MyResourceGroup
        - name: Create a buildpack binding with only properties.
          text: az spring build-service builder buildpack-binding create --name first-binding --builder-name first-builder --type ApplicationInsights --properties a=b c=d --service MyCluster --resource-group MyResourceGroup
        - name: Create a buildpack binding with properties and secrets.
          text: az spring build-service builder buildpack-binding create --name first-binding --builder-name first-builder --type ApplicationInsights --properties a=b c=d --secrets k1=v1 k2=v2 --service MyCluster --resource-group MyResourceGroup
"""

helps['spring build-service builder buildpack-binding set'] = """
    type: command
    short-summary: (Enterprise Tier Only) Set a buildpack binding.
    examples:
        - name: Set a buildpack binding with properties and secrets.
          text: az spring build-service builder buildpack-binding set --name first-binding --builder-name first-builder --type ApplicationInsights --properties a=b c=d --secrets k1=v1 k2=v2 --service MyCluster --resource-group MyResourceGroup
"""

helps['spring build-service builder buildpack-binding show'] = """
    type: command
    short-summary: (Enterprise Tier Only) Show a buildpack binding. The secrets will be masked.
    examples:
        - name: Show a buildpack binding.
          text: az spring build-service builder buildpack-binding show --name first-binding --builder-name first-builder --service MyCluster --resource-group MyResourceGroup
"""

helps['spring build-service builder buildpack-binding list'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all buildpack binding in a builder. The secrets will be masked.
    examples:
        - name: List all buildpack binding of a builder.
          text: az spring build-service builder buildpack-binding list --builder-name first-builder --service MyCluster --resource-group MyResourceGroup
"""

helps['spring build-service builder buildpack-binding delete'] = """
    type: command
    short-summary: (Enterprise Tier Only) Delete a buildpack binding.
    examples:
        - name: Delete a buildpack binding.
          text: az spring build-service builder buildpack-binding delete --name first-binding --builder-name first-builder --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage Application Accelerator in Azure Spring Apps.
"""

helps['spring application-accelerator create'] = """
    type: command
    short-summary: (Enterprise Tier Only) Create Application Accelerator in Azure Spring Apps instance.
    examples:
        - name: Create Application Accelerator in Azure Spring Apps instance.
          text: az spring application-accelerator create --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator show'] = """
    type: command
    short-summary: (Enterprise Tier Only) Show the settings, provisioning status and runtime status of Application Accelerator.
    examples:
        - name: Show details of a Application Accelerator.
          text: az spring application-accelerator show --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator delete'] = """
    type: command
    short-summary: (Enterprise Tier Only) Delete Application Accelerator from Azure Spring Apps instance.
    examples:
        - name: Delete Application Accelerator from Azure Spring Apps instance.
          text: az spring application-accelerator delete --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator predefined-accelerator'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage predefined accelerator in Azure Spring Apps.
"""

helps['spring application-accelerator predefined-accelerator list'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all existing predefined accelerators.
    examples:
        - name: List all existing predefined accelerators.
          text: az spring application-accelerator predefined-accelerator list --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator predefined-accelerator show'] = """
    type: command
    short-summary: (Enterprise Tier Only) Show the settings, provisioning status and runtime status of predefined accelerator.
    examples:
        - name: Show details of a predefined accelerator.
          text: az spring application-accelerator predefined-accelerator show --name AcceleratorName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator predefined-accelerator disable'] = """
    type: command
    short-summary: (Enterprise Tier Only) Disable a predefined accelerator.
    examples:
        - name: Disable a predefined accelerator.
          text: az spring application-accelerator predefined-accelerator disable --name AcceleratorName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator predefined-accelerator enable'] = """
    type: command
    short-summary: (Enterprise Tier Only) Enable a predefined accelerator.
    examples:
        - name: Enable a predefined accelerator.
          text: az spring application-accelerator predefined-accelerator enable --name AcceleratorName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator customized-accelerator'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage customized accelerator in Azure Spring Apps.
"""

helps['spring application-accelerator customized-accelerator list'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all existing customized accelerators.
    examples:
        - name: List all existing customized accelerators.
          text: az spring application-accelerator customized-accelerator list --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator customized-accelerator show'] = """
    type: command
    short-summary: (Enterprise Tier Only) Show the settings, provisioning status and runtime status of customized accelerator.
    examples:
        - name: Show details of a customized accelerator.
          text: az spring application-accelerator customized-accelerator show --name AcceleratorName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator customized-accelerator create'] = """
    type: command
    short-summary: (Enterprise Tier Only) Create a customized accelerator.
    examples:
        - name: Create a customized accelerator.
          text: az spring application-accelerator customized-accelerator create --name AcceleratorName --service MyCluster --resource-group MyResourceGroup --git-url https://github.com/xxx --git-branch main --display-name acc-name
"""

helps['spring application-accelerator customized-accelerator update'] = """
    type: command
    short-summary: (Enterprise Tier Only) Update a customized accelerator.
    examples:
        - name: Update a customized accelerator.
          text: az spring application-accelerator customized-accelerator update --name AcceleratorName --service MyCluster --resource-group MyResourceGroup --git-url https://github.com/xxx --git-branch main --display-name acc-name
"""

helps['spring application-accelerator customized-accelerator sync-cert'] = """
    type: command
    short-summary: (Enterprise Tier Only) Sync certificate of a customized accelerator.
    examples:
        - name: Sync certificate of a customized accelerator.
          text: az spring application-accelerator customized-accelerator sync-cert --name AcceleratorName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring application-accelerator customized-accelerator delete'] = """
    type: command
    short-summary: (Enterprise Tier Only) Delete a customized accelerator.
    examples:
        - name: Delete a customized accelerator.
          text: az spring application-accelerator customized-accelerator delete --name AcceleratorName --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to manage APMs in Azure Spring Apps.
"""

helps['spring apm create'] = """
    type: command
    short-summary: (Enterprise Tier Only) Create an APM.
    examples:
        - name: Create an APM with secrets only.
          text: az spring apm create --name first-apm --type ApplicationInsights --secrets k1=v1 k2=v2 --service MyCluster --resource-group MyResourceGroup
        - name: Create an APM with properties only.
          text: az spring apm create --name first-apm --type ApplicationInsights --properties a=b c=d --service MyCluster --resource-group MyResourceGroup
        - name: Create an APM with properties and secrets.
          text: az spring apm create --name first-apm --type ApplicationInsights --properties a=b c=d --secrets k1=v1 k2=v2 --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm update'] = """
    type: command
    short-summary: (Enterprise Tier Only) Update an APM.
    examples:
        - name: Update an APM with properties and secrets.
          text: az spring apm update --name first-apm --type ApplicationInsights --properties a=b c=d --secrets k1=v1 k2=v2 --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm show'] = """
    type: command
    short-summary: (Enterprise Tier Only) Show an APM. The secrets will be masked.
    examples:
        - name: Show an APM.
          text: az spring apm show --name first-apm --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm list'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all the APMs in the Azure Spring Apps. The secrets will be omitted.
    examples:
        - name: List all the APMs in the Azure Spring Apps.
          text: az spring apm list --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm delete'] = """
    type: command
    short-summary: (Enterprise Tier Only) Delete an APM.
    examples:
        - name: Delete an APM.
          text: az spring apm delete --name first-apm --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm list-enabled-globally'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all the APMs enabled globally in the Azure Spring Apps.
    examples:
        - name: List all the APMs enabled globally in the Azure Spring Apps.
          text: az spring apm list-enabled-globally --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm list-support-types'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all the supported APM types in the Azure Spring Apps.
    examples:
        - name: List all the supported APM types in the Azure Spring Apps.
          text: az spring apm list-support-types --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm enable-globally'] = """
    type: command
    short-summary: (Enterprise Tier Only) Enable an APM globally.
    examples:
        - name: Enable an APM globally.
          text: az spring apm enable-globally --name first-apm --service MyCluster --resource-group MyResourceGroup
"""

helps['spring apm disable-globally'] = """
    type: command
    short-summary: (Enterprise Tier Only) Disable an APM globally.
    examples:
        - name: Disable an APM globally.
          text: az spring apm disable-globally --name first-apm --service MyCluster --resource-group MyResourceGroup
"""

helps['spring component'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to handle managed components.
"""

helps['spring component logs'] = """
    type: command
    short-summary: (Enterprise Tier Only) Show logs for managed components. Logs will be streamed when setting '-f/--follow'. For now, only supports subcomponents of (a) Application Configuration Service (b) Spring Cloud Gateway
    examples:
        - name: Show logs for all instances of flux in Application Configuration Serice (Gen2)
          text: az spring component logs --name flux-source-controller --service MyAzureSpringAppsInstance --resource-group MyResourceGroup --all-instances
        - name: Show logs for a specific instance of application-configuration-service in Application Configuration Serice
          text: az spring component logs --name application-configuration-service --service MyAzureSpringAppsInstance --resource-group MyResourceGroup --instance InstanceName
        - name: Stream and watch logs for all instances of spring-cloud-gateway
          text: az spring component logs --name spring-cloud-gateway --service MyAzureSpringAppsInstance --resource-group MyResourceGroup --all-instances --follow
        - name: Show logs for a specific instance without specify the component name
          text: az spring component logs --service MyAzureSpringAppsInstance --resource-group MyResourceGroup --instance InstanceName
"""

helps['spring component list'] = """
    type: command
    short-summary: (Enterprise Tier Only) List managed components.
    examples:
        - name: List all managed components
          text: az spring component list --service MyAzureSpringAppsInstance --resource-group MyResourceGroup
"""

helps['spring component instance'] = """
    type: group
    short-summary: (Enterprise Tier Only) Commands to handle instances of a managed component.
"""

helps['spring component instance list'] = """
    type: command
    short-summary: (Enterprise Tier Only) List all available instances of a specific managed component in an Azure Spring Apps instance.
    examples:
        - name: List instances for spring-cloud-gateway of Spring Cloud Gateway
          text: az spring component instance list --component spring-cloud-gateway --service MyAzureSpringAppsInstance --resource-group MyResourceGroup
        - name: List instances for spring-cloud-gateway-operator of Spring Cloud Gateway
          text: az spring component instance list --component spring-cloud-gateway-operator --service MyAzureSpringAppsInstance --resource-group MyResourceGroup
"""
