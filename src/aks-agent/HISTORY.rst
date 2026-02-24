.. :changelog:

Release History
===============

Guidance
++++++++
If there is no rush to release a new version, please just add a description of the modification under the *Pending* section.

To release a new version, please select a new version number (usually plus 1 to last patch version, X.Y.Z -> Major.Minor.Patch, more details in `\doc <https://semver.org/>`_), and then add a new section named as the new version number in this file, the content should include the new modifications and everything from the *Pending* section. Finally, update the `VERSION` variable in `setup.py` with this new version number.

Pending
+++++++

1.0.0b18
++++++++
* Bump aks-agent to v0.3.0
  * chore: use aks mcp streamable-http mode
  * Remove runbook toolset until it's stabilized
  * Several CEV fixes
* Fix: accept endpoints ending with cognitiveservices.azure.com/ for Azure OpenAI service

1.0.0b17
++++++++
* Fix: remove the prompt to user about managed identity client id during `az aks agent-init`
 
1.0.0b16
++++++++
* Fix: client mode use AzureCLICredential to authenticate with Azure
* Fix: correct wrong prompt message for init and cleanup
* Fix: prompt the whole flags including --resource-group, --name and optional --namespace for az aks agent command
* Enhancement: cluster mode cleanup will wait for pods to be removed after deletion

1.0.0b15
++++++++
* Feature: Add local mode support - run AKS agent in Docker container on local machine as an alternative to cluster deployment
* Feature: Mode selection during `az aks agent-init` - choose between cluster mode (Helm deployment) or local mode (Docker container)
* Feature: Cluster Mode requires the user to specify the namespace and service account name during `az aks agent-init`
* Feature: Cluster Mode requires namespace for `az aks agent-cleanup` and `az aks agent`
* Enhancement: Comprehensive telemetry tracking - track init, cleanup, and startup events with mode information (cluster/local)

1.0.0b14
++++++++
* Fix: set stdout to blocking mode to avoid "BlockingIOError: [Errno 35] write could not complete without blocking"
* Fix: gracefully handle the connection reset error
* Fix: correct the prompt to user `az aks agent-init` to initialize the aks agent
* Fix: dont echo the user input for Linux users
* Close websocket and restore terminal settings after `az aks agent` ends

1.0.0b13
++++++++
* Fix subscription id not correctly set in helm chart

1.0.0b12
++++++++
* [BREAKING CHANGE]:
  * aks-agent is now containerized and deployed per Kubernetes cluster along with a managed aks-mcp instance
  * aks-agent is deployed on the AKS cluster as Helm charts during `az aks agent-init`
  * aks agent commands now require --resource-group and --name parameters to specify the target AKS cluster
  * Add `az aks agent-cleanup` to cleanup the AKS agent from the cluster
* [SECURITY]:
  * Kubernetes RBAC: Uses cluster roles to securely access Kubernetes resources with least-privilege principles
  * Azure Workload Identity: Supports Azure workload identity for secure, keyless access to Azure resources
  * LLM credentials are stored securely in Kubernetes secrets with encryption at rest

1.0.0b11
++++++++
* Fix(agent-init): replace max_tokens with max_completion_tokens for connection check of Azure OpenAI service.

1.0.0b10
++++++++
* Pin supabase==2.8.0 to avoid "ModuleNotFoundError: No module named 'supabase_auth.http_clients'"

1.0.0b9
+++++++
* agent-init: replace model name with deployment name for Azure OpenAI service.
* agent-init: remove importing holmesgpt to resolve the latency issue.

1.0.0b8
+++++++
* Error handling: dont raise traceback for init prompt and holmesgpt interaction.
* Improve aks agent-init user experience
* Improve the user holmesgpt interaction error handling
* Fix stdin reading hang in CI/CD pipelines by using select with timeout for non-interactive mode.
* Update pytest marker registration and fix datetime.utcnow() deprecation warning in tests.
* Improve test framework with real-time stderr output visibility and subprocess timeout.

1.0.0b7
+++++++
* Bump aks-mcp to v0.0.10 - here are the notable changes:
  * Fix: Improved server health check endpoints /health for both HTTP and SSE connections for http, sse
  * Fix: enforce json output for az monitor metrics and aks tools
  * Fix: Build the resource URL with correct MCP endpoint path based on transport
* Fix feedback slash command

1.0.0b6
+++++++
* Introduce the new `az aks agent-init` command for better cli interaction.
* Separate llm configuration from main agent command for improved clarity and extensibility.

1.0.0b5
+++++++
* Bump holmesgpt to 0.15.0 - Enhanced AI debugging experience and bug fixes
  * Added TODO list feature to allows holmes to reliably answers questions it wasn't able to answer before due to early-stopping
  * Fixed mcp server http connection fails when using socks proxy by adding the missing socks dependency
  * Fixed gpt-5 temperature bug by upgrading litellm and dropping non-1 values for temperature
  * Improved the installation time by removing unnecessary dependencies and move test dependencies to dev dependency group
* Added Feedback slash command Feature to allow users to provide feedback on their experience with the agent performance
* Disable prometheus toolset loading by default to workaround the libbz2-dev missing issue in Azure CLI python environment.

1.0.0b4
+++++++
* Fix the --aks-mcp flag to allow true/false values.
* Bump aks-mcp version to v0.0.9

1.0.0b3
+++++++
* Disable aks-mcp by default, offer --aks-mcp flag to enable it.
* Don't print version check at bottom toolbar


1.0.0b2
+++++++

* Add MCP integration for `az aks agent` with aks-mcp binary management and local server lifecycle (download, version validation, start/stop, health checks).
* Introduce dual-mode operation: MCP mode (enhanced) and Traditional mode (built-in toolsets), with mode-specific system prompts.
* Implement smart toolset refresh strategy with persisted mode state to avoid unnecessary refresh on repeated runs.
* Add `--no-aks-mcp` flag to force Traditional mode when desired.
* Add `az aks agent --status` command to display MCP binary availability/version, server health, and overall mode/readiness.
* Add structured error handling with user-friendly messages and actionable suggestions for MCP/binary/server/config errors.
* Port and adapt comprehensive unit tests covering binary manager, MCP manager, configuration generation/validation, status models/collection, error handling, user feedback, parameters, smart refresh, MCP integration, and status command.

1.0.0b1
+++++++
* Add interactive AI-powered debugging tool `az aks agent`.
