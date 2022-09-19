# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['nginx deployment list'] = """
    type: command
    short-summary: "List all Nginx Deployments under the specified resource group; List all deployments under the specified subscription."
    examples:
      - name: Deployments_ListByResourceGroup
        text: |-
               az nginx deployment list --resource-group myResourceGroup
      - name: Deployments_List
        text: |-
               az nginx deployment list
"""

helps['nginx deployment show'] = """
    type: command
    short-summary: "Get the properties of a specific Nginx Deployment."
    examples:
      - name: Deployment_Get
        text: |-
               az nginx deployment show --name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment create'] = """
    type: command
    short-summary: "Create an Nginx resource."
    parameters:
      - name: --sku
        short-summary: "The billing information for the resource (https://docs.nginx.com/nginx-for-azure/billing/overview/)"
        long-summary: |
            Usage: --sku name=XXX

      - name: --network-profile
        short-summary: "The IP address details"
        long-summary: |
            Usage: --network-profile front-end-ip-configuration="{public-ip-addresses:[{id:/subscriptions/mySubscriptionId/resourceGroups/myResourceGroup/providers/Microsoft.Network/publicIPAddresses/myPublicIP}]}" network-interface-configuration="{subnet-id:/subscriptions/mySubscriptionId/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet}"

            front-end-ip-configuration: IP information, public or private IP addresses.
            network-interface-configuration: Subnet information. This subnet should be delegated to NGINX.NGINXPLUS/nginxDeployments
    examples:
      - name: Deployment_Create_With_PublicIP
        text: |-
               az nginx deployment create --name myDeployment --resource-group myResourceGroup --location eastus2 --sku name="preview_Monthly_gmz7xq9ge3py" --network-profile front-end-ip-configuration="{public-ip-addresses:[{id:/subscriptions/mySubscription/resourceGroups/myResourceGroup/providers/Microsoft.Network/publicIPAddresses/myPublicIP}]}" network-interface-configuration="{subnet-id:/subscriptions/mySubscription/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet}"

      - name: Deployment_Create_With_PrivateIP
        text: |-
               az nginx deployment create --name myDeployment --resource-group myResourceGroup --location eastus2 --sku name="preview_Monthly_gmz7xq9ge3py" --network-profile front-end-ip-configuration="{private-ip-addresses:[{private-ip-allocation-method:Static,subnet-id:/subscriptions/mySubscription/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet,private-ip-address:10.0.0.1}]}" network-interface-configuration="{subnet-id:/subscriptions/mySubscription/resourceGroups/myResourceGroup/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet}"
"""

helps['nginx deployment update'] = """
    type: command
    short-summary: "Update an Nginx deployment."
    examples:
      - name: Deployment_Update
        text: |-
               az nginx deployment update --name myDeployment --resource-group myResourceGroup --location eastus2 --tags tag1="value1" tag2="value2" --enable-diagnostics true
"""

helps['nginx deployment delete'] = """
    type: command
    short-summary: "Delete an Nginx deployment."
    examples:
      - name: Deployment_Delete
        text: |-
               az nginx deployment delete --name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Nginx deployment is met.
    examples:
      - name: Pause executing next line of CLI script until the Nginx deployment is successfully created.
        text: |-
               az nginx deployment wait --name myDeployment --resource-group myResourceGroup --created
      - name: Pause executing next line of CLI script until the Nginx deployment is successfully updated.
        text: |-
               az nginx deployment wait --name myDeployment --resource-group myResourceGroup --updated
      - name: Pause executing next line of CLI script until the Nginx deployment is successfully deleted.
        text: |-
               az nginx deployment wait --name myDeployment --resource-group myResourceGroup --deleted
"""

helps['nginx deployment certificate list'] = """
    type: command
    short-summary: "List all certificates under the specified deployment and resource group"
    examples:
      - name: Certificate_ListByDeployment
        text: |-
               az nginx deployment certificate list --deployment-name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment certificate show'] = """
    type: command
    short-summary: "Get the properties of a specific Nginx certificate."
    examples:
      - name: Certificate_Get
        text: |-
               az nginx deployment certificate show --certificate-name myCertificate --deployment-name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment certificate create'] = """
    type: command
    short-summary: "Create a certificate for an Nginx deployment."
    parameters:
      - name: --deployment-name
        short-summary: "The Nginx deployment name"

      - name: --certificate-path
        short-summary: "This path must match one or more ssl_certificate_key directive file argument in your Nginx configuration. This path must be unique between certificates within the same deployment"

      - name: --key-path
        short-summary: "This path must match one or more ssl_certificate directive file argument in your Nginx configuration. This path must be unique between certificates within the same deployment"

      - name: --key-vault-secret-id
        short-summary: "The secret ID for your certificate from Azure Key Vault"
    examples:
      - name: Certificate_Create
        text: |-
               az nginx deployment certificate create --certificate-name myCertificate --deployment-name myDeployment --resource-group myResourceGroup --certificate-path /etc/nginx/test.cert --key-path /etc/nginx/test.key --key-vault-secret-id keyVaultSecretId
"""

helps['nginx deployment certificate update'] = """
    type: command
    short-summary: "Update an Nginx deployment certificate."
    examples:
      - name: Certificate_Update
        text: |-
               az nginx deployment certificate update --certificate-name myCertificate --deployment-name myDeployment --resource-group myResourceGroup --certificate-path /etc/nginx/testupdated.cert --key-path /etc/nginx/testupdated.key --key-vault-secret-id newKeyVaultSecretId
"""

helps['nginx deployment certificate delete'] = """
    type: command
    short-summary: "Delete an Nginx deployment certificate."
    examples:
      - name: Certificate_Delete
        text: |-
               az nginx deployment certificate delete --certificate-name myCertificate --deployment-name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment certificate wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the certificate is met.
    examples:
      - name: Pause executing next line of CLI script until the certificate is successfully created.
        text: |-
               az nginx deployment certificate wait --name myCertificate --deployment-name myDeployment --resource-group myResourceGroup --created
      - name: Pause executing next line of CLI script until the certificate is successfully updated.
        text: |-
               az nginx deployment certificate wait --name myCertificate --deployment-name myDeployment --resource-group myResourceGroup --updated
      - name: Pause executing next line of CLI script until the certificate is successfully deleted.
        text: |-
               az nginx deployment certificate wait --name myCertificate --deployment-name myDeployment --resource-group myResourceGroup --deleted
"""

helps['nginx deployment configuration list'] = """
    type: command
    short-summary: "List all configurations under the specified deployment and resource group"
    examples:
      - name: Configuration_ListByDeployment
        text: |-
               az nginx deployment configuration list --deployment-name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment configuration show'] = """
    type: command
    short-summary: "Get the properties of a specific Nginx configuration."
    examples:
      - name: Configuration_Get
        text: |-
               az nginx deployment configuration show --name default --deployment-name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment configuration create'] = """
    type: command
    short-summary: "Create a configuration for an Nginx deployment."
    parameters:
      - name: --deployment-name
        short-summary: "The Nginx deployment name"

      - name: --root-file
        short-summary: "This should align with your Nginx configuration structure"

      - name: --files
        short-summary: "This is an array of files required for the config set-up"
        long-summary: |
            One of the files virtual-path should match the root file. For a multi-file config set-up, the root file needs to have references to the other file(s) in an include directive.
            Usage: [{"content":"<Base64 content of config file>","virtual-path":"<path>"}].
    examples:
      - name: SingleConfiguration_Create
        text: |-
               az nginx deployment configuration create --name default --deployment-name myDeployment --resource-group myResourceGroup --root-file /etc/nginx/nginx.conf --files '[{"content":"aHR0cCB7CiAgICB1cHN0cmVhbSBhcHAgewogICAgICAgIHpvbmUgYXBwIDY0azsKICAgICAgICBsZWFzdF9jb25uOwogICAgICAgIHNlcnZlciAxMC4wLjEuNDo4MDAwOwogICAgfQoKICAgIHNlcnZlciB7CiAgICAgICAgbGlzdGVuIDgwOwogICAgICAgIHNlcnZlcl9uYW1lICouZXhhbXBsZS5jb207CgogICAgICAgIGxvY2F0aW9uIC8gewogICAgICAgICAgICBwcm94eV9zZXRfaGVhZGVyIEhvc3QgJGhvc3Q7CiAgICAgICAgICAgIHByb3h5X3NldF9oZWFkZXIgWC1SZWFsLUlQICRyZW1vdGVfYWRkcjsKICAgICAgICAgICAgcHJveHlfc2V0X2hlYWRlciBYLVByb3h5LUFwcCBhcHA7CiAgICAgICAgICAgIHByb3h5X3NldF9oZWFkZXIgR2l0aHViLVJ1bi1JZCAwMDAwMDA7CiAgICAgICAgICAgIHByb3h5X2J1ZmZlcmluZyBvbjsKICAgICAgICAgICAgcHJveHlfYnVmZmVyX3NpemUgNGs7CiAgICAgICAgICAgIHByb3h5X2J1ZmZlcnMgOCA4azsKICAgICAgICAgICAgcHJveHlfcmVhZF90aW1lb3V0IDYwczsKICAgICAgICAgICAgcHJveHlfcGFzcyBodHRwOi8vYXBwOwogICAgICAgICAgICBoZWFsdGhfY2hlY2s7CiAgICAgICAgfQogICAgICAgIAogICAgfQp9","virtual-path":"/etc/nginx/nginx.conf"}]'
      - name: MultiConfiguration_Create
        text: |-
               az nginx deployment configuration create --name default --deployment-name myDeployment --resource-group myResourceGroup --root-file /etc/nginx/nginx.conf --files '[{"content":"aHR0cCB7CiAgICB1cHN0cmVhbSBhcHAgewogICAgICAgIHpvbmUgYXBwIDY0azsKICAgICAgICBsZWFzdF9jb25uOwogICAgICAgIHNlcnZlciAxMC4wLjEuNDo4MDAwOwogICAgfQoKICAgIHNlcnZlciB7CiAgICAgICAgbGlzdGVuIDgwOwogICAgICAgIHNlcnZlcl9uYW1lICouZXhhbXBsZS5jb207CgogICAgICAgIGxvY2F0aW9uIC8gewogICAgICAgICAgICBpbmNsdWRlIC9ldGMvbmdpbngvY29uZi5kL3Byb3h5LmNvbmY7CiAgICAgICAgICAgIHByb3h5X3Bhc3MgaHR0cDovL2FwcDsKICAgICAgICAgICAgaGVhbHRoX2NoZWNrOwogICAgICAgIH0KICAgICAgICAKICAgIH0KfQ==","virtual-path":"/etc/nginx/nginx.conf"},{"content":"cHJveHlfc2V0X2hlYWRlciBIb3N0ICRob3N0Owpwcm94eV9zZXRfaGVhZGVyIFgtUmVhbC1JUCAkcmVtb3RlX2FkZHI7CnByb3h5X3NldF9oZWFkZXIgWC1Qcm94eS1BcHAgYXBwOwpwcm94eV9zZXRfaGVhZGVyIEdpdGh1Yi1SdW4tSWQgMDAwMDAwOwpwcm94eV9idWZmZXJpbmcgb247CnByb3h5X2J1ZmZlcl9zaXplIDRrOwpwcm94eV9idWZmZXJzIDggOGs7CnByb3h5X3JlYWRfdGltZW91dCA2MHM7","virtual-path":"/etc/nginx/conf.d/proxy.conf"}]'
"""

helps['nginx deployment configuration update'] = """
    type: command
    short-summary: "Update an Nginx configuration."
    examples:
      - name: Configuration_Update
        text: |-
               az nginx deployment configuration update --name default --deployment-name myDeployment --resource-group myResourceGroup --root-file /etc/nginx/nginx.conf --files '[{"content":"aHR0cCB7CiAgICB1cHN0cmVhbSBhcHAgewogICAgICAgIHpvbmUgYXBwIDY0azsKICAgICAgICBsZWFzdF9jb25uOwogICAgICAgIHNlcnZlciAxMC4wLjEuNDo4MDAwOwogICAgfQoKICAgIHNlcnZlciB7CiAgICAgICAgbGlzdGVuIDgwOwogICAgICAgIHNlcnZlcl9uYW1lICouZXhhbXBsZS5jb207CgogICAgICAgIGxvY2F0aW9uIC8gewogICAgICAgICAgICBwcm94eV9zZXRfaGVhZGVyIEhvc3QgJGhvc3Q7CiAgICAgICAgICAgIHByb3h5X3NldF9oZWFkZXIgWC1SZWFsLUlQICRyZW1vdGVfYWRkcjsKICAgICAgICAgICAgcHJveHlfc2V0X2hlYWRlciBYLVByb3h5LUFwcCBhcHA7CiAgICAgICAgICAgIHByb3h5X3NldF9oZWFkZXIgR2l0aHViLVJ1bi1JZCAwMDAwMDA7CiAgICAgICAgICAgIHByb3h5X2J1ZmZlcmluZyBvbjsKICAgICAgICAgICAgcHJveHlfYnVmZmVyX3NpemUgNGs7CiAgICAgICAgICAgIHByb3h5X2J1ZmZlcnMgOCA4azsKICAgICAgICAgICAgcHJveHlfcmVhZF90aW1lb3V0IDYwczsKICAgICAgICAgICAgcHJveHlfcGFzcyBodHRwOi8vYXBwOwogICAgICAgICAgICBoZWFsdGhfY2hlY2s7CiAgICAgICAgfQogICAgICAgIAogICAgfQp9","virtual-path":"/etc/nginx/nginx.conf"}]'
"""

helps['nginx deployment configuration delete'] = """
    type: command
    short-summary: "Delete an Nginx configuration."
    examples:
      - name: Configuration_Delete
        text: |-
               az nginx deployment configuration delete --name default --deployment-name myDeployment --resource-group myResourceGroup
"""

helps['nginx deployment configuration wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the configuration is met.
    examples:
      - name: Pause executing next line of CLI script until the configuration is successfully created.
        text: |-
               az nginx deployment configuration wait --name default --deployment-name myDeployment --resource-group myResourceGroup --created
      - name: Pause executing next line of CLI script until the configuration is successfully updated.
        text: |-
               az nginx deployment configuration wait --name default --deployment-name myDeployment --resource-group myResourceGroup --updated
      - name: Pause executing next line of CLI script until the configuration is successfully deleted.
        text: |-
               az nginx deployment configuration wait --name default --deployment-name myDeployment --resource-group myResourceGroup --deleted
"""
