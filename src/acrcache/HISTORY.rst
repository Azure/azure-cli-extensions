.. :changelog:

Release History
===============
1.1.2 - version 1.0.0c8
++++++
* **BUGFIX**: Resolved issue with sync-referrers enabled without sync activesync
  * Added validation to ensure `--sync-referrers` can only be used with `--sync activesync`
  * Ensured proper validation and assignment of managed identities in `az acr cache create` and `az acr cache update` commands


1.1.1 - version 1.0.0c7
++++++
* **FEATURE**: Added `--assign-identity` parameter support for cache rules
  * `az acr cache create --assign-identity` - Create cache rules with user-assigned managed identities
  * `az acr cache update --assign-identity` - Update existing cache rules with managed identities
  * Enables secure authentication for ACR-to-ACR caching across subscriptions and tenants
  * Supports Azure resource ID format validation for managed identity resources
* **ENHANCEMENT**: Improved error handling and validation for identity parameters
* **TESTING**: Added comprehensive unit test coverage for identity processing functionality

1.1.0 - version 1.0.0c6
++++++
* **BREAKING**: Migrated to Container Registry SDK v2025-09-01-preview
  * Updated SDK imports from v2025_07_01_preview to v2025_09_01_preview
  * Updated SDK client factory to support new API version
* **ENHANCEMENT**: Standardized enum values for sync and referrer status
  * Sync parameter now uses ActiveSync/PassiveSync values
  * Referrer status now uses Enabled/Disabled values
  * Added case-insensitive comparisons and improved None handling
* **REFACTOR**: Improved validation and state logic
  * Refactored input validation logic in cache.py for sync/referrer options
  * Modified CLI argument definitions in _params.py to reflect new enum values
  * Enhanced error handling and parameter validation
* **DOCUMENTATION**: Updated help examples for clarity
  * Rewrote help examples in _help.py for alignment with new conventions
  * Improved CLI documentation and usage examples
* **TESTING**: Expanded test coverage
  * Added comprehensive unit tests for cache operations and validation logic
  * Updated test coverage to support the new API version
  * Enhanced reliability testing under new SDK
* **COMPATIBILITY**: No breaking changes to CLI interface, only behavioral improvements

1.0.0
++++++
* Initial release.