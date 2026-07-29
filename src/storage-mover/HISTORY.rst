.. :changelog:

Release History
===============

1.3.1
+++++
* Added system-assigned managed identity creation to `endpoint create-for-s3-with-hmac`.

1.3.0
+++++
* Updated to the 2025-12-01 GA API version.
* Added `connection` resource commands (create, delete, list, show, update, wait).
* Added S3-compatible storage endpoint type (`create-for-s3-with-hmac`, `update-for-s3-with-hmac`).
* Added `schedule`, `connections`, `preserve-permissions`, and `data-integrity-validation` parameters to job definition commands.
* Fixed allowed values for S3WithHmac `source-type` parameter to match 2025-12-01 API spec: added `ALIBABA`, `DELL_EMC`, `OTHER` and removed deprecated `BACKBLAZE`, `CLOUDFLARE`.

1.2.1
+++++
* Added system assigned MI creation as part of az storage-mover endpoint create-for-storage-container command.

1.2.0
+++++
* Updated to the 2025-07-01 GA API version. 
* Add new endpoints for storage-nfs-file-share and multi-cloud-connector.

1.1.0
++++++
* Update to 2024-07-01 GA api version
* `az storage-mover agent update`: support `--upload-limit-schedule`

1.0.0
++++++
* Update to 2023-10-01 GA api version

1.0.0b1
++++++
* Add new endpoints for storage-smb-file-share and smb mount.
* BREAKING CHANGE: remove non-updatable params in endpoint update commands. 

0.1.1
++++++
* Remove preview tag for endpoint create/update commands.

0.1.0
++++++
* Initial release.
