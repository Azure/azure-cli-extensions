.. :changelog:

Release History
===============

5.0.0
++++++
* November 2025 release
* Added `az workload-orchestration support create-bundle` command for troubleshooting Day 0 (installation) and Day N (runtime) issues on 3rd-party Kubernetes clusters:
  * Collects cluster info, node details, pod/deployment/service/event descriptions across configurable namespaces
  * Collects container logs (current + previous for crash-looping pods) with configurable tail lines
  * Runs 18 prerequisite validation checks across 10 categories: K8s version, node readiness, CoreDNS health, registry access, cert-manager, namespace validation, resource availability, admission controllers, storage configuration, and WO component health
  * Generates a zip bundle with health summary score (HEALTHY/DEGRADED/CRITICAL) for sharing with Microsoft support
  * Supports `--skip-checks`, `--skip-logs`, `--full-logs`, `--namespaces`, `--kube-config`, `--kube-context` options
  * Includes retry with exponential backoff and per-call timeout for resilient K8s API access
  * RBAC-aware error handling with actionable remediation guidance

4.1.0
++++++
* Added currentStage and latestActionTriggeredBy fields in response of below commands:
  * ``az workload-orchestration target review`` - Post request to review configuration.
  * ``az workload-orchestration target solution-revision-list`` - List all revisions of a solution deployed on a target.

4.0.0
++++++
* Added new bulk management commands:
  * ``az workload-orchestration solution-template bulk-review`` - Review solutions across multiple targets and apply target-specific configurations in bulk
* Added option in bulk publish to publish solution even without review
* Updated context ID validation during target create for improved reliability
* Upgraded API version from 2025-06-01 to 2025-08-01

3.0.0
++++++
* Added Context Management capabilities with new commands:
  * ``az workload-orchestration context use`` - Set current context by name and resource group
  * ``az workload-orchestration context set`` - Set current context using ARM resource ID
  * ``az workload-orchestration context current`` - Display current context information
* Added Solution Management commands:
  * ``az workload-orchestration target solution-instance-list`` - List all solution instances on a target
  * ``az workload-orchestration target solution-revision-list`` - List all revisions of solutions on a target
* Enhanced Target creation with automatic context fallback to CLI configuration
* Added persistent context storage in CLI configuration
* Improved error handling with better messages for context-related operations
* Added automatic fallback to default context when context-id is not provided
* Enhanced context ID validation for better user experience
* Added --version parameter to ``az workload-orchestration configuration config show``

2.0.0
++++++
* Added required context-id parameter to target create command
* Fixed target update command to preserve contextId property during PUT operations
* Enhanced package description with comprehensive workload orchestration summary
* Improved README documentation with detailed feature descriptions and use cases
* Better formatting and structure in package metadata

1.0.0
++++++
* Initial release.