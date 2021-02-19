.. :changelog:

Release History
===============

0.3.7
++++++
* Pulled GA changes

0.3.6
++++++
* Added az connectedk8s proxy

0.3.5
++++++
* Fixed Custom tenant id issue with validation

0.3.4
++++++
* Synced with Azure cli-extensions repo
 
0.3.3
++++++
* Fixed Custom tenant Id passability

0.3.2
++++++
* Fixed aad server/client app id validation
* Added descriptive error messages
* Added block for delete connected cluster using cluster connect credentials

0.3.1
++++++
* Fixed dependency version in setup file

0.3.0
++++++
* `az connectedk8s connect`: Added support for connect proxy
* `az connectedk8s get-credentials`: Added support for list cluster user credentials for both AAD and non-AAD connected clusters
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
