# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['webpubsub'] = """
    type: group
    short-summary: Commands to manage Webpubsub.
"""

helps['webpubsub key'] = """
    type: group
    short-summary: Commands to manage Webpubsub keys.
"""

helps['webpubsub hub'] = """
    type: group
    short-summary: Commands to manage Webpubsub hub settings.
"""

helps['webpubsub network-rule'] = """
    type: group
    short-summary: Commands to manage Webpubsub network rules.
"""

helps['webpubsub client'] = """
    type: group
    short-summary: Commands to manage client connections.
"""

helps['webpubsub service'] = """
    type: group
    short-summary: Commands to manage Webpubsub service.
"""

helps['webpubsub service connection'] = """
    type: group
    short-summary: Commands to manage Webpubsub service connections.
"""

helps['webpubsub service user'] = """
    type: group
    short-summary: Commands to manage Webpubsub service users.
"""

helps['webpubsub service group'] = """
    type: group
    short-summary: Commands to manage Webpubsub service groups.
"""

helps['webpubsub service permission'] = """
    type: group
    short-summary: Commands to manage Webpubsub service permissions.
"""

helps['webpubsub replica'] = """
    type: group
    short-summary: Manage replica settings.
"""

helps['webpubsub network-rule ip-rule'] = """
    type: group
    short-summary: Manage WebPubSub Service IP rules.
"""

helps['webpubsub custom-certificate'] = """
    type: group
    short-summary: Manage WebPubSub custom certificates.
"""

helps['webpubsub custom-domain'] = """
    type: group
    short-summary: Manage custom domain settings.
"""

helps['webpubsub identity'] = """
    type: group
    short-summary: Manage managed identity settings.
"""

helps['webpubsub create'] = """
    type: command
    short-summary: Create a Webpubsub.
    examples:
      - name: Create a WebPubSub Service with Standard SKU and unit 2.
        text: >
          az webpubsub create -n MyWebPubSub -g MyResourceGroup --sku Standard_S1 --unit-count 2
      - name: Create a Web PubSub for Socket.IO with Premium SKU and unit 1.
        text: >
          az webpubsub create -n MyWebPubSub -g MyResourceGroup --sku Premium_P1 --unit-count 1 --kind SocketIO
      - name: Create a Web PubSub for Socket.IO in Serverless mode with Premium SKU and unit 1
        text: >
          az webpubsub create -n MyWebPubSub -g MyResourceGroup --sku Premium_P1 --unit-count 1 --kind SocketIO --service-mode Serverless
"""

helps['webpubsub list'] = """
    type: command
    short-summary: List Webpubsub.
"""

helps['webpubsub delete'] = """
    type: command
    short-summary: Delete a Webpubsub.
"""

helps['webpubsub show'] = """
    type: command
    short-summary: Show details of a Webpubsub.
"""

helps['webpubsub update'] = """
    type: command
    short-summary: Update a Webpubsub.
    examples:
      - name: Update a WebPubSub Service to unit 10.
        text: >
          az webpubsub update -n MyWebPubSub -g MyResourceGroup --sku Standard_S1 --unit-count 10
      - name: Update a Web PubSub for Socket.IO to Serverless mode.
        text: >
          az webpubsub update -n MyWebPubSub -g MyResourceGroup --service-mode Serverless
      - name: Enable or disable client certificate authentication for a WebPubSub Service
        text: >
          az webpubsub update -n MyWebPubSub -g MyResourceGroup --client-cert-enabled true
      - name: Enable or disable local auth for a WebPubSub Service
        text: >
          az webpubsub update -n MyWebPubSub -g MyResourceGroup --disable-local-auth true
      - name: Enable or disable region endpoint for a WebPubSub Service
        text: >
          az webpubsub update -n MyWebPubSub -g MyResourceGroup --region-endpoint-enabled true
"""

helps['webpubsub start'] = """
    type: command
    short-summary: Start a Webpubsub.
"""

helps['webpubsub stop'] = """
    type: command
    short-summary: Stop a Webpubsub.
"""

helps['webpubsub restart'] = """
    type: command
    short-summary: Restart a Webpubsub.
"""

helps['webpubsub list-usage'] = """
    type: command
    short-summary: List resource usage quotas by location.
"""

helps['webpubsub list-skus'] = """
    type: command
    short-summary: List all available skus of the resource.
"""

helps['webpubsub key show'] = """
    type: command
    short-summary: Show connetion strings and keys for a WebPubSub Service
    examples:
      - name: Get the primary key for a WebPubSub Service.
        text: >
          az webpubsub key show -n MyWebPubSub -g MyResourceGroup --query primaryKey -o tsv
"""

helps['webpubsub key regenerate'] = """
    type: command
    short-summary: Regenerate keys for a WebPubSub Service
    examples:
      - name: Regenerate the primary key for a WebPubSub Service.
        text: >
          az webpubsub key regenerate -n MyWebPubSub -g MyResourceGroup --key-type primary --query primaryKey -o tsv
"""

helps['webpubsub network-rule show'] = """
    type: command
    short-summary: Get the Network access control of WebPubSub Service.
"""

helps['webpubsub network-rule update'] = """
    type: command
    short-summary: Update the Network access control of WebPubSub Service.
    examples:
      - name: Set allowing RESTAPI only for public network.
        text: >
            az webpubsub network-rule update --public-network -n MyWebPubSub -g MyResourceGroup --allow RESTAPI
      - name: Set allowing client connection and server connection for a private endpoint connection
        text: >
            az webpubsub network-rule update --connection-name MyPrivateEndpointConnection -n MyWebPubSub -g MyResourceGroup --allow ClientConnection ServerConnection
      - name: Set denying client connection for both public network and private endpoint connections
        text: >
            az webpubsub network-rule update --public-network --connection-name MyPrivateEndpointConnection1 MyPrivateEndpointConnection2 -n MyWebPubSub -g MyResourceGroup --deny ClientConnection
"""

helps['webpubsub network-rule ip-rule add'] = """
    type: command
    short-summary: Add IP rule to WebPubSub Service.
    examples:
      - name: Add IP rule
        text: >
            az webpubsub network-rule ip-rule add -n MyWebPubSub -g MyResourceGroup --ip-rule value="10.0.0.24" action="Allow" --ip-rule value="192.168.0.0/24" action="Deny"
"""

helps['webpubsub network-rule ip-rule remove'] = """
    type: command
    short-summary: Remove IP rule from WebPubSub Service.
    examples:
      - name: Remove IP rule
        text: >
            az webpubsub network-rule ip-rule remove -n MyWebPubSub -g MyResourceGroup --ip-rule value="10.0.0.24" action="Allow" --ip-rule value="192.168.0.0/24" action="Deny"
"""

helps['webpubsub hub show'] = """
    type: command
    short-summary: Show hub settings for WebPubSub Service.
"""

helps['webpubsub hub list'] = """
    type: command
    short-summary: List all hub settings for WebPubSub Service.
"""

helps['webpubsub hub delete'] = """
    type: command
    short-summary: Delete hub settings for WebPubSub Service.
"""

helps['webpubsub hub create'] = """
    type: command
    short-summary: Create hub settings for WebPubSub Service or Web PubSub for Socket.IO in Serverless Mode.
    examples:
      - name: Create a hub setting with two event handler settings
        text: >
            az webpubsub hub create -n MyWebPubSub -g MyResourceGroup --hub-name MyHub --event-handler url-template="http://host.com" user-event-pattern="MyEvent" --event-handler url-template="http://host2.com" system-event="connected" system-event="disconnected" auth-type="ManagedIdentity" auth-resource="uri://myUri"
      - name: Create a hub setting with anonymous connection allowed
        text: >
            az webpubsub hub create -n MyWebPubSub -g MyResourceGroup --hub-name MyHub --allow-anonymous true
"""

helps['webpubsub hub update'] = """
    type: command
    short-summary: Update hub settings for WebPubSub Service or Web PubSub for Socket.IO in Serverless Mode.
    examples:
      - name: Update event handler settings of a hub
        text: >
            az webpubsub hub update -n MyWebPubSub -g MyResourceGroup --hub-name MyHub --event-handler url-template="http://host.com" user-event-pattern="MyEvent" --event-handler url-template="http://host2.com" system-event="connected" system-event="disconnected" auth-type="ManagedIdentity" auth-resource="uri://myUri"
      - name: Update to allow anonymous connection
        text: >
            az webpubsub hub update -n MyWebPubSub -g MyResourceGroup --hub-name MyHub --allow-anonymous true
      - name: Update to web socket keep alive interval in seconds (default is 20 seconds, minimum is 1, maximum is 120)
        text: >
            az webpubsub hub update -n MyWebPubSub -g MyResourceGroup --hub-name MyHub --websocket-keepalive 30
"""

helps['webpubsub client start'] = """
    type: command
    short-summary: Start a interactive client connection.
"""

helps['webpubsub service broadcast'] = """
    type: command
    short-summary: Broadcast messages to hub. Error throws if operation fails.
    examples:
      - name: Send a message to hub
        text: >
            az webpubsub service broadcast -n MyWebPubSub -g MyResourceGroup --hub-name MyHub --payload MyPayload
"""

helps['webpubsub service connection exist'] = """
    type: command
    short-summary: Check whether client connection exists.
"""

helps['webpubsub service connection close'] = """
    type: command
    short-summary: Close a specific client connection. Error throws if operation fails.
"""

helps['webpubsub service connection send'] = """
    type: command
    short-summary: Send a message to connection. Error throws if operation fails.
"""

helps['webpubsub service group add-connection'] = """
    type: command
    short-summary: Add a connection to group. Error throws if operation fails.
"""

helps['webpubsub service group remove-connection'] = """
    type: command
    short-summary: Remove a connection from group. Error throws if operation fails.
"""

helps['webpubsub service group add-user'] = """
    type: command
    short-summary: Add a user to group. Error throws if operation fails.
"""

helps['webpubsub service group remove-user'] = """
    type: command
    short-summary: Remove a user from group. Error throws if operation fails.
"""

helps['webpubsub service group send'] = """
    type: command
    short-summary: Send a message to group. Error throws if operation fails.
"""

helps['webpubsub service user send'] = """
    type: command
    short-summary: Send a message to user. Error throws if operation fails.
"""

helps['webpubsub service user exist'] = """
    type: command
    short-summary: Check if there are any client connections connected for the given user
"""

helps['webpubsub service permission grant'] = """
    type: command
    short-summary: Grant a group permission to the connection. Error throws if operation fails.
"""

helps['webpubsub service permission revoke'] = """
    type: command
    short-summary: Revoke a group permission from the connection. Error throws if operation fails.
"""

helps['webpubsub service permission check'] = """
    type: command
    short-summary: Check if a connection has permission to the specified group.
"""

helps['webpubsub replica show'] = """
type: command
short-summary: Show the details of a replica
examples:
  - name: Get the detail of a replica
    text: >
        az webpubsub replica show --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub replica start'] = """
type: command
short-summary: Start a replica of WebPubSub Service.
examples:
  - name: Start a replica
    text: >
        az webpubsub replica start --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub replica stop'] = """
type: command
short-summary: Stop a replica of WebPubSub Service.
examples:
  - name: Stop a replica
    text: >
        az webpubsub replica stop --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub replica restart'] = """
type: command
short-summary: Restart a replica of WebPubSub Service.
examples:
  - name: Restart a replica
    text: >
        az webpubsub replica restart --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup
"""


helps['webpubsub replica delete'] = """
type: command
short-summary: Delete a replica of WebPubSub Service.
examples:
  - name: Delete a replica
    text: >
        az webpubsub replica delete --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub replica list'] = """
type: command
short-summary: List replicas of Webpubsub Service.
examples:
  - name: Get the detail of a replica
    text: >
        az webpubsub replica list --name MyWebPubSub -g MyResourceGroup -o table
"""

helps['webpubsub replica create'] = """
type: command
short-summary: Create a replica of Webpubsub Service.
examples:
  - name: Get the detail of a replica
    text: >
        az webpubsub replica create --sku Premium_P1 -l eastus --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub replica update'] = """
type: command
short-summary: Update a replica of Webpubsub Service.
examples:
  - name: Enable or disable region endpoint for the replica of WebPubSub Service
    text: >
        az webpubsub replica update --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup --region-endpoint-enabled true
  - name: Update the unit count of the replica of WebPubSub Service
    text: >
        az webpubsub replica update --replica-name MyReplica --name MyWebPubSub -g MyResourceGroup --unit-count 2
"""

helps['webpubsub custom-certificate list'] = """
type: command
short-summary: List custom certificates of WebPubSub Service.
examples:
  - name: List custom certificates
    text: >
        az webpubsub custom-certificate list --webpubsub-name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub custom-certificate show'] = """
type: command
short-summary: Show the detail of a custom certificate of WebPubSub Service.
examples:
  - name: Show custom certificate
    text: >
        az webpubsub custom-certificate show --webpubsub-name MyWebPubSub -g MyResourceGroup --certificate-name MyCertificate
"""

helps['webpubsub custom-certificate create'] = """
type: command
short-summary: Create a custom certificate of WebPubSub Service.
examples:
  - name: Create a custom certificate
    text: >
        az webpubsub custom-certificate create --webpubsub-name MyWebPubSub -g MyResourceGroup --certificate-name MyCertificate --key-vault-base-uri https://myvault.vault.azure.net/ --key-vault-secret-name MySecret --key-vault-secret-version 8d35338681be4cf09b97e899cb7179b8
"""

helps['webpubsub custom-certificate delete'] = """
type: command
short-summary: Delete a custom certificate of WebPubSub Service.
examples:
  - name: Delete a custom certificate
    text: >
        az webpubsub custom-certificate delete --webpubsub-name MyWebPubSub -g MyResourceGroup --certificate-name MyCertificate
"""

helps['webpubsub custom-domain create'] = """
type: command
short-summary: Create a custom domain of WebPubSub Service.
examples:
  - name: Create a custom domain
    text: >
        az webpubsub custom-domain create --webpubsub-name MyWebPubSub -g MyResourceGroup --name MyDomain --domain-name MyDomain.com --certificate-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyResourceGroup/providers/Microsoft.Web/certificates/MyCertificate
"""

helps['webpubsub custom-domain delete'] = """
type: command
short-summary: Delete a custom domain of WebPubSub Service.
examples:
  - name: Delete a custom domain
    text: >
        az webpubsub custom-domain delete --webpubsub-name MyWebPubSub -g MyResourceGroup --name MyDomain
"""

helps['webpubsub custom-domain list'] = """
type: command
short-summary: List custom domains of WebPubSub Service.
examples:
  - name: List custom domains
    text: >
        az webpubsub custom-domain list --webpubsub-name MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub custom-domain show'] = """
type: command
short-summary: Show the detail of a custom domain of WebPubSub Service.
examples:
  - name: Show custom domain
    text: >
        az webpubsub custom-domain show --webpubsub-name MyWebPubSub -g MyResourceGroup --name MyDomain
"""

helps['webpubsub identity assign'] = """
type: command
short-summary: Assign managed identity for WebPubSub Service.
examples:
  - name: Assign system assigned identity.
    text: >
        az webpubsub identity assign --identity [system] -n MyWebPubSub -g MyResourceGroup
  - name: Assign user assigned identity.
    text: >
        az webpubsub identity assign --identity MyManagedIdentityId -n MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub identity remove'] = """
type: command
short-summary: Remove managed identity for WebPubSub Service.
examples:
  - name: Remove managed identity.
    text: >
        az webpubsub identity remove -n MyWebPubSub -g MyResourceGroup
"""

helps['webpubsub identity show'] = """
type: command
short-summary: Show managed identity for WebPubSub Service.
examples:
  - name: Show managed identity.
    text: >
        az webpubsub identity show -n MyWebPubSub -g MyResourceGroup
"""
