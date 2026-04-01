.. :changelog:

Release History
===============

1.0.0b1
+++++++
* Initial release.

1.0.0b2
+++++++
* Add frontend commandlets
* Add MSAL device code flow authentication

1.0.0b3
++++++
* Update commands to reflect new API version 2026-03-31-preview

1.0.0b4
+++++++
* Updated to latest Frontend API spec from develop branch (2026-03-01-preview)
* Regenerated analytics_frontend_api SDK with updated method signatures
* SDK Changes (internal, transparent to CLI users):
  - Method renames: collaboration.list → collaboration.list_get
  - Method renames: analytics_dataset_* → analytics_datasets_* (dataset → datasets, plural)
  - Method renames: check_consent_document_id_get → consent_document_id_get
  - Method renames: set_consent_document_id_put → consent_document_id_put
* BREAKING CHANGE: All frontend API endpoints now require api-version=2026-03-01-preview query parameter
* Added: --api-version parameter to all frontend commands (default: 2026-03-01-preview)
* Updated: SDK client now automatically injects api-version into all API requests
* BREAKING CHANGE: Removed deprecated commands (APIs no longer supported in SDK):
  - `az managedcleanroom frontend workloads list`
  - `az managedcleanroom frontend analytics deploymentinfo`
  - `az managedcleanroom frontend attestation cgs`
  - `az managedcleanroom frontend analytics attestationreport cleanroom`
  - `az managedcleanroom frontend analytics query vote accept`
  - `az managedcleanroom frontend analytics query vote reject`
* BREAKING CHANGE: Consent action values changed from 'accept/reject' to 'enable/disable'
* BREAKING CHANGE: Vote commands consolidated into single unified endpoint
* Added: `az managedcleanroom frontend report` - Comprehensive attestation report (replaces cgs/cleanroom commands)
* Added: `az managedcleanroom frontend oidc set-issuer-url` - Configure OIDC issuer URL
* Added: `az managedcleanroom frontend oidc keys` - Get OIDC signing keys (JWKS)
* Added: `az managedcleanroom frontend analytics dataset queries` - List queries using a specific dataset
* Added: `az managedcleanroom frontend analytics secret set` - Set analytics secrets
* Added: `az managedcleanroom frontend analytics query vote` - Unified vote command with --vote-action parameter
* Updated: Added --active-only filter to collaboration list and show commands
* Updated: Added --pending-only filter to invitation list command
* Updated: Added --scope, --from-seqno, --to-seqno filters to audit event list command
* Updated: Response structures modernized (many list endpoints now return structured objects with value arrays)

1.0.0b5
+++++++
* Updated to latest Frontend API spec (2026-03-01-preview with SKR policy)
* Regenerated analytics_frontend_api SDK with updated method signatures and SKR policy support
* BREAKING CHANGE: Removed `az managedcleanroom frontend analytics cleanroompolicy` command
* Added: `az managedcleanroom frontend analytics skr-policy` - Get SKR (Secure Key Release) policy for a specific dataset
  - New required parameter: --dataset-id to specify the dataset for which to retrieve the SKR policy
* SDK Changes (internal):
  - Added: collaboration.analytics_skr_policy_get(collaboration_id, dataset_id) method
  - Removed: collaboration.analytics_cleanroompolicy_get(collaboration_id) method
  - Fixed: analytics_queries_document_id_runhistory_get → analytics_queries_document_id_runs_get
  - Fixed: analytics_queries_jobid_get → analytics_runs_job_id_get
* Bug Fixes:
  - Fixed token normalization in _frontend_auth.py to handle tuple, AccessToken, and string token formats
  - Added SSL verification environment variable support (AZURE_CLI_DISABLE_CONNECTION_VERIFICATION, REQUESTS_CA_BUNDLE)
  - Fixed schema_file parameter handling in dataset publish to support Azure CLI auto-loading (dict, string, and @file formats)
  - Fixed runhistory API endpoint method name
  - Fixed runresult API endpoint method name
