.. :changelog:

Release History
===============

1.1.0
+++++
* `az edge-action list`: Add subscription-wide listing when `--resource-group` is omitted, while preserving resource-group-scoped listing and `--subscription` selection.

1.0.0
+++++
* GA release of the Edge Action extension.
* Upgrade Edge Action commands to stable API version `2026-10-01`.
* Add optional version ID and header name/value arguments to execution-filter updates while preserving omitted fields and generic update options.
* Preserve `get-version-code --output-directory`/`-d` ZIP downloads across command regeneration and report invalid download content and file-write errors.
* Preserve `swap-default` polling compatibility across command regeneration.
* Restore CLI help examples and correct version-update examples to use supported tag updates.

1.0.0b4
++++++
* Fix `swap-default` command failing with `TypeError: 'NoneType' object is not callable` by providing a no-op deserialization callback for the 202 LRO response
* Add test for `swap-default` command verifying default version changes correctly
* Re-enable execution filter CRUD test with code deployment prerequisite

1.0.0b3
++++++
* Upgrade to API version 2025-12-01-preview
* Remove `add-attachment` and `delete-attachment` commands (no longer supported in new API version)

1.0.0b2
++++++
* Fix 415 Unsupported Media Type error for `get-version-code` and `swap-default` POST operations by adding required Content-Type header and empty JSON body
* Add `--output-directory` parameter to `get-version-code` command to decode and save version code as zip file

1.0.0b1
++++++
* Initial release.