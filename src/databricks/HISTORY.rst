.. :changelog:

Release History
===============
0.10.0

+++++
* Upgrade API version from 2022-04-01-preview to 2022-10-01-preview and 2023-02-01
* az databricks workspace update: add --sku to change the sku tier name
* az databricks access-connector create/update: add --identities to set the user assigned identities associated with the resource.

0.9.0
+++++
* Upgrade API version from 2021-04-01-preview to 2022-04-01-preview
* az databricks access-connector: Support create/update/list/show/delete access connector.
* az databricks workspace private-endpoint-connection: Support create/update/list/show/delete private endpoint connection.
* az databricks workspace private-link-resource: Support list/show private link resource.
* az databricks workspace outbound-endpoint: Support list outbound endpoint.

0.8.0
+++++
* az databricks workspace create: Add --public-network-access to allow creating workspace with network access from public internet
* az databricks workspace create: Add --required-nsg-rules to allow creating workspace with nsg rule for internal

0.7.3
+++++
* Migrate databricks to track2 SDK

0.7.2
+++++
* az databricks workspace create: Add --enable-no-public-ip to allow creating workspace with no public ip

0.7.1
+++++
* az databricks workspace create: Fix issue when creating a workspace with --tags

0.7.0
+++++
* GA databricks extension

0.6.0
+++++
* GA CMK feature
* Make --key-version optional when updating CMK

0.5.0
+++++
* az databricks workspace create: add --require-infrastructure-encryption to enable double encryption

0.4.0
+++++
* az databricks workspace vnet-peering: support vnet peering operations for workspaces

0.3.0
+++++
* az databricks workspace create/update: add customer-managed key feature

0.2.0
+++++
* Rename --virtual-network to --vnet
* Rename --public-subnet-name to --public-subnet
* Rename --private-subnet-name to --private-subnet
* Remove --aml-workspace-id
* Remove --enable-no-public-ip
* Remove --load-balancer-backend-pool-name
* Remove --load-balancer
* Remove --relay-namespace-name
* Remove --storage-account-name
* Remove --storage-account-sku
* Remove --vnet-address-prefix

0.1.0
++++++
* Initial release.
