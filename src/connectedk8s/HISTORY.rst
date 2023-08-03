.. :changelog:

Release History
===============

1.4.0
++++++
* Added support for reading ARM metadata 2022-09-01.

1.3.20
++++++

* Bug fix in parsing logs for outbound connectivity check for troubleshoot command

1.3.19
++++++
* Adding outbound network connectivity check for Cluster Connect (OBO endpoint)

1.3.18
++++++
* Cleaning up stale CRDs if present during onboarding (even in absence of azure-arc release)
* Adding retries in Helm client download
* Added some failures to be classified as userfaults

1.3.17
++++++
* Added a spinner which runs while ARM resource is being provisioned
* Added additional logging to indicate which step is running

1.3.16
++++++
* Adding force delete in connect command in case of stale resources present during onboarding
* Bug fixes in diagnoser
* Pushing armd id and location to telemetry
* Adding test for connectedk8s proxy command

1.3.15
++++++
* Diagnoser Enhancements - storing metadata and KAP CR snapshots , azure-arc helm values , azure-arc ns secret list
* Removing circular imports of 1. custom from precheckutils and 2.(precheckutils and troubleshootutils) from utils
* Adding back heuristics detection in connect command

1.3.14
++++++
* Changing telemetry push interval to 1 hr
* Adding two new supported infra values - Windows 10 IoT Enterprise, LTSCWindows 10 Enterprise LTSC
* Saving cluster diagnostic checks pod and job logs

1.3.13
++++++
* Bumping up the cluster diagnostic checks helm chart version - Nodeselector addition

1.3.12
++++++
* Added retries for helm chart pull and config DP POST call
* Fix parameterizing for kid in csp method
* Bug fix in delete_arc_agents for arm64 parameter
* Added specific exception messages for pre-checks

1.3.11
++++++
* Added support for custom AAD token
* Removed ARM64 unsupported warning
* Increased helm delete timeout for ARM64 clusters
* Added multi-architectural images for troubleshoot* Delete azure-arc-release NS if exists as part of delete command

1.3.10
++++++
* Added CLI heuristics change
* Added AKS IOT infra support 
* Bug Fix in precheckutils

1.3.9
++++++
* Added DNS and outbound connectivity prechecks in connect command

1.3.8
++++++
* Added connectedk8s proxy support for fairfax

1.3.7
++++++
* Install new helm release in azure-arc-release NS

1.3.6
++++++
* Updated patch behaviour for Azure Hybrid Benefit property

1.3.5
++++++
* Added software assurance related changes for AKS HCI
* Added parameter for overriding container log path
* Updated kubernetes package dependency to 24.2.0

1.3.4
++++++
* Fixed a proxy related bug in connectedk8s upgrade

1.3.3
++++++
* Added a timeout in force delete's CRD deletion command

1.3.2
++++++
* Added force delete command which is an added functionality in connectedk8s delete function

1.3.1
++++++
* Updated min cli core version to 2.30.0

1.3.0
++++++
* Added private link support

1.2.11
++++++
* Increased the timeout of diagnoser job completion to 180 seconds

1.2.10
++++++
* Added troubleshoot command which can be used to diagnose Arc enabled K8s clusters

1.2.9
++++++
* Add correlation-id parameter to internally track onboarding sources

1.2.8
++++++
* Bump up CSP version to 1.3.019103, bump up `pycryptodome` to 3.14.1 to support Python 3.10

1.2.7
++++++
* Avoid using packaging module and revert minCliCoreVersion to 2.16.0

1.2.6
++++++
* Update minCliCoreVersion to 2.23.0

1.2.5
++++++
* Using MSAL based auth for CLI version >= 2.30.0

1.2.4
++++++
* Custom cert changes, using "userValues.txt" for existing values in update command instead of --reuse-values, fix to wait for LRO to complete before starting agent installation/deletion

1.2.3
++++++
* Fetching the tenantID from subscription object instead of graphclient

1.2.2
++++++
* Updated connectedk8s proxy to support mooncake

1.2.1
++++++
* Add maxCliCoreVersion as 2.29.0

1.2.0
++++++
* Updated CSP version to 1.3.017131
* Updated GA SDK to 2021-10-01
* Updated CSP endpoint to CDN
* Disabled proxy command in fairfax

1.1.11
++++++
* Installing helm binary as part of CLI commands

1.1.10
++++++
* Fixed ARM exception telemetry

1.1.9
++++++
* Increase onboarding and upgrade timeout

1.1.8
++++++
* Improve kubernetes distro and infra detection


1.1.7
++++++
* Add non-existing namespace deploy check
* Improve some error and warning experiences


1.1.6
++++++
* Moved to track2 SDK
* `az connectedk8s connect`: Added onboarding timeout parameter
* `az connectedk8s upgrade`: Added upgrade timeout parameter
* Release namespace detection bug fix in multiple commands


1.1.5
++++++
* Add custom-locations oid parameter for spn scenario


1.1.4
++++++
* Add compatible logic for the track 2 migration of resource dependence


1.1.3
++++++
* Fix for list_node() sdk function for AKS v1.19.x clusters
* Some logging and telemetry fixes


1.1.2
++++++
* Fix/remove bug for unused error type import from az cli version 2.16.0+


1.1.1
++++++
* Adapting to the new CLI error handling guidelines


1.1.0
++++++
* Adding enable/disable features support and az connectedk8s proxy

1.0.0
++++++
* Moving to GA API version

0.2.9
++++++
* `az connectedk8s connect`: Added support for disabling auto upgrade of agents
* `az connectedk8s update`: Added support for switching on/off the auto-upgrade
* `az connectedk8s upgrade`: Added support for manual upgrading of agents

0.2.8
++++++
* Added checks for proxy and added disable-proxy
* Updated config dataplane endpoint to support other clouds
* `az connectedk8s connect`: Added support for kubernetes distro/infra parameters and heuristics

0.2.7
++++++
* Fixed dependency version in setup file

0.2.6
++++++
* `az connectedk8s connect`: Added support for proxy cert
* `az connectedk8s update`: Added support for proxy cert

0.2.5
++++++
* `az connectedk8s connect`: Added support for Dogfood cloud
* `az connectedk8s update`: Added support for Dogfood cloud

0.2.4
++++++
* `az connectedk8s connect`: Bug fixes and updated telemetry
* `az connectedk8s delete`: Bug fixes and updated telemetry
* `az connectedk8s update`: Bug fixes and updated telemetry

0.2.3
++++++
* `az connectedk8s connect`: Modified CLI params for proxy
* `az connectedk8s update`: Added update command

0.2.2
++++++
* `az connectedk8s connect`: Added CLI params to support proxy.

0.2.1
++++++
* `az connectedk8s connect`: Added kubernetes distribution.

0.2.0
++++++
* `az connectedk8s connect`: Added telemetry.
* `az connectedk8s delete`: Added telemetry.

0.1.5
++++++
* Initial release.
