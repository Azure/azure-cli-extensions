.. :changelog:

Release History
===============
5.1.1
++++++
* Resolved solution template name to uniqueIdentifier for ``az workload-orchestration target solution-revision-list`` and ``az workload-orchestration target solution-instance-list``
* Added shared ``_target_helper.py`` for reusable solution template resolution logic
* Added ``az workload-orchestration support create-bundle`` command for troubleshooting Day 0 (installation) and Day N (runtime) issues on 3rd-party Kubernetes clusters:
  * Collects cluster info, node details, pod/deployment/service/event descriptions across configurable namespaces
  * Collects container logs (current + previous for crash-looping pods) with configurable tail lines
  * Runs prerequisite validation checks across 10 categories
  * Generates a zip bundle for sharing with Microsoft support
  * Includes retry with exponential backoff and per-call timeout for resilient K8s API access

5.1.0
++++++
* Added new target solution management command:
  * ``az workload-orchestration target unstage`` - Unstage a solution version from a target
* Added double confirmation before ``az workload-orchestration target remove-revision`` to prevent accidental deletions

5.0.0
++++++
* November 2025 release

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