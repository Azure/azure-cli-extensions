.. :changelog:

Release History
===============

1.0.0b4
+++++++
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
* Updated: Regenerated frontend SDK from OpenAPI spec to support new APIs

1.0.0b3
+++++++
* Regenerate analytics_frontend_api SDK from updated frontend.yaml OpenAPI spec
* Remove empty enum value from ApplicationState schema

1.0.0b1
+++++++
* Initial release.

1.0.0b2
+++++++
* Add frontend commandlets
* Add MSAL device code flow authentication