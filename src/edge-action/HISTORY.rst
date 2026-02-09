.. :changelog:

Release History
===============

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