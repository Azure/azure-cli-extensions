# Azure CLI Planetary Computer Extension #
This is an extension to Azure CLI to manage Planetary Computer GeoCatalog resources.

The extension targets `Microsoft.Orbital` API version `2026-10-01`.

## How to use ##

### Install the extension ###
```bash
az extension add --name planetarycomputer
```

### Commands ###

#### GeoCatalog Management ####
```bash
# Create a GeoCatalog
az planetarycomputer geocatalog create -g MyResourceGroup -n MyCatalog -l eastus

# Show a GeoCatalog
az planetarycomputer geocatalog show -g MyResourceGroup -n MyCatalog

# List GeoCatalogs in a resource group
az planetarycomputer geocatalog list -g MyResourceGroup

# List all GeoCatalogs in a subscription
az planetarycomputer geocatalog list

# Update tags on a GeoCatalog
az planetarycomputer geocatalog update -g MyResourceGroup -n MyCatalog --tags env=prod

# Delete a GeoCatalog
az planetarycomputer geocatalog delete -g MyResourceGroup -n MyCatalog

# Wait for a GeoCatalog to reach a desired state
az planetarycomputer geocatalog wait -g MyResourceGroup -n MyCatalog --created
```

#### GeoCatalog Identity Management ####
```bash
# Assign a user-assigned managed identity
az planetarycomputer geocatalog identity assign -g MyResourceGroup -n MyCatalog --user-assigned /subscriptions/<subscription-id>/resourceGroups/MyResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity

# Show identity information
az planetarycomputer geocatalog identity show -g MyResourceGroup -n MyCatalog

# Remove a user-assigned managed identity
az planetarycomputer geocatalog identity remove -g MyResourceGroup -n MyCatalog --user-assigned /subscriptions/<subscription-id>/resourceGroups/MyResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity
```

#### GeoCatalog Network Access ####
```bash
# Disable public network access
az planetarycomputer geocatalog update -g MyResourceGroup -n MyCatalog --public-network-access Disabled

# List private endpoint connections
az planetarycomputer geocatalog private-endpoint-connection list -g MyResourceGroup --catalog-name MyCatalog

# Show a private endpoint connection
az planetarycomputer geocatalog private-endpoint-connection show -g MyResourceGroup --catalog-name MyCatalog -n MyConnection

# Update a private endpoint connection (the longer option remains supported)
az planetarycomputer geocatalog private-endpoint-connection update -g MyResourceGroup --catalog-name MyCatalog -n MyConnection --connection-state description=Approved

# List private link resources
az planetarycomputer geocatalog private-link-resource list -g MyResourceGroup --catalog-name MyCatalog
```

The stable contract supports Basic catalogs and user-assigned managed identities.
Premium configuration and system-assigned identity options are not exposed.
Lifecycle `state` and `stoppedSinceUtc` are read-only response properties.

Generation uses public specification commit
`3d41865727e08555114cd851cb6145987474f9d8`.
The AAZ workspace hides the generator-synthesized system-assigned identity
arguments because the service supports only user-assigned identities.

## Development smoke test ##

From the repository root in the configured `azdev` environment:

```bash
python -m unittest discover -s src/planetarycomputer/azext_planetarycomputer/tests/latest -p test_stable_api.py -v
```

This offline smoke test invokes the CLI with mocked HTTP responses; it does not
validate the live service. The existing scenario recordings still target
`2026-04-15` and need refreshing before the full playback suite and pre-push gate
can pass.

## GeoCatalog integration tests ##

Use an authorized, disposable Basic GeoCatalog with `TenantReuse` domain scope
and a user-assigned managed identity in the same subscription. These scenarios
modify the catalog's tags and identity, and create three additional temporary
catalogs in separate resource groups. Resource preparers remove those groups even
when an assertion fails; the supplied catalog and identity remain caller-owned.
Do not run other tests that modify the supplied catalog concurrently.

```bash
export PLANETARYCOMPUTER_TEST_CATALOG_ID="/subscriptions/<subscription>/resourceGroups/<group>/providers/Microsoft.Orbital/geoCatalogs/<catalog>"
export PLANETARYCOMPUTER_TEST_IDENTITY_ID="/subscriptions/<subscription>/resourceGroups/<group>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<identity>"
export PLANETARYCOMPUTER_TEST_LOCATION="eastus2euap"
AZURE_TEST_RUN_LIVE=true python -m unittest discover -s src/planetarycomputer/azext_planetarycomputer/tests/latest -p test_planetarycomputer.py -v
```

The test patches only its process-local ARM endpoint, defaulting to
`https://eastus2euap.management.azure.com/`; set
`PLANETARYCOMPUTER_TEST_ARM_ENDPOINT` to override it for live runs. The
authentication audience is unchanged. Recordings sanitize the supplied resource
names and subscription IDs and match request bodies as well as URLs.

For playback, unset `AZURE_TEST_RUN_LIVE` and run the same command without the
assignment. Playback uses sanitized fixtures and does not require the fixture
environment variables.

## Private-link integration test ##

The private-link lifecycle scenario uses an existing GeoCatalog and subnet. It
creates a separate temporary network private endpoint, exercises the generated
connection create/show/update/list/wait/delete commands, and removes only its own
endpoint. It does not change catalog identity, tags, or public network access.

Until the API rollout reaches global Azure Resource Manager routing, this test
uses `https://eastus2euap.management.azure.com/` on its isolated CLI context and
restores the original endpoint afterward.

To record against an authorized test catalog and subnet:

```bash
export PLANETARYCOMPUTER_TEST_CATALOG_ID="/subscriptions/<catalog-subscription>/resourceGroups/<catalog-group>/providers/Microsoft.Orbital/geoCatalogs/<catalog>"
export PLANETARYCOMPUTER_TEST_SUBNET_ID="/subscriptions/<network-subscription>/resourceGroups/<network-group>/providers/Microsoft.Network/virtualNetworks/<vnet>/subnets/<subnet>"
AZURE_TEST_RUN_LIVE=true python -m unittest discover -s src/planetarycomputer/azext_planetarycomputer/tests/latest -p test_private_link.py -v
```

The recording currently uses `broken` in `canary-test` and the existing
`internal-testing` private-endpoint subnet. If different fixtures are used for a
new recording, update the playback fixture defaults in the scenario to match the
sanitized recording.

To replay without contacting Azure:

```bash
unset AZURE_TEST_RUN_LIVE
python -m unittest discover -s src/planetarycomputer/azext_planetarycomputer/tests/latest -p test_private_link.py -v
```

The existing general GeoCatalog scenario recordings still require a separate
refresh; this focused private-link test does not make the entire suite pass.