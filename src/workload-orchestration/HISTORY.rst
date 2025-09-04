.. :changelog:

Release History
===============

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