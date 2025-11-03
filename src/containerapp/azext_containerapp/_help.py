# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['containerapp'] = """
    type: group
    short-summary: Manage Azure Container Apps.
"""


helps['containerapp env dapr-component resiliency'] = """
    type: group
    short-summary: Commands to manage resiliency policies for a dapr component.
"""

helps['containerapp env dapr-component resiliency create'] = """
    type: command
    short-summary: Create resiliency policies for a dapr component.
    examples:
    - name: Create timeout resiliency policy for a dapr component.
      text: |
          az containerapp env dapr-component resiliency create -g MyResourceGroup \\
            -n MyDaprResiliency --dapr-component-name MyDaprComponentName \\
            --environment MyEnvironment --out-timeout 45
    - name: Create resiliency policies for a dapr component using a yaml configuration.
      text: |
          az containerapp env dapr-component resiliency create -g MyResourceGroup \\
            -n MyDaprResiliency --dapr-component-name MyDaprComponentName \\
            --environment MyEnvironment --yaml "path/to/yaml/file.yml"
"""

helps['containerapp env dapr-component resiliency update'] = """
    type: command
    short-summary: Update resiliency policies for a dapr component.
    examples:
    - name: Update timeout resiliency policy for a dapr component.
      text: |
          az containerapp env dapr-component resiliency update -g MyResourceGroup \\
            -n MyDaprResiliency --dapr-component-name MyDaprComponentName \\
            --environment MyEnvironment --in-timeout 45
    - name: Update resiliency policies for a dapr component using a yaml configuration.
      text: |
          az containerapp env dapr-component resiliency update -g MyResourceGroup \\
            -n MyDaprResiliency --dapr-component-name MyDaprComponentName \\
            --environment MyEnvironment --yaml "path/to/yaml/file.yml"
"""

helps['containerapp env dapr-component resiliency show'] = """
    type: command
    short-summary: Show resiliency policies for a dapr component.
    examples:
    - name: Show resiliency policies for a dapr component.
      text: |
          az containerapp env dapr-component resiliency show -g MyResourceGroup \\
            -n MyDaprResiliency --dapr-component-name MyDaprComponentName \\
            --environment MyEnvironment
"""

helps['containerapp env dapr-component resiliency delete'] = """
    type: command
    short-summary: Delete resiliency policies for a dapr component.
    examples:
    - name: Delete resiliency policies for a dapr component.
      text: |
          az containerapp env dapr-component resiliency delete -g MyResourceGroup \\
            -n MyDaprResiliency --dapr-component-name MyDaprComponentName \\
            --environment MyEnvironment
"""

helps['containerapp env dapr-component resiliency list'] = """
    type: command
    short-summary: List resiliency policies for a dapr component.
    examples:
    - name: List resiliency policies for a dapr component.
      text: |
          az containerapp env dapr-component resiliency list -g MyResourceGroup \\
           --dapr-component-name MyDaprComponentName --environment MyEnvironment
"""

# Identity Commands
helps['containerapp env identity'] = """
    type: group
    short-summary: Commands to manage environment managed identities.
"""

helps['containerapp env identity assign'] = """
    type: command
    short-summary: Assign managed identity to a managed environment.
    long-summary: Managed identities can be user-assigned or system-assigned.
    examples:
    - name: Assign system identity.
      text: |
          az containerapp env identity assign -n my-env -g MyResourceGroup --system-assigned
    - name: Assign user identity.
      text: |
          az containerapp env identity assign -n my-env -g MyResourceGroup --user-assigned myUserIdentityName
    - name: Assign user identity (from a different resource group than the managed environment).
      text: |
          az containerapp env identity assign -n my-env -g MyResourceGroup --user-assigned myUserIdentityResourceId
    - name: Assign system and user identity.
      text: |
          az containerapp env identity assign -n my-env -g MyResourceGroup --system-assigned --user-assigned myUserIdentityResourceId
"""

helps['containerapp env identity remove'] = """
    type: command
    short-summary: Remove a managed identity from a managed environment.
    examples:
    - name: Remove system identity.
      text: |
          az containerapp env identity remove -n my-env -g MyResourceGroup --system-assigned
    - name: Remove user identity.
      text: |
          az containerapp env identity remove -n my-env -g MyResourceGroup --user-assigned myUserIdentityName
    - name: Remove system and user identity (from a different resource group than the containerapp).
      text: |
          az containerapp env identity remove -n my-env -g MyResourceGroup --system-assigned --user-assigned myUserIdentityResourceId
    - name: Remove all user identities.
      text: |
          az containerapp env identity remove -n my-env -g MyResourceGroup --user-assigned
    - name: Remove system identity and all user identities.
      text: |
          az containerapp env identity remove -n my-env -g MyResourceGroup --system-assigned --user-assigned
"""

helps['containerapp env identity show'] = """
    type: command
    short-summary: Show managed identities of a managed environment.
    examples:
    - name: Show managed identities.
      text: |
          az containerapp env identity show -n my-env -g MyResourceGroup
"""

helps['containerapp up'] = """
    type: command
    short-summary: Create or update a container app as well as any associated resources (ACR, resource group, container apps environment, GitHub Actions, etc.)
    examples:
    - name: Create a container app from a dockerfile in a GitHub repo (setting up github actions)
      text: |
          az containerapp up -n my-containerapp --repo https://github.com/myAccount/myRepo
    - name: Create a container app from a dockerfile in a local directory (or autogenerate a container if no dockerfile is found)
      text: |
          az containerapp up -n my-containerapp --source .
    - name: Create a container app from an image in a registry
      text: |
          az containerapp up -n my-containerapp --image myregistry.azurecr.io/myImage:myTag
    - name: Create a container app from an image in a registry with ingress enabled and a specified environment
      text: |
          az containerapp up -n my-containerapp --image myregistry.azurecr.io/myImage:myTag --ingress external --target-port 80 --environment MyEnv
    - name: Create a container app from an image in a registry on a Connected cluster
      text: |
          az containerapp up -n my-containerapp --image myregistry.azurecr.io/myImage:myTag --connected-cluster-id MyConnectedClusterResourceId
    - name: Create a container app from an image in a registry on a connected environment
      text: |
          az containerapp up -n my-containerapp --image myregistry.azurecr.io/myImage:myTag --environment MyConnectedEnvironmentId
    - name: Create a container app and deploy a model from Azure AI Foundry
      text: |
            az containerapp up -n my-containerapp -l westus3 --model-registry azureml --model-name Phi-4 --model-version 7
    - name: Create an Azure Functions on Azure Container Apps (kind=functionapp)
      text: |
            az containerapp up -n my-containerapp --image my-app:v1.0 --kind functionapp
"""


helps['containerapp replica count'] = """
    type: command
    short-summary: Count of a container app's replica(s)
    examples:
    - name: Count replicas of a particular revision
      text: |
          az containerapp replica count -n my-containerapp -g MyResourceGroup --revision MyRevision
    - name: Count replicas of the latest revision
      text: |
          az containerapp replica count -n my-containerapp -g MyResourceGroup
"""

# Environment Commands
helps['containerapp env'] = """
    type: group
    short-summary: Commands to manage Container Apps environments.
"""

helps['containerapp env create'] = """
    type: command
    short-summary: Create a Container Apps environment.
    examples:
    - name: Create an environment with an auto-generated Log Analytics workspace.
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --location eastus2
    - name: Create a zone-redundant environment
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --location eastus2 --zone-redundant
    - name: Create an environment with an existing Log Analytics workspace.
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --logs-workspace-id myLogsWorkspaceID \\
              --logs-workspace-key myLogsWorkspaceKey \\
              --location eastus2
    - name: Create an environment with workload profiles enabled.
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --location eastus2 --enable-workload-profiles
    - name: Create an environment without workload profiles enabled.
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --location eastus2 --enable-workload-profiles false
    - name: Create an environment with system assigned and user assigned identity.
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --location eastus2 --mi-system-assigned --mi-user-assigned MyUserIdentityResourceId
"""

helps['containerapp add-on'] = """
    type: group
    short-summary: Commands to manage add-ons available within the environment.
"""

helps['containerapp add-on list'] = """
    type: command
    short-summary: List all add-ons within the environment.
"""

helps['containerapp resiliency'] = """
    type: group
    short-summary: Commands to manage resiliency policies for a container app.
"""

helps['containerapp resiliency create'] = """
    type: command
    short-summary: Create resiliency policies for a container app.
    examples:
    - name: Create recommended resiliency policies.
      text: |
          az containerapp resiliency create -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name my-containerapp --recommended
    - name: Create the timeout resiliency policy.
      text: |
          az containerapp resiliency create -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name my-containerapp \\
            --timeout 15 --timeout-connect 5
    - name: Create resiliency policies using a yaml configuration.
      text: |
          az containerapp resiliency create -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name my-containerapp \\
            --yaml "path/to/yaml/file.yml"
"""

helps['containerapp resiliency update'] = """
    type: command
    short-summary: Update resiliency policies for a container app.
    examples:
    - name: Update the TCP Connection Pool resiliency policy.
      text: |
          az containerapp resiliency update -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name my-containerapp \\
            --tcp-connections 1024
    - name: Update resiliency policies using a yaml configuration.
      text: |
          az containerapp resiliency update -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name my-containerapp \\
            --yaml "path/to/yaml/file.yml"

"""

helps['containerapp resiliency delete'] = """
    type: command
    short-summary: Delete resiliency policies for a container app.
    examples:
    - name: Delete resiliency policies for a container app.
      text: |
          az containerapp resiliency delete -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name MyContainerApp
"""

helps['containerapp resiliency show'] = """
    type: command
    short-summary: Show resiliency policies for a container app.
    examples:
    - name: Show resiliency policies for a container app.
      text: |
          az containerapp resiliency show -g MyResourceGroup \\
            -n MyResiliencyName --container-app-name MyContainerApp
"""

helps['containerapp resiliency list'] = """
    type: command
    short-summary: List resiliency policies for a container app.
    examples:
    - name: List resiliency policies for a container app.
      text: |
          az containerapp resiliency list -g MyResourceGroup \\
            --container-app-name MyContainerApp
"""

helps['containerapp add-on redis'] = """
    type: group
    short-summary: Commands to manage the redis add-on for the Container Apps environment.
"""

helps['containerapp add-on postgres'] = """
    type: group
    short-summary: Commands to manage the postgres add-on for the Container Apps environment.
"""

helps['containerapp add-on kafka'] = """
    type: group
    short-summary: Commands to manage the kafka add-on for the Container Apps environment.
"""

helps['containerapp add-on mariadb'] = """
    type: group
    short-summary: Commands to manage the mariadb add-on for the Container Apps environment.
"""

helps['containerapp add-on qdrant'] = """
    type: group
    short-summary: Commands to manage the qdrant add-on for the Container Apps environment.
"""

helps['containerapp add-on weaviate'] = """
    type: group
    short-summary: Commands to manage the weaviate add-on for the Container Apps environment.
"""

helps['containerapp add-on milvus'] = """
    type: group
    short-summary: Commands to manage the milvus add-on for the Container Apps environment.
"""

helps['containerapp add-on redis create'] = """
    type: command
    short-summary: Command to create the redis add-on.
"""

helps['containerapp add-on postgres create'] = """
    type: command
    short-summary: Command to create the postgres add-on.
"""

helps['containerapp add-on kafka create'] = """
    type: command
    short-summary: Command to create the kafka add-on.
"""

helps['containerapp add-on mariadb create'] = """
    type: command
    short-summary: Command to create the mariadb add-on.
"""

helps['containerapp add-on qdrant create'] = """
    type: command
    short-summary: Command to create the qdrant add-on.
"""

helps['containerapp add-on weaviate create'] = """
    type: command
    short-summary: Command to create the weaviate add-on.
"""

helps['containerapp add-on milvus create'] = """
    type: command
    short-summary: Command to create the milvus add-on.
"""

helps['containerapp add-on redis delete'] = """
    type: command
    short-summary: Command to delete the redis add-on.
"""

helps['containerapp add-on postgres delete'] = """
    type: command
    short-summary: Command to delete the postgres add-on.
"""

helps['containerapp add-on kafka delete'] = """
    type: command
    short-summary: Command to delete the kafka add-on.
"""

helps['containerapp add-on mariadb delete'] = """
    type: command
    short-summary: Command to delete the mariadb add-on.
"""

helps['containerapp add-on qdrant delete'] = """
    type: command
    short-summary: Command to delete the qdrant add-on.
"""

helps['containerapp add-on weaviate delete'] = """
    type: command
    short-summary: Command to delete the weaviate service.
"""

helps['containerapp add-on milvus delete'] = """
    type: command
    short-summary: Command to delete the milvus service.
"""

helps['containerapp env update'] = """
    type: command
    short-summary: Update a Container Apps environment.
    examples:
    - name: Update an environment's custom domain configuration.
      text: |
          az containerapp env update -n MyContainerappEnvironment -g MyResourceGroup \\
              --dns-suffix my-suffix.net --certificate-file MyFilePath \\
              --certificate-password MyCertPass
"""


helps['containerapp env delete'] = """
    type: command
    short-summary: Delete a Container Apps environment.
    examples:
    - name: Delete an environment.
      text: az containerapp env delete -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env show'] = """
    type: command
    short-summary: Show details of a Container Apps environment.
    examples:
    - name: Show the details of an environment.
      text: |
          az containerapp env show -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env list'] = """
    type: command
    short-summary: List Container Apps environments by subscription or resource group.
    examples:
    - name: List environments in the current subscription.
      text: |
          az containerapp env list
    - name: List environments by resource group.
      text: |
          az containerapp env list -g MyResourceGroup
"""

# Container Apps Job Commands
helps['containerapp job'] = """
    type: group
    short-summary: Commands to manage Container Apps jobs.
"""

helps['containerapp job create'] = """
    type: command
    short-summary: Create a container apps job.
    examples:
    - name: Create a container apps job with Trigger Type as Manual.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --trigger-type Manual \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --image imageName \\
              --workload-profile-name my-wlp
    - name: Create a container apps job with Trigger Type as Schedule.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --trigger-type Schedule \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --cron-expression \"*/1 * * * *\" \\
              --image imageName
    - name: Create a container apps job with Trigger Type as Event.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --trigger-type Event \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --polling-interval 30 \\
              --min-executions 0 \\
              --max-executions 1 \\
              --scale-rule-name queue \\
              --scale-rule-type azure-queue \\
              --scale-rule-metadata "accountName=mystorageaccountname" \\
                                    "cloud=AzurePublicCloud" \\
                                    "queueLength=5" "queueName=foo" \\
              --scale-rule-auth "connection=my-connection-string-secret-name" \\
              --image imageName
"""

helps['containerapp job delete'] = """
    type: command
    short-summary: Delete a Container Apps Job.
    examples:
    - name: Delete a job.
      text: az containerapp job delete -n my-containerapp-job -g MyResourceGroup
"""

helps['containerapp job show'] = """
    type: command
    short-summary: Show details of a Container Apps Job.
    examples:
    - name: Show the details of a job.
      text: |
          az containerapp job show -n my-containerapp-job -g MyResourceGroup
"""

helps['containerapp job list'] = """
    type: command
    short-summary: List Container Apps Job by subscription or resource group.
    examples:
    - name: List jobs in the current subscription.
      text: |
          az containerapp job list
    - name: List environments by resource group.
      text: |
          az containerapp job list -g MyResourceGroup
"""

helps['containerapp job start'] = """
    type: command
    short-summary: Start a Container Apps Job execution.
    examples:
    - name: Start a job execution.
      text: az containerapp job start -n my-containerapp-job -g MyResourceGroup
    - name: Start a job with different image and configurations.
      text: az containerapp job start -n my-containerapp-job -g MyResourceGroup --image MyImageName --cpu 0.5 --memory 1.0Gi
"""

helps['containerapp job stop'] = """
    type: command
    short-summary: Stops a Container Apps Job execution.
    examples:
    - name: Stop a job execution.
      text: az containerapp job stop -n my-containerapp-job -g MyResourceGroup
    - name: Stop a job execution giving a specific job execution name.
      text: az containerapp job stop -n my-containerapp-job -g MyResourceGroup --job-execution-name MyContainerAppJob-66v9xh0
    - name: Stop multiple job executions giving a list of execution names.
      text: az containerapp job stop -n my-containerapp-job -g MyResourceGroup --execution-name-list MyContainerAppJob-66v9xh0,MyContainerAppJob-66v9xh1
"""

# Certificates Commands
helps['containerapp env certificate'] = """
    type: group
    short-summary: Commands to manage certificates for the Container Apps environment.
"""

helps['containerapp env certificate create'] = """
    type: command
    short-summary: Create a managed certificate.
    examples:
    - name: Create a managed certificate.
      text: |
          az containerapp env certificate create -g MyResourceGroup --name MyEnvironment --certificate-name MyCertificate --hostname MyHostname --validation-method CNAME
"""

helps['containerapp env certificate upload'] = """
    type: command
    short-summary: Add or update a certificate.
    examples:
    - name: Add or update a certificate.
      text: |
          az containerapp env certificate upload -g MyResourceGroup --name MyEnvironment --certificate-file MyFilepath
    - name: Add or update a certificate with a user-provided certificate name.
      text: |
          az containerapp env certificate upload -g MyResourceGroup --name MyEnvironment --certificate-file MyFilepath --certificate-name MyCertificateName
    - name: Add or update a certificate from azure key vault using managed identity.
      text: |
          az containerapp env certificate upload -g MyResourceGroup --name MyEnvironment --akv-url akvSecretUrl --identity system
"""

helps['containerapp env certificate list'] = """
    type: command
    short-summary: List certificates for an environment.
    examples:
    - name: List certificates for an environment.
      text: |
          az containerapp env certificate list -g MyResourceGroup --name MyEnvironment
    - name: Show a certificate by certificate id.
      text: |
          az containerapp env certificate list -g MyResourceGroup --name MyEnvironment --certificate MyCertificateId
    - name: List certificates by certificate name.
      text: |
          az containerapp env certificate list -g MyResourceGroup --name MyEnvironment --certificate MyCertificateName
    - name: List certificates by certificate thumbprint.
      text: |
          az containerapp env certificate list -g MyResourceGroup --name MyEnvironment --thumbprint MyCertificateThumbprint
    - name: List managed certificates for an environment.
      text: |
          az containerapp env certificate list -g MyResourceGroup --name MyEnvironment --managed-certificates-only
    - name: List private key certificates for an environment.
      text: |
          az containerapp env certificate list -g MyResourceGroup --name MyEnvironment --private-key-certificates-only
"""

helps['containerapp env certificate delete'] = """
    type: command
    short-summary: Delete a certificate from the Container Apps environment.
    examples:
    - name: Delete a certificate from the Container Apps environment by certificate name
      text: |
          az containerapp env certificate delete -g MyResourceGroup --name MyEnvironment --certificate MyCertificateName
    - name: Delete a certificate from the Container Apps environment by certificate id
      text: |
          az containerapp env certificate delete -g MyResourceGroup --name MyEnvironment --certificate MyCertificateId
    - name: Delete all certificates that have a matching thumbprint from the Container Apps environment
      text: |
          az containerapp env certificate delete -g MyResourceGroup --name MyEnvironment --thumbprint MyCertificateThumbprint
"""

helps['containerapp env dapr-component init'] = """
    type: command
    short-summary: Initializes Dapr components and dev services for an environment.
    examples:
    - name: Initialize Dapr components with default statestore and pubsub.
      text: |
          az containerapp env dapr-component init -g MyResourceGroup --name MyEnvironment
    - name: Initialize Dapr components with Postgres statestore and Kafka pubsub.
      text: |
          az containerapp env dapr-component init -g MyResourceGroup --name MyEnvironment --statestore postgres --pubsub kafka
"""

helps['containerapp github-action'] = """
    type: group
    short-summary: Commands to manage GitHub Actions.
"""

helps['containerapp github-action add'] = """
    type: command
    short-summary: Add a GitHub Actions workflow to a repository to deploy a container app.
    examples:
    - name: Add GitHub Actions, using Azure Container Registry and personal access token.
      text: az containerapp github-action add -g MyResourceGroup -n my-containerapp --repo-url https://github.com/userid/repo --branch main
          --registry-url myregistryurl.azurecr.io
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --token MyAccessToken
    - name: Add GitHub Actions, using Azure Container Registry and personal access token, configure image build via build environment variables.
      text: az containerapp github-action add -g MyResourceGroup -n my-containerapp --repo-url https://github.com/userid/repo --branch main
          --registry-url myregistryurl.azurecr.io
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --token MyAccessToken
          --build-env-vars BP_JVM_VERSION=21 BP_MAVEN_VERSION=4
    - name: Add GitHub Actions, using Azure Container Registry and log in to GitHub flow to retrieve personal access token.
      text: az containerapp github-action add -g MyResourceGroup -n my-containerapp --repo-url https://github.com/userid/repo --branch main
          --registry-url myregistryurl.azurecr.io
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --login-with-github
    - name: Add GitHub Actions, using Docker Hub and log in to GitHub flow to retrieve personal access token.
      text: az containerapp github-action add -g MyResourceGroup -n my-containerapp --repo-url https://github.com/userid/repo --branch main
          --registry-username MyUsername
          --registry-password MyPassword
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --login-with-github
"""

helps['containerapp hostname'] = """
    type: group
    short-summary: Commands to manage hostnames of a container app.
"""

helps['containerapp hostname bind'] = """
    type: command
    short-summary: Add or update the hostname and binding with a certificate.
    examples:
    - name: Add or update hostname and binding with a provided certificate.
      text: |
          az containerapp hostname bind -n my-containerapp -g MyResourceGroup --hostname MyHostname --certificate MyCertificateId
    - name: Look for or create a managed certificate and bind with the hostname if no certificate or thumbprint is provided.
      text: |
          az containerapp hostname bind -n my-containerapp -g MyResourceGroup --hostname MyHostname
"""

# Auth commands
helps['containerapp auth'] = """
type: group
short-summary: Manage containerapp authentication and authorization.
"""

helps['containerapp auth show'] = """
type: command
short-summary: Show the authentication settings for the containerapp.
examples:
  - name: Show the authentication settings for the containerapp.
    text: az containerapp auth show --name my-containerapp --resource-group MyResourceGroup
"""

helps['containerapp auth update'] = """
type: command
short-summary: Update the authentication settings for the containerapp.
examples:
  - name: Update the client ID of the AAD provider already configured.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --set identityProviders.azureActiveDirectory.registration.clientId=my-client-id
  - name: Configure the app with file based authentication by setting the config file path.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --config-file-path D:\\home\\site\\wwwroot\\auth.json
  - name: Configure the app to allow unauthenticated requests to hit the app.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --unauthenticated-client-action AllowAnonymous
  - name: Configure the app to redirect unauthenticated requests to the Facebook provider.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --redirect-provider Facebook
  - name: Configure the app to listen to the forward headers X-FORWARDED-HOST and X-FORWARDED-PROTO.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --proxy-convention Standard
  - name: Configure the blob storage token store using default system assigned managed identity to authenticate.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --token-store true --blob-container-uri https://storageAccount1.blob.core.windows.net/container1
  - name: Configure the blob storage token store using user assigned managed identity to authenticate.
    text: |
        az containerapp auth update -g myResourceGroup --name my-containerapp --token-store true --blob-container-uri https://storageAccount1.blob.core.windows.net/container1 --blob-container-identity managedIdentityResourceId
"""

helps['containerapp env workload-profile set'] = """
    type: command
    short-summary: Create or update an existing workload profile in a Container Apps environment
    examples:
    - name: Create or update an existing workload profile in a Container Apps environment
      text: |
          az containerapp env workload-profile set -g MyResourceGroup -n MyEnvironment --workload-profile-name my-wlp --workload-profile-type D4 --min-nodes 1 --max-nodes 2
"""

helps['containerapp env storage set'] = """
    type: command
    short-summary: Create or update a storage.
    examples:
    - name: Create a azure file storage.
      text: |
          az containerapp env storage set -g MyResourceGroup -n MyEnv --storage-name MyStorageName --access-mode ReadOnly --azure-file-account-key MyAccountKey --azure-file-account-name MyAccountName --azure-file-share-name MyShareName
    - name: Create a nfs azure file storage.
      text: |
          az containerapp env storage set -g MyResourceGroup -n MyEnv --storage-name MyStorageName --storage-type NfsAzureFile --access-mode ReadOnly --server MyNfsServer.file.core.windows.net --file-share /MyNfsServer/MyShareName
"""

# Compose commands
helps['containerapp compose'] = """
    type: group
    short-summary: Commands to create Azure Container Apps from Compose specifications.
"""

helps['containerapp compose create'] = """
    type: command
    short-summary: Create one or more Container Apps in a new or existing Container App Environment from a Compose specification.
    examples:
    - name: Create a container app by implicitly passing in a Compose configuration file from current directory.
      text: |
          az containerapp compose create -g MyResourceGroup \\
              --environment MyContainerappEnv
    - name: Create a container app by explicitly passing in a Compose configuration file.
      text: |
          az containerapp compose create -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --compose-file-path "path/to/docker-compose.yml"
"""

# Patch commands
helps['containerapp patch'] = """
    type: group
    short-summary: Patch Azure Container Apps. Patching is only available for the apps built using the source to cloud feature. See https://aka.ms/aca-local-source-to-cloud
"""

helps['containerapp patch list'] = """
   type: command
   short-summary: List container apps that can be patched. Patching is only available for the apps built using the source to cloud feature. See https://aka.ms/aca-local-source-to-cloud
   examples:
    - name: List patchable container apps in the current subscription.
      text: |
          az containerapp patch list
    - name: List patchable container apps by resource group.
      text: |
          az containerapp patch list -g MyResourceGroup
    - name: List patchable container apps by managed environment.
      text: |
          az containerapp patch list -g MyResourceGroup --environment MyContainerAppEnv
    - name: List patchable and unpatchable container apps by managed environment with the show-all option.
      text: |
          az containerapp patch list -g MyResourceGroup --environment MyContainerAppEnv --show-all
"""

helps['containerapp patch apply'] = """
    type: command
    short-summary: List and apply container apps to be patched. Patching is only available for the apps built using the source to cloud feature. See https://aka.ms/aca-local-source-to-cloud
    examples:
    - name: List patchable container apps in the current subscription and apply patch.
      text: |
          az containerapp patch apply
    - name: List patchable container apps by resource group and apply patch.
      text: |
          az containerapp patch apply -g MyResourceGroup
    - name: List patchable container apps by managed environment and apply patch.
      text: |
          az containerapp patch apply -g MyResourceGroup --environment MyContainerAppEnv
    - name: List patchable and unpatchable container apps by managed environment with the show-all option and apply patch for patchable container apps.
      text: |
          az containerapp patch apply -g MyResourceGroup --environment MyContainerAppEnv --show-all
"""

helps['containerapp patch interactive'] = """
    type: command
    short-summary: List and select container apps to be patched in an interactive way. Patching is only available for the apps built using the source to cloud feature. See https://aka.ms/aca-local-source-to-cloud
    examples:
    - name: List patchable container apps in the current subscription and apply patch interactively.
      text: |
          az containerapp patch interactive
    - name: List patchable container apps by resource group and apply patch interactively.
      text: |
          az containerapp patch interactive -g MyResourceGroup
    - name: List patchable container apps by managed environment and apply patch interactively.
      text: |
          az containerapp patch interactive -g MyResourceGroup --environment MyContainerAppEnv
    - name: List patchable and unpatchable container apps by managed environment with the show-all option and apply patch for patchable container apps interactively.
      text: |
          az containerapp patch interactive -g MyResourceGroup --environment MyContainerAppEnv --show-all
"""

# containerapp create for preview
helps['containerapp create'] = """
    type: command
    short-summary: Create a container app.
    examples:
    - name: Create a container app and retrieve its fully qualified domain name.
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image myregistry.azurecr.io/my-app:v1.0 --environment MyContainerappEnv \\
              --ingress external --target-port 80 \\
              --registry-server myregistry.azurecr.io --registry-username myregistry --registry-password $REGISTRY_PASSWORD \\
              --query properties.configuration.ingress.fqdn
    - name: Create a container app with resource requirements and replica count limits.
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image nginx --environment MyContainerappEnv \\
              --cpu 0.5 --memory 1.0Gi \\
              --min-replicas 4 --max-replicas 8
    - name: Create a container app with secrets and environment variables.
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --secrets mysecret=secretvalue1 anothersecret="secret value 2" \\
              --env-vars GREETING="Hello, world" SECRETENV=secretref:anothersecret
    - name: Create a container app using a YAML configuration. Example YAML configuration - https://aka.ms/azure-container-apps-yaml
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --yaml "path/to/yaml/file.yml"
    - name: Create a container app with an http scale rule
      text: |
          az containerapp create -n myapp -g mygroup --environment myenv --image nginx \\
              --scale-rule-name my-http-rule \\
              --scale-rule-http-concurrency 50
    - name: Create a container app with a custom scale rule
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-queue-processor --environment MyContainerappEnv \\
              --min-replicas 4 --max-replicas 8 \\
              --scale-rule-name queue-based-autoscaling \\
              --scale-rule-type azure-queue \\
              --scale-rule-metadata "accountName=mystorageaccountname" \\
                                    "cloud=AzurePublicCloud" \\
                                    "queueLength=5" "queueName=foo" \\
              --scale-rule-auth "connection=my-connection-string-secret-name"
    - name: Create a container app with a custom scale rule using identity to authenticate
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-queue-processor --environment MyContainerappEnv \\
              --user-assigned myUserIdentityResourceId --min-replicas 4 --max-replicas 8 \\
              --scale-rule-name queue-based-autoscaling \\
              --scale-rule-type azure-queue \\
              --scale-rule-metadata "accountName=mystorageaccountname" \\
                                    "cloud=AzurePublicCloud" \\
                                    "queueLength=5" "queueName=foo" \\
              --scale-rule-identity myUserIdentityResourceId
    - name: Create a container app with secrets and mounts them in a volume.
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --secrets mysecret=secretvalue1 anothersecret="secret value 2" \\
              --secret-volume-mount "mnt/secrets"
    - name: Create a container app hosted on a Connected Environment.
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappConnectedEnv \\
              --environment-type connected
    - name: Create a container app from a new GitHub Actions workflow in the provided GitHub repository
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
          --environment MyContainerappEnv --registry-server MyRegistryServer \\
          --registry-user MyRegistryUser --registry-pass MyRegistryPass \\
          --repo https://github.com/myAccount/myRepo
    - name: Create a Container App from the provided application source
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
          --environment MyContainerappEnv --registry-server MyRegistryServer \\
          --registry-user MyRegistryUser --registry-pass MyRegistryPass \\
          --source .
    - name: Create a container app with java metrics enabled
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --enable-java-metrics
    - name: Create a container app with java agent enabled
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --enable-java-agent
    - name: Create an Azure Functions on Azure Container Apps (kind=functionapp)
      text: |
          az containerapp create -n my-containerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --kind functionapp
"""

# containerapp update for preview
helps['containerapp update'] = """
    type: command
    short-summary: Update a container app. In multiple revisions mode, create a new revision based on the latest revision.
    examples:
    - name: Update a container app's container image.
      text: |
          az containerapp update -n my-containerapp -g MyResourceGroup \\
              --image myregistry.azurecr.io/my-app:v2.0
    - name: Update a container app's resource requirements and scale limits.
      text: |
          az containerapp update -n my-containerapp -g MyResourceGroup \\
              --cpu 0.5 --memory 1.0Gi \\
              --min-replicas 4 --max-replicas 8
    - name: Update a container app with an http scale rule
      text: |
          az containerapp update -n myapp -g mygroup \\
              --scale-rule-name my-http-rule \\
              --scale-rule-http-concurrency 50
    - name: Update a container app with a custom scale rule
      text: |
          az containerapp update -n myapp -g mygroup \\
              --scale-rule-name my-custom-rule \\
              --scale-rule-type my-custom-type \\
              --scale-rule-metadata key=value key2=value2 \\
              --scale-rule-auth triggerparam=secretref triggerparam=secretref
    - name: Update a Container App from the provided application source
      text: |
          az containerapp update -n my-containerapp -g MyResourceGroup --source .
    - name: Update a container app with java metrics enabled
      text: |
          az containerapp update -n my-containerapp -g MyResourceGroup \\
              --enable-java-metrics
    - name: Update a container app with java agent enabled
      text: |
          az containerapp update -n my-containerapp -g MyResourceGroup \\
              --enable-java-agent
    - name: Update a container app to erase java enhancement capabilities, like java metrics, java agent, etc.
      text: |
          az containerapp update -n my-containerapp -g MyResourceGroup \\
              --runtime generic
"""

# containerapp list for preview
helps['containerapp list'] = """
    type: command
    short-summary: List container apps.
    examples:
    - name: List container apps in the current subscription.
      text: |
          az containerapp list
    - name: List container apps by resource group.
      text: |
          az containerapp list -g MyResourceGroup
    - name: List container apps by environment type.
      text: |
          az containerapp list --environment-type connected
"""

# Connected Environment Commands
helps['containerapp connected-env'] = """
    type: group
    short-summary: Commands to manage Container Apps Connected environments for use with Arc enabled Container Apps.
"""

helps['containerapp connected-env create'] = """
    type: command
    short-summary: Create a Container Apps connected environment.
    long-summary: Create a Container Apps Connected environment for use with Arc enabled Container Apps.  Environments are an isolation boundary around a collection of container apps.
    examples:
    - name: Create a connected environment
      text: |
          az containerapp connected-env create -n MyContainerappConnectedEnv -g MyResourceGroup \\
              --location eastus --custom-location MyCustomLocationResourceID
"""

helps['containerapp connected-env delete'] = """
    type: command
    short-summary: Delete a Container Apps connected environment.
    examples:
    - name: Delete a connected environment.
      text: az containerapp connected-env delete -n MyContainerappConnectedEnv -g MyResourceGroup
"""

helps['containerapp connected-env show'] = """
    type: command
    short-summary: Show details of a Container Apps connected environment.
    examples:
    - name: Show the details of a connected environment.
      text: |
          az containerapp connected-env show -n MyContainerappConnectedEnv -g MyResourceGroup
"""

helps['containerapp connected-env list'] = """
    type: command
    short-summary: List Container Apps connected environments by subscription or resource group.
    examples:
    - name: List connected environments in the current subscription.
      text: |
          az containerapp connected-env list
    - name: List connected environments by resource group.
      text: |
          az containerapp connected-env list -g MyResourceGroup
"""

helps['containerapp arc'] = """
    type: group
    short-summary: Install prerequisites for Kubernetes cluster on Arc
"""

helps['containerapp arc setup-core-dns'] = """
    type: command
    short-summary: Setup CoreDNS for Kubernetes cluster on Arc
    examples:
    - name: Setup CoreDNS for Aks on Azure Local on Arc
      text: |
          az containerapp arc setup-core-dns --distro AksAzureLocal
    - name: Setup CoreDNS for Aks on Azure Local on Arc by specifying the kubeconfig and kubecontext.
      text: |
          az containerapp arc setup-core-dns --distro AksAzureLocal --kube-config /path/to/kubeconfig --kube-context kubeContextName
"""

helps['containerapp connected-env dapr-component'] = """
    type: group
    short-summary: Commands to manage Dapr components for Container Apps connected environments.
"""

helps['containerapp connected-env dapr-component list'] = """
    type: command
    short-summary: List Dapr components for a connected environment.
    examples:
    - name: List Dapr components for a connected environment.
      text: |
          az containerapp connected-env dapr-component list -g MyResourceGroup --name MyConnectedEnv
"""

helps['containerapp connected-env dapr-component show'] = """
    type: command
    short-summary: Show the details of a Dapr component.
    examples:
    - name: Show the details of a Dapr component.
      text: |
          az containerapp connected-env dapr-component show -g MyResourceGroup --dapr-component-name MyDaprComponentName --name MyConnectedEnv
"""

helps['containerapp connected-env dapr-component set'] = """
    type: command
    short-summary: Create or update a Dapr component.
    examples:
    - name: Create a Dapr component.
      text: |
          az containerapp connected-env dapr-component set -g MyResourceGroup --name MyEnv --yaml MyYAMLPath --dapr-component-name MyDaprComponentName
"""

helps['containerapp connected-env dapr-component remove'] = """
    type: command
    short-summary: Remove a Dapr component from a connected environment.
    examples:
    - name: Remove a Dapr component from a Container Apps connected environment.
      text: |
          az containerapp connected-env dapr-component remove -g MyResourceGroup --dapr-component-name MyDaprComponentName --name MyConnectedEnv
"""

helps['containerapp connected-env storage'] = """
    type: group
    short-summary: Commands to manage storage for the Container Apps connected environment.
"""

helps['containerapp connected-env storage list'] = """
    type: command
    short-summary: List the storages for a connected environment.
    examples:
    - name: List the storages for a connected environment.
      text: |
          az containerapp connected-env storage list -g MyResourceGroup -n MyConnectedEnv
"""

helps['containerapp connected-env storage show'] = """
    type: command
    short-summary: Show the details of a storage.
    examples:
    - name: Show the details of a storage.
      text: |
          az containerapp connected-env storage show -g MyResourceGroup --storage-name MyStorageName -n MyConnectedEnv
"""

helps['containerapp connected-env storage set'] = """
    type: command
    short-summary: Create or update a storage.
    examples:
    - name: Create a storage.
      text: |
          az containerapp connected-env storage set -g MyResourceGroup -n MyEnv --storage-name MyStorageName --access-mode ReadOnly --azure-file-account-key MyAccountKey --azure-file-account-name MyAccountName --azure-file-share-name MyShareName
"""

helps['containerapp connected-env storage remove'] = """
    type: command
    short-summary: Remove a storage from a connected environment.
    examples:
    - name: Remove a storage from a Container Apps connected environment.
      text: |
          az containerapp connected-env storage remove -g MyResourceGroup --storage-name MyStorageName -n MyConnectedEnv
"""

# Certificates Commands
helps['containerapp connected-env certificate'] = """
    type: group
    short-summary: Commands to manage certificates for the Container Apps connected environment.
"""

helps['containerapp connected-env certificate list'] = """
    type: command
    short-summary: List certificates for a connected environment.
    examples:
    - name: List certificates for a connected environment.
      text: |
          az containerapp connected-env certificate list -g MyResourceGroup --name MyConnectedEnv
    - name: List certificates by certificate id.
      text: |
          az containerapp connected-env certificate list -g MyResourceGroup --name MyConnectedEnv --certificate MyCertificateId
    - name: List certificates by certificate name.
      text: |
          az containerapp connected-env certificate list -g MyResourceGroup --name MyConnectedEnv --certificate MyCertificateName
    - name: List certificates by certificate thumbprint.
      text: |
          az containerapp connected-env certificate list -g MyResourceGroup --name MyConnectedEnv --thumbprint MyCertificateThumbprint
"""

helps['containerapp connected-env certificate upload'] = """
    type: command
    short-summary: Add or update a certificate.
    examples:
    - name: Add or update a certificate.
      text: |
          az containerapp connected-env certificate upload -g MyResourceGroup --name MyConnectedEnv --certificate-file MyFilepath
    - name: Add or update a certificate with a user-provided certificate name.
      text: |
          az containerapp connected-env certificate upload -g MyResourceGroup --name MyConnectedEnv --certificate-file MyFilepath --certificate-name MyCertificateName
"""

helps['containerapp connected-env certificate delete'] = """
    type: command
    short-summary: Delete a certificate from the Container Apps connected environment.
    examples:
    - name: Delete a certificate from the Container Apps connected environment by certificate name
      text: |
          az containerapp connected-env certificate delete -g MyResourceGroup --name MyConnectedEnv --certificate MyCertificateName
    - name: Delete a certificate from the Container Apps connected environment by certificate id
      text: |
          az containerapp connected-env certificate delete -g MyResourceGroup --name MyConnectedEnv --certificate MyCertificateId
    - name: Delete a certificate from the Container Apps connected environment by certificate thumbprint
      text: |
          az containerapp connected-env certificate delete -g MyResourceGroup --name MyConnectedEnv --thumbprint MyCertificateThumbprint
"""

# Container Apps Job Commands

helps['containerapp job create'] = """
    type: command
    short-summary: Create a container apps job.
    examples:
    - name: Create a container apps job with Trigger Type as Manual.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --trigger-type Manual \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --image imageName \\
              --workload-profile-name my-wlp
    - name: Create a container apps job with Trigger Type as Schedule.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --trigger-type Schedule \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --cron-expression \"*/1 * * * *\" \\
              --image imageName
    - name: Create a container apps job with Trigger Type as Event.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --trigger-type Event \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --polling-interval 30 \\
              --min-executions 0 \\
              --max-executions 1 \\
              --scale-rule-name queueJob \\
              --scale-rule-type azure-queue \\
              --scale-rule-metadata "accountName=mystorageaccountname" \\
                                    "cloud=AzurePublicCloud" \\
                                    "queueLength=5" "queueName=foo" \\
              --scale-rule-auth "connection=my-connection-string-secret-name" \\
              --image imageName
    - name: Create container app job with Trigger Type as Event using identity to authenticate
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappEnv
              --trigger-type Event \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --polling-interval 30 \\
              --min-executions 0 \\
              --max-executions 1 \\
              --scale-rule-name azure-queue \\
              --scale-rule-type azure-queue \\
              --scale-rule-metadata "accountName=mystorageaccountname" \\
                                    "cloud=AzurePublicCloud" \\
                                    "queueLength=5" "queueName=foo" \\
              --scale-rule-identity myUserIdentityResourceId \\
              --image imageName
    - name: Create a container apps job hosted on a Connected Environment.
      text: |
          az containerapp job create -n MyContainerappsjob -g MyResourceGroup \\
              --environment MyContainerappConnectedEnv
              --environment-type connected
              --trigger-type Manual \\
              --replica-timeout 5 \\
              --replica-retry-limit 2 \\
              --replica-completion-count 1 \\
              --parallelism 1 \\
              --image imageName \\
              --workload-profile-name my-wlp
"""

# Java Components Commands
helps['containerapp env java-component'] = """
    type: group
    short-summary: Commands to manage Java components within the environment.
"""

helps['containerapp env java-component list'] = """
    type: command
    short-summary: List all Java components within the environment.
    examples:
    - name: List all Java components within an environment.
      text: |
          az containerapp env java-component list -g MyResourceGroup --environment MyEnvironment
"""

helps['containerapp env java-component spring-cloud-config'] = """
    type: group
    short-summary: Commands to manage the Config Server for Spring for the Container Apps environment.
    deprecate_info: This command group is deprecated. Use 'az containerapp env java-component config-server-for-spring' instead.
"""

helps['containerapp env java-component spring-cloud-config create'] = """
    type: command
    short-summary: Command to create the Spring Cloud Config.
    examples:
    - name: Create a Spring Cloud Config.
      text: |
          az containerapp env java-component spring-cloud-config create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
"""

helps['containerapp env java-component spring-cloud-config delete'] = """
    type: command
    short-summary: Command to delete the Spring Cloud Config.
    examples:
    - name: Delete a Spring Cloud Config.
      text: |
          az containerapp env java-component spring-cloud-config delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component spring-cloud-config show'] = """
    type: command
    short-summary: Command to show the Spring Cloud Config.
    examples:
    - name: Show a Spring Cloud Config.
      text: |
          az containerapp env java-component spring-cloud-config show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component spring-cloud-config update'] = """
    type: command
    short-summary: Command to update the Spring Cloud Config.
    examples:
    - name: Delete all configurations of the Spring Cloud Config.
      text: |
          az containerapp env java-component spring-cloud-config update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
    - name: Update a Spring Cloud Config with custom configurations.
      text: |
          az containerapp env java-component spring-cloud-config update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
"""

helps['containerapp env java-component config-server-for-spring'] = """
    type: group
    short-summary: Commands to manage the Config Server for Spring for the Container Apps environment.
"""

helps['containerapp env java-component config-server-for-spring create'] = """
    type: command
    short-summary: Command to create the Config Server for Spring.
    examples:
    - name: Create a Config Server for Spring.
      text: |
          az containerapp env java-component config-server-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Create a Config Server for Spring with multiple replicas.
      text: |
          az containerapp env java-component config-server-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --min-replicas 2 --max-replicas 2
"""

helps['containerapp env java-component config-server-for-spring delete'] = """
    type: command
    short-summary: Command to delete the Config Server for Spring.
    examples:
    - name: Delete a Config Server for Spring.
      text: |
          az containerapp env java-component config-server-for-spring delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component config-server-for-spring show'] = """
    type: command
    short-summary: Command to show the Config Server for Spring.
    examples:
    - name: Show a Config Server for Spring.
      text: |
          az containerapp env java-component config-server-for-spring show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component config-server-for-spring update'] = """
    type: command
    short-summary: Command to update the Config Server for Spring.
    examples:
    - name: Update a Config Server for Spring with custom configurations.
      text: |
          az containerapp env java-component config-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Replace all configurations of the Config Server for Spring.
      text: |
          az containerapp env java-component config-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --replace-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Delete configurations of the Config Server for Spring.
      text: |
          az containerapp env java-component config-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-configurations PropertyName1 PropertyName2
    - name: Delete all configurations of the Config Server for Spring.
      text: |
          az containerapp env java-component config-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
"""

helps['containerapp env java-component spring-cloud-eureka'] = """
    type: group
    short-summary: Commands to manage the Spring Cloud Eureka for the Container Apps environment.
    deprecate_info: This command group is deprecated. Use 'az containerapp env java-component eureka-server-for-spring' instead.
"""

helps['containerapp env java-component spring-cloud-eureka create'] = """
    type: command
    short-summary: Command to create the Spring Cloud Eureka.
    examples:
    - name: Create a Spring Cloud Eureka with default configuration.
      text: |
          az containerapp env java-component spring-cloud-eureka create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
    - name: Create a Spring Cloud Eureka with custom configurations.
      text: |
          az containerapp env java-component spring-cloud-eureka create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
"""

helps['containerapp env java-component spring-cloud-eureka delete'] = """
    type: command
    short-summary: Command to delete the Spring Cloud Eureka.
    examples:
    - name: Delete a Spring Cloud Eureka.
      text: |
          az containerapp env java-component spring-cloud-eureka delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component spring-cloud-eureka show'] = """
    type: command
    short-summary: Command to show the Spring Cloud Eureka.
    examples:
    - name: Show a Spring Cloud Eureka.
      text: |
          az containerapp env java-component spring-cloud-eureka show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component spring-cloud-eureka update'] = """
    type: command
    short-summary: Command to update the Spring Cloud Eureka.
    examples:
    - name: Delete all configurations of the Spring Cloud Eureka.
      text: |
          az containerapp env java-component spring-cloud-eureka update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
    - name: Update a Spring Cloud Eureka with custom configurations.
      text: |
          az containerapp env java-component spring-cloud-eureka update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
"""

helps['containerapp env java-component eureka-server-for-spring'] = """
    type: group
    short-summary: Commands to manage the Eureka Server for Spring for the Container Apps environment.
"""

helps['containerapp env java-component eureka-server-for-spring create'] = """
    type: command
    short-summary: Command to create the Eureka Server for Spring.
    examples:
    - name: Create an Eureka Server for Spring with default configuration.
      text: |
          az containerapp env java-component eureka-server-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
    - name: Create an Eureka Server for Spring with custom configurations.
      text: |
          az containerapp env java-component eureka-server-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
"""

helps['containerapp env java-component eureka-server-for-spring delete'] = """
    type: command
    short-summary: Command to delete the Eureka Server for Spring.
    examples:
    - name: Delete an Eureka Server for Spring.
      text: |
          az containerapp env java-component eureka-server-for-spring delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component eureka-server-for-spring show'] = """
    type: command
    short-summary: Command to show the Eureka Server for Spring.
    examples:
    - name: Show an Eureka Server for Spring.
      text: |
          az containerapp env java-component eureka-server-for-spring show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component eureka-server-for-spring update'] = """
    type: command
    short-summary: Command to update the Eureka Server for Spring.
    examples:
    - name: Update an Eureka Server for Spring with custom configurations.
      text: |
          az containerapp env java-component eureka-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Replace all configurations of the Eureka Server for Spring.
      text: |
          az containerapp env java-component eureka-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --replace-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Delete configurations of the Eureka Server for Spring.
      text: |
          az containerapp env java-component eureka-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-configurations PropertyName1 PropertyName2
    - name: Delete all configurations of the Eureka Server for Spring.
      text: |
          az containerapp env java-component eureka-server-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
"""

helps['containerapp env java-component admin-for-spring'] = """
    type: group
    short-summary: Commands to manage the Admin for Spring for the Container Apps environment.
"""

helps['containerapp env java-component admin-for-spring create'] = """
    type: command
    short-summary: Command to create the Admin for Spring.
    examples:
    - name: Create an Admin for Spring with default configuration.
      text: |
          az containerapp env java-component admin-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
    - name: Create an Admin for Spring with custom configurations.
      text: |
          az containerapp env java-component admin-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Create an Admin for Spring with multiple replicas.
      text: |
          az containerapp env java-component admin-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --min-replicas 2 --max-replicas 2
"""

helps['containerapp env java-component admin-for-spring delete'] = """
    type: command
    short-summary: Command to delete the Admin for Spring.
    examples:
    - name: Delete an Admin for Spring.
      text: |
          az containerapp env java-component admin-for-spring delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component admin-for-spring show'] = """
    type: command
    short-summary: Command to show the Admin for Spring.
    examples:
    - name: Show an Admin for Spring.
      text: |
          az containerapp env java-component admin-for-spring show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component admin-for-spring update'] = """
    type: command
    short-summary: Command to update the Admin for Spring.
    examples:
    - name: Update an Admin for Spring with custom configurations.
      text: |
          az containerapp env java-component admin-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Replace all configurations of the Admin for Spring.
      text: |
          az containerapp env java-component admin-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --replace-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Delete configurations of the Admin for Spring.
      text: |
          az containerapp env java-component admin-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-configurations PropertyName1 PropertyName2
    - name: Delete all configurations of the Admin for Spring.
      text: |
          az containerapp env java-component admin-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
"""

helps['containerapp env java-component nacos'] = """
    type: group
    short-summary: Commands to manage the Nacos for the Container Apps environment.
"""

helps['containerapp env java-component nacos create'] = """
    type: command
    short-summary: Command to create the Nacos.
    examples:
    - name: Create a Nacos with default configuration.
      text: |
          az containerapp env java-component nacos create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
    - name: Create a Nacos with custom configurations.
      text: |
          az containerapp env java-component nacos create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
"""

helps['containerapp env java-component nacos delete'] = """
    type: command
    short-summary: Command to delete the Nacos.
    examples:
    - name: Delete a Nacos.
      text: |
          az containerapp env java-component nacos delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component nacos show'] = """
    type: command
    short-summary: Command to show the Nacos.
    examples:
    - name: Show an Nacos.
      text: |
          az containerapp env java-component nacos show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component nacos update'] = """
    type: command
    short-summary: Command to update the Nacos.
    examples:
    - name: Update an Nacos with custom configurations.
      text: |
          az containerapp env java-component nacos update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Replace all configurations of the nacos.
      text: |
          az containerapp env java-component nacos update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --replace-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Delete configurations of the nacos.
      text: |
          az containerapp env java-component nacos update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-configurations PropertyName1 PropertyName2
    - name: Delete all configurations of the nacos.
      text: |
          az containerapp env java-component nacos update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
"""

helps['containerapp env java-component gateway-for-spring'] = """
    type: group
    short-summary: Commands to manage the Gateway for Spring for the Container Apps environment.
"""

helps['containerapp env java-component gateway-for-spring create'] = """
    type: command
    short-summary: Command to create the Gateway for Spring.
    examples:
    - name: Create a Gateway for Spring with default configuration.
      text: |
          az containerapp env java-component gateway-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --route-yaml MyRouteYamlFilePath
    - name: Create a Gateway for Spring with custom configurations.
      text: |
          az containerapp env java-component gateway-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --route-yaml MyRouteYamlFilePath \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Create a Gateway for Spring with multiple replicas.
      text: |
          az containerapp env java-component gateway-for-spring create -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --route-yaml MyRouteYamlFilePath \\
              --min-replicas 2 --max-replicas 2
"""

helps['containerapp env java-component gateway-for-spring delete'] = """
    type: command
    short-summary: Command to delete the Gateway for Spring.
    examples:
    - name: Delete a Gateway for Spring.
      text: |
          az containerapp env java-component gateway-for-spring delete -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component gateway-for-spring show'] = """
    type: command
    short-summary: Command to show the Gateway for Spring.
    examples:
    - name: Show Gateway for Spring.
      text: |
          az containerapp env java-component gateway-for-spring show -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env java-component gateway-for-spring update'] = """
    type: command
    short-summary: Command to update the Gateway for Spring.
    examples:
    - name: Update a Gateway for Spring with new routes.
      text: |
          az containerapp env java-component gateway-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --route-yaml MyRouteYamlFilePath
    - name: Update a Gateway for Spring with custom configurations.
      text: |
          az containerapp env java-component gateway-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --set-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Replace all configurations of the Gateway for Spring.
      text: |
          az containerapp env java-component gateway-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --replace-configurations PropertyName1=Value1 PropertyName2=Value2
    - name: Delete configurations of the Gateway for Spring.
      text: |
          az containerapp env java-component gateway-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-configurations PropertyName1 PropertyName2
    - name: Delete all configurations of the Gateway for Spring.
      text: |
          az containerapp env java-component gateway-for-spring update -g MyResourceGroup \\
              -n MyJavaComponentName \\
              --environment MyEnvironment \\
              --remove-all-configurations
"""

# Container Apps Telemetry Commands

helps['containerapp env telemetry'] = """
    type: group
    short-summary: Commands to manage telemetry settings for the container apps environment.
"""

helps['containerapp env telemetry data-dog'] = """
    type: group
    short-summary: Commands to manage data dog settings for the container apps environment.
"""

helps['containerapp env telemetry app-insights'] = """
    type: group
    short-summary: Commands to manage app insights settings for the container apps environment.
"""

helps['containerapp env telemetry data-dog set'] = """
    type: command
    short-summary: Create or update container apps environment telemetry data dog settings.
    examples:
    - name: Create or update container apps environment telemetry data dog settings.
      text: |
          az containerapp env telemetry data-dog set -n MyContainerappEnvironment -g MyResourceGroup \\
              --site dataDogSite --key dataDogKey --enable-open-telemetry-traces true --enable-open-telemetry-metrics true
"""

helps['containerapp env telemetry data-dog show'] = """
    type: command
    short-summary: Show container apps environment telemetry data dog settings.
    examples:
    - name: Show container apps environment telemetry data dog settings.
      text: |
          az containerapp env telemetry data-dog show -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env telemetry app-insights set'] = """
    type: command
    short-summary: Create or update container apps environment telemetry app insights settings.
    examples:
    - name: Create or update container apps environment telemetry app insights settings.
      text: |
          az containerapp env telemetry app-insights set -n MyContainerappEnvironment -g MyResourceGroup \\
              --connection-string connectionString --enable-open-telemetry-traces true --enable-open-telemetry-logs true
"""

helps['containerapp env telemetry app-insights show'] = """
    type: command
    short-summary: Show container apps environment telemetry app insights settings.
    examples:
    - name: Show container apps environment telemetry app insights settings.
      text: |
          az containerapp env telemetry app-insights show -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env telemetry data-dog delete'] = """
    type: command
    short-summary: Delete container apps environment telemetry data dog settings.
    examples:
    - name: Delete container apps environment telemetry data dog settings.
      text: |
          az containerapp env telemetry data-dog delete -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env telemetry app-insights delete'] = """
    type: command
    short-summary: Delete container apps environment telemetry app insights settings.
    examples:
    - name: Delete container apps environment telemetry app insights settings.
      text: |
          az containerapp env telemetry app-insights delete -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env telemetry otlp'] = """
    type: group
    short-summary: Commands to manage otlp settings for the container apps environment.
"""

helps['containerapp env telemetry otlp add'] = """
    type: command
    short-summary: Add container apps environment telemetry otlp settings.
    examples:
    - name: Add container apps environment telemetry otlp settings.
      text: |
          az containerapp env telemetry otlp add -n MyContainerappEnvironment -g MyResourceGroup \\
              --otlp-name otlpName --endpoint otlpEndpoint --insecure false --headers api-key=apiKey \\
              --enable-open-telemetry-traces true --enable-open-telemetry-logs true --enable-open-telemetry-metrics true
"""

helps['containerapp env telemetry otlp update'] = """
    type: command
    short-summary: Update container apps environment telemetry otlp settings.
    examples:
    - name: Update container apps environment telemetry otlp settings.
      text: |
          az containerapp env telemetry otlp update -n MyContainerappEnvironment -g MyResourceGroup \\
              --otlp-name otlpName --endpoint otlpEndpoint --insecure false --headers api-key=apiKey \\
              --enable-open-telemetry-traces true --enable-open-telemetry-logs true --enable-open-telemetry-metrics true
"""

helps['containerapp env telemetry otlp remove'] = """
    type: command
    short-summary: Remove container apps environment telemetry otlp settings.
    examples:
    - name: Remove container apps environment telemetry otlp settings.
      text: |
          az containerapp env telemetry otlp remove -n MyContainerappEnvironment -g MyResourceGroup \\
              --otlp-name otlpName
"""

helps['containerapp env telemetry otlp show'] = """
    type: command
    short-summary: Show container apps environment telemetry otlp settings.
    examples:
    - name: Show container apps environment telemetry otlp settings.
      text: |
          az containerapp env telemetry otlp show -n MyContainerappEnvironment -g MyResourceGroup \\
              --otlp-name otlpName
"""

helps['containerapp env telemetry otlp list'] = """
    type: command
    short-summary: List container apps environment telemetry otlp settings.
    examples:
    - name: List container apps environment telemetry otlp settings.
      text: |
          az containerapp env telemetry otlp list -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp job logs'] = """
    type: group
    short-summary: Show container app job logs
"""

helps['containerapp job logs show'] = """
    type: command
    short-summary: Show past logs and/or print logs in real time (with the --follow parameter). Note that the logs are only taken from one execution, replica, and container.
    examples:
    - name: Fetch the past 20 lines of logs from a job and return
      text: |
          az containerapp job logs show -n my-containerappjob -g MyResourceGroup --container MyContainer
    - name: Fetch 30 lines of past logs logs from a job and print logs as they come in
      text: |
          az containerapp job logs show -n my-containerappjob -g MyResourceGroup --container MyContainer --follow --tail 30
    - name: Fetch logs for a particular execution, replica, and container
      text: |
          az containerapp job logs show -n my-containerappjob -g MyResourceGroup --execution MyExecution --replica MyReplica --container MyContainer
"""

helps['containerapp job replica'] = """
    type: group
    short-summary: Manage container app replicas
"""

helps['containerapp job replica list'] = """
    type: command
    short-summary: List a container app job execution's replica
    examples:
    - name: List a container app job's replicas in a particular execution
      text: |
          az containerapp job replica list -n my-containerappjob -g MyResourceGroup --execution MyExecution
"""

# SessionPool Commands
helps['containerapp sessionpool'] = """
    type: group
    short-summary: Commands to manage session pools.
"""

helps['containerapp sessionpool create'] = """
    type: command
    short-summary: Create or update a Session pool.
    examples:
    - name: Create or update a Session Pool with container type PythonLTS default settings.
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --location eastasia
    - name: Create or update a Session Pool with container type PythonLTS, with max concurrent sessions is 30, ready session instances 20.
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --container-type PythonLTS --max-sessions 30 --ready-sessions 20 \\
              --location eastasia
    - name: Create or update a Session Pool with container type CustomContainer with default quickstart image.
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --container-type CustomContainer --environment MyEnvironment \\
              --cpu 0.5 --memory 1Gi --target-port 80 --location eastasia --image mcr.microsoft.com/k8se/quickstart:latest
    - name: Create or update a Session Pool with container type CustomContainer that has secrets and environment variables.
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --container-type CustomContainer --environment MyEnvironment \\
              --cpu 0.5 --memory 1Gi --target-port 80 --image MyImage \\
              --env-vars GREETING="Hello, world" SECRETENV=secretref:anothersecret \\
              --secrets mysecret=secretvalue1 anothersecret="secret value 2" --location eastasia
    - name: Create or update a Session Pool with container type CustomContainer that from private registry
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --container-type CustomContainer --environment MyEnvironment --image MyImage \\
              --cpu 0.5 --memory 1Gi --target-port 80 --registry-server myregistry.azurecr.io \\
              --registry-username myregistry --registry-password $REGISTRY_PASSWORD \\
              --location eastasia
    - name: Create or update a Session Pool with container type CustomContainer and Managed Identity to authenticate Azure container registry
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --container-type CustomContainer --environment MyEnvironment --image MyImage \\
              --cpu 0.5 --memory 1Gi --target-port 80 --registry-server myregistry.azurecr.io \\
              --registry-identity  MyUserIdentityResourceId \\
              --location eastasia
    - name: Create or update a Session Pool with container type CustomContainer with system assigned and user assigned identity.
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --container-type CustomContainer --environment MyEnvironment --image MyImage \\
              --cpu 0.5 --memory 1Gi --target-port 80 \\
              --mi-system-assigned --mi-user-assigned MyUserIdentityResourceId \\
              --location eastasia
    - name: Create or update a Session Pool with container type CustomContainer with cooldown period 360s
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --environment MyEnvironment --cpu 0.5 --memory 1Gi --target-port 80 --container-type CustomContainer \\
              --cooldown-period 360 --location eastasia
    - name: Create or update a Session Pool with container type CustomContainer with container probes
      text: |
          az containerapp sessionpool create -n mysessionpool -g MyResourceGroup \\
              --environment MyEnvironment --cpu 0.5 --memory 1Gi --target-port 80 --container-type CustomContainer \\
              --probe-yaml config.yaml --location eastasia
"""

helps['containerapp sessionpool update'] = """
    type: command
    short-summary: Update a Session pool.
    examples:
    - name: Update a session pool's max concurrent sessions configuration and image.
      text: |
          az containerapp sessionpool update -n mysessionpool -g MyResourceGroup --max-sessions 20 --image MyNewImage
    - name: Update the container probes of a CustomContainer type session pool.
      text: |
          az containerapp sessionpool update -n mysessionpool -g MyResourceGroup --probe-yaml config.yaml
"""

helps['containerapp sessionpool delete'] = """
    type: command
    short-summary: Delete a session pool.
    examples:
    - name: Delete a session pool.
      text: az containerapp sessionpool delete -n mysessionpool -g MyResourceGroup
"""

helps['containerapp sessionpool show'] = """
    type: command
    short-summary: Show details of a Session Pool.
    examples:
    - name: Show the details of a Session Pool.
      text: |
          az containerapp sessionpool show -n mysessionpool -g MyResourceGroup
"""

helps['containerapp sessionpool list'] = """
    type: command
    short-summary: List Session Pools by subscription or resource group.
    examples:
    - name: List Session Pools in the current subscription.
      text: |
          az containerapp sessionpool list
    - name: List Session Pools by resource group.
      text: |
          az containerapp sessionpool list -g MyResourceGroup
"""

# Session Commands
helps['containerapp session'] = """
    type: group
    short-summary: Commands to manage sessions.To learn more about individual commands under each subgroup run containerapp session [subgroup name] --help.
"""

helps['containerapp session stop'] = """
    type: command
    short-summary: Stop a custom container session.
    examples:
    - name: Stop a custom container session.
      text: |
          az containerapp session stop -n MySessionPool -g MyResourceGroup --identifier MySession
"""

# code interpreter commands
helps['containerapp session code-interpreter'] = """
    type: group
    short-summary: Commands to interact with and manage code interpreter sessions.
"""

helps['containerapp session code-interpreter execute'] = """
    type: command
    short-summary: Execute code in a code interpreter session.
    examples:
    - name: Execute a simple hello world.
      text: |
          az containerapp session code-interpreter execute -n MySessionPool -g MyResourceGroup --identifier MySession \\
              --code 'print("'"Hello world"'")' --timeout-in-seconds 30 --session-pool-location eastasia
"""

helps['containerapp session code-interpreter upload-file'] = """
    type: command
    short-summary: Upload a file to a code interpreter session .
    examples:
    - name: Upload a file to a session.
      text: |
          az containerapp session code-interpreter upload-file -n MySessionPool -g MyResourceGroup --identifier MySession \\
              --filepath example.txt --path my-directory
"""

helps['containerapp session code-interpreter show-file-content'] = """
    type: command
    short-summary: Show the content a file uploaded to a code interpreter session.
    examples:
    - name: Show content of file.
      text: az containerapp session code-interpreter show-file-content -n MySessionPool -g MyResourceGroup --identifier MySession \\
              --filename example.txt --path my-directory
"""

helps['containerapp session code-interpreter show-file-metadata'] = """
    type: command
    short-summary: Shows the meta-data content a file uploaded to a code interpreter session.
    examples:
    - name: Show the meta-data details of a file uploaded to a session.
      text: az containerapp session code-interpreter show-file-metadata -n MySessionPool -g MyResourceGroup --identifier MySession \\
              --filename example.txt --path my-directory
"""

helps['containerapp session code-interpreter delete-file'] = """
    type: command
    short-summary: Delete a file uploaded to a code interpreter session.
    examples:
    - name: Delete a file .
      text: az containerapp session code-interpreter delete-file -n MySessionPool -g MyResourceGroup --identifier MySession \\
              --filename example.txt --path my-directory
"""

helps['containerapp session code-interpreter list-files'] = """
    type: command
    short-summary: List files uploaded to a code interpreter session
    examples:
    - name: List files uploaded in a code-interpreter session.
      text: |
          az containerapp session code-interpreter list-files -n MySessionPool -g MyResourceGroup --identifier MySession --path my-directory
"""

helps['containerapp java'] = """
    type: group
    short-summary: Commands to manage Java workloads.
"""

# Java Logging logger Commands
helps['containerapp java logger'] = """
    type: group
    short-summary: Dynamically change log level for Java workloads.
"""

# Java Logging logger Commands
helps['containerapp java logger set'] = """
    type: command
    short-summary: Create or update logger for Java workloads.
    examples:
    - name: Create root logger with debug level.
      text: |
          az containerapp java logger set --logger-name root --logger-level debug -n my-containerapp -g MyResourceGroup
    - name: Update root logger with debug level.
      text: |
          az containerapp java logger set --logger-name root --logger-level info -n my-containerapp -g MyResourceGroup
"""

helps['containerapp java logger show'] = """
    type: command
    short-summary: Display logger setting for Java workloads.
    examples:
    - name: Display all logger settings for Java workloads.
      text: |
          az containerapp java logger show --all -n my-containerapp -g MyResourceGroup
    - name: Display specific logger with name for Java workloads.
      text: |
          az containerapp java logger show --logger-name root -n my-containerapp -g MyResourceGroup
"""

helps['containerapp java logger delete'] = """
    type: command
    short-summary: Delete logger for Java workloads.
    examples:
    - name: Delete all logger settings for Java workloads.
      text: |
          az containerapp java logger delete --all -n my-containerapp -g MyResourceGroup
    - name: Delete specific logger with name for Java workloads.
      text: |
          az containerapp java logger delete --logger-name root -n my-containerapp -g MyResourceGroup
"""

# DotNet Components Commands
helps['containerapp env dotnet-component'] = """
    type: group
    short-summary: Commands to manage DotNet components within the environment.
"""

helps['containerapp env dotnet-component list'] = """
    type: command
    short-summary: Command to list DotNet components within the environment.
    examples:
    - name: List all DotNet components within an environment.
      text: |
          az containerapp env dotnet-component list -g MyResourceGroup --environment MyEnvironment
"""

helps['containerapp env dotnet-component create'] = """
    type: command
    short-summary: Command to create DotNet component to enable Aspire Dashboard. Supported DotNet component type is Aspire Dashboard.
    examples:
    - name: Create a DotNet component to enable Aspire Dashboard.
      text: |
          az containerapp env dotnet-component create -g MyResourceGroup \\
              -n MyDotNetComponentName \\
              --environment MyEnvironment \\
              --type AspireDashboard
"""

helps['containerapp env dotnet-component delete'] = """
    type: command
    short-summary: Command to delete DotNet component to disable Aspire Dashboard.
    examples:
    - name: Delete DotNet component.
      text: |
          az containerapp env dotnet-component delete -g MyResourceGroup \\
              -n MyDotNetComponentName \\
              --environment MyEnvironment
"""

helps['containerapp env dotnet-component show'] = """
    type: command
    short-summary: Command to show DotNet component in environment.
    examples:
    - name: Show the details of an environment.
      text: |
          az containerapp env dotnet-component show -n MyDotNetComponentName --environment MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp registry set'] = """
    type: command
    short-summary: Add or update a container registry's details.
    examples:
    - name: Configure a container app to use a registry.
      text: |
          az containerapp registry set -n my-containerapp -g MyResourceGroup \\
              --server MyExistingContainerappRegistry.azurecr.io --username MyRegistryUsername --password MyRegistryPassword
    - name: Configure a container app to use environment system assigned managed identity to authenticate Azure container registry.
      text: |
          az containerapp registry set -n my-containerapp -g MyResourceGroup \\
              --server MyExistingContainerappRegistry.azurecr.io --identity system-environment
"""

helps['containerapp job registry set'] = """
    type: command
    short-summary: Add or update a container registry's details in a Container App Job.
    examples:
    - name: Configure a Container App Job to use a registry.
      text: |
          az containerapp job registry set -n my-containerapp-job -g MyResourceGroup \\
              --server MyContainerappJobRegistry.azurecr.io --username MyRegistryUsername --password MyRegistryPassword
    - name: Configure a Container App Job to use environment system assigned managed identity to authenticate Azure container registry.
      text: |
          az containerapp job registry set -n my-containerapp-job -g MyResourceGroup \\
              --server MyContainerappJobRegistry.azurecr.io --identity system-environment
"""

# Maintenance Config Commands
helps['containerapp env maintenance-config'] = """
    type: group
    short-summary: Commands to manage Planned Maintenance for Container Apps
"""

helps['containerapp env maintenance-config add'] = """
    type: command
    short-summary: Add Planned Maintenance to a Container App Environment
    examples:
    - name: Configure a Container App Environment to use a Planned Maintenance
      text: |
          az containerapp env maintenance-config add --environment myEnv -g MyResourceGroup \\
              --duration 10 --start-hour-utc 11 --weekday Sunday
"""

helps['containerapp env maintenance-config update'] = """
    type: command
    short-summary: Update Planned Maintenance in a Container App Environment
    examples:
    - name: Update the Planned Maintenance in a Container App Environment
      text: |
          az containerapp env maintenance-config update --environment myEnv -g MyResourceGroup \\
              --duration 8 --start-hour-utc 12 --weekday Thursday
"""

helps['containerapp env maintenance-config list'] = """
    type: command
    short-summary: List Planned Maintenance in a Container App Environment
    examples:
    - name: List Planned Maintenance
      text: |
          az containerapp env maintenance-config list --environment myEnv -g MyResourceGroup
"""

helps['containerapp env maintenance-config remove'] = """
    type: command
    short-summary: Remove Planned Maintenance in a Container App Environment
    examples:
    - name: Remove Planned Maintenance
      text: |
          az containerapp env maintenance-config remove --environment myEnv -g MyResourceGroup
"""

helps['containerapp debug'] = """
    type: command
    short-summary: Open an SSH-like interactive shell within a container app debug console.
    examples:
    - name: Debug by connecting to a container app's debug console by replica, revision and container
      text: |
          az containerapp debug -n MyContainerapp -g MyResourceGroup --revision MyRevision --replica MyReplica --container MyContainer
"""

helps['containerapp label-history'] = """
    type: group
    short-summary: Show the history for one or more labels on the Container App.
    examples:
    - name: Show Label History
      text: |
          az containerapp label-history show -n my-containerapp -g MyResourceGroup --label LabelName
"""

helps['containerapp label-history list'] = """
    type: command
    short-summary: List the history for all labels on the Container App.
    examples:
    - name: List All Label History
      text: |
          az containerapp label-history list -n my-containerapp -g MyResourceGroup
"""

helps['containerapp label-history show'] = """
    type: command
    short-summary: Show the history for a specific label on the Container App.
    examples:
    - name: Show Label History
      text: |
          az containerapp label-history show -n my-containerapp -g MyResourceGroup --label LabelName
"""

helps['containerapp env http-route-config'] = """
    type: group
    short-summary: Commands to manage environment level http routing.
"""

helps['containerapp env http-route-config list'] = """
    type: command
    short-summary: List the http route configs in the environment.
    examples:
    - name: List the http route configs in the environment.
      text: |
          az containerapp env http-route-config list -g MyResourceGroup -n MyEnvironment
"""

helps['containerapp env http-route-config create'] = """
    type: command
    short-summary: Create a new http route config.
    examples:
    - name: Create a new route from a yaml file.
      text: |
          az containerapp env http-route-config create -g MyResourceGroup -n MyEnvironment -r configname --yaml config.yaml
"""

helps['containerapp env http-route-config update'] = """
    type: command
    short-summary: Update a http route config.
    examples:
    - name: Update a route in the environment from a yaml file.
      text: |
          az containerapp env http-route-config update -g MyResourceGroup -n MyEnvironment -r configname --yaml config.yaml
"""

helps['containerapp env http-route-config show'] = """
    type: command
    short-summary: Show a http route config.
    examples:
    - name: Show a route in the environment.
      text: |
          az containerapp env http-route-config show -g MyResourceGroup -n MyEnvironment -r configname
"""

helps['containerapp env http-route-config delete'] = """
    type: command
    short-summary: Delete a http route config.
    examples:
    - name: Delete a route from the environment.
      text: |
          az containerapp env http-route-config delete -g MyResourceGroup -n MyEnvironment -r configname
"""

helps['containerapp env premium-ingress show'] = """
    type: command
    short-summary: Show the premium ingress settings for the environment.
    examples:
    - name: Show the premium ingress settings for the environment.
      text: |
          az containerapp env premium-ingress show -g MyResourceGroup -n MyEnvironment
"""

helps['containerapp env premium-ingress'] = """
    type: group
    short-summary: Configure premium ingress settings for the environment.
    long-summary: |
        Premium ingress settings apply to all applications in the environment. They allow moving the ingress instances to a workload profile and scaling them beyond the system defaults to enable high traffic workloads. Other settings include request idle timeouts, header count limits, and the termination grace period.
    examples:
    - name: Enable premium ingress for the environment.
      text: |
          az containerapp env premium-ingress add -g MyResourceGroup -n MyEnvironment -w WorkloadProfileName
"""

helps['containerapp env premium-ingress add'] = """
    type: command
    short-summary: Enable the premium ingress settings for the environment.
    long-summary: |
        Unspecified optional parameters will be cleared from any existing configuration.
    examples:
    - name: Add the premium ingress settings for the environment.
      text: |
          az containerapp env premium-ingress add -g MyResourceGroup -n MyEnvironment -w WorkloadProfileName
"""

helps['containerapp env premium-ingress update'] = """
    type: command
    short-summary: Update the premium ingress settings for the environment.
    examples:
    - name: Update the workload profile used for premium ingress.
      text: |
          az containerapp env premium-ingress update -g MyResourceGroup -n MyEnvironment -w WorkloadProfileName
"""

helps['containerapp env premium-ingress remove'] = """
    type: command
    short-summary: Remove the ingress settings and restores the system to default values.
    examples:
    - name: Reset the ingress settings for the environment to its default values
      text: |
          az containerapp env premium-ingress remove -g MyResourceGroup -n MyEnvironment
"""
