.. :changelog:

Release History
===============

1.7.1
+++++
* Upgrade `websockets` to `13.0.1` to sure the compatibility with Python 3.12

1.7.0
+++++
* Add `az webpubsub update --client-cert-enable/--disable-local-auth/--region-endpoint-enabled` support
* Add `az webpubsub replica update -region-endpoint-enabled/--unit-count` support
* Add `az webpubsub custom-certificate list/show/create/delete` support
* Add `az webpubsub custom-domain list/show/create/delete` support
* Add `az webpubsub identity assign/remove/show` support

1.6.0
+++++
* Add `az webpubsub start/stop` support
* Add `az webpubsub replica start/stop/restart` support
* Add `az webpubsub network-rule ip-rule add/remove` support
* Update `az webpubsub hub create/update` to support `webSocketKeepAliveIntervalInSeconds`


1.5.1
+++++
* Update the min core version to `2.56.0`

1.5.0
+++++
* Add `service-mode` for Web PubSub for Socket.IO

1.4.0
+++++
* Add `az webpubsub replica create/delete/list/show` support for replica

1.3.0
+++++
* Add `kind` support for creating resource

1.2.0
+++++
* Drop python 3.6 support
* Update websocket dependency version
* Remove hard limit of sku

1.1.0
++++++
* Add `az webpubsub list-usage`
* Add `az webpubsub list-skus`
* Sending event in `az webpubsub client start` returns result.
* Follow the return value guidance that returns a dictionary rather than bool in check existence operation like `webpubsub service connection exist`
* Some description and help update

1.0.0
++++++
* Add command group `az webpubsub hub`
* [Breaking] Remove command group `az webpubsub event-handlers`

0.2.1
++++++
* Add argument `--user-id` to command: `az webpubsub client start`

0.2.0
++++++
* Add data plane command: `az webpubsub client` and `az webpubsub service`

0.1.0
++++++
* Initial release.