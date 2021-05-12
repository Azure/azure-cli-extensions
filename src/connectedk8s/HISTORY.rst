.. :changelog:

Release History
===============

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
