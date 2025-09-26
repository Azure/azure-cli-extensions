.. :changelog:

Release History
===============
8.2.0
++++++
* All fields with swagger setting `format=arm-id` are now nullable via the CLI.

8.1.1
++++++
* Removing the `externalnetwork update-bfd-administrative-state` command as it is not supported by the API.

8.1.0
++++++
* Adding breaking change notices for the following items that will be included in the upcoming 2025-07-15-stable CLI (9.0.x).
* [Breaking Change] Command group `fabric identity` will be removed as current az-cli-core does not support GET-PATCH. This includes the `assign`, `remove`, `show` sub-commands.
* [Breaking Change] Parameter `route-prefix-limit` will be removed from `l3domain create` and `l3domain update` commands.
* [Breaking Change] Parameter `version` on `device upgrade` command will become required.

8.0.0
++++++
* Updating version 8-beta to stable cli version 8.x for 2024-06-15-preview.
* Adds missing `--resource-name` parameter to many commands to keep better consistency.
* This version requires a minimum of 2.75.0 Azure core CLI. See install instructions: https://github.com/MicrosoftDocs/azure-docs-cli/blob/main/docs-ref-conceptual/Latest-version/install-azure-cli.md

8.0.0b7
++++++
* Added missing examples and updated verbiage on existing examples

8.0.0b6
++++++
* Enables the 'device refresh-configuration' command that was previously disabled/removed.
* Renames the 'network-device-name' parameter on 'device refresh-configuration' and 'device reboot' operations to 'resource-name' for better overall consistency.

8.0.0b5
++++++
* Fixes 'taprule create' command as the API cannot support float values for 'polling-interval-in-seconds' option, i.e. - '30.0'.
* Fixes the response object model for validate-configuration operations that cause response of the operation to not show any output.
* az core cli updated to version 2.70, aaz_dev updated to version 4.2.0, and azdev to version 0.2.4.

8.0.0b4
++++++
* Fixes 'device run-ro' command for missing fields in the response.

8.0.0b3
++++++
* Adding custom output formatting for 'device' run-ro command

8.0.0b2
++++++
* Making the Network Monitor resource available through the CLI.
* Within the the IPv4/IPv6 PrefixLimitPatchProperties structure for External and Internal Networks, renamed the 'softLimit' property to 'threshold'.

8.0.0b1
++++++
* New preview CLI version for latest api 2024-06-15-preview.
* az core cli updated to version 2.67, aaz_dev updated to version 3.2.0, and azdev to version 0.1.94.
* New `fabric identity` commands introduced: `fabric identity assign`, `fabric identity remove`, `fabric identity show`.
* Expose the 'update' command for the 'interface' resource that was previously removed in post generate script.

7.1.0
++++++
* Bug fix: expose the 'update-admin-state' command for the 'interface' resource that was removed from the CLI by invalid post-processing logic.

7.0.0
++++++
* This version requires a minimum of 2.66 Azure core CLI. See release notes for more details: https://github.com/MicrosoftDocs/azure-docs-cli/blob/main/docs-ref-conceptual/release-notes-azure-cli.md
* This version upgrades the internal generation tool aaz-dev-tools to 3.1.0. Refer to the release notes for more details: https://github.com/Azure/aaz-dev-tools/releases/tag/v3.1.0.

6.4.0
++++++
* Updating release version to be in sync with 6.4 RP release

6.2.0
++++++
* Updating release version

6.1.0
++++++
* Added device update-admin-state support

6.0.0
++++++
* Added device run rw support

5.2.4
++++++
* Added device run ro support
* Allowed null values for acl ids in nni

5.2.1
++++++
* Reverted changes to 5.0.0 version

5.2.0
++++++
* Added device run ro support
* Allowed null values for acl ids in nni

5.0.0
++++++
* Added Resync functionality for Network taps and Network tap rules
* Added support External Network to patch NNI

4.2.0
++++++
* Added support for upgrading Device and Network Fabric resource.
* Added support for validate configuration in Network Fabric resources.

4.1.1
++++++
* Revered the attribute renaming changes done in previous commit.

4.1.0
++++++
* Supported for fabric commit-configuration functionality
* PATCH support added for
*	- Route Policy,
*	- Access Control List,
*	- IPCommunity,
*	- IPExtendedCommunity,
*	- IPPrefix,
*	- L2 Isolation Domain,
*	- L3 Isolation Domain,
*	- Internal Network,
*	- External Network

3.2.0
++++++
* Supported ACL
* Added new parameter "defaultAction" in RoutePolicies and ACL
* Supported NeighborGroup
* Supported Tap
* Supported TapRule

3.1.0
++++++
* GA Initial release.

1.0.0b2
++++++
* Updated latest swagger specification.
* Removed commands which are not required.

1.0.0b1
++++++
* Initial release.