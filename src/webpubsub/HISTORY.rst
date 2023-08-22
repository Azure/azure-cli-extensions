.. :changelog:

Release History
===============

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