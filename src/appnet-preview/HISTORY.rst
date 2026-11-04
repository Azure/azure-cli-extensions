.. :changelog:

Release History
===============

1.0.0b4
++++++
* Update AppNet commands to the `2026-08-01-preview` API version and add `--network-name` to `az appnet member join` and `az appnet member update`.

1.0.0b3
++++++
* Make `--member-location` optional on `az appnet member join`; when omitted it defaults to the location of the member cluster referenced by `--member-resource-id`.

1.0.0b2
++++++
* Add `--east-west-gateway` to `az appnet member join` and `az appnet member update`
* Add `--private-connect-subnet` to `az appnet member join`.

1.0.0b1
++++++
* Initial release.