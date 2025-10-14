.. :changelog:

Release History
===============

Guidance
++++++++
If there is no rush to release a new version, please just add a description of the modification under the *Pending* section.

To release a new version, please select a new version number (usually plus 1 to last patch version, X.Y.Z -> Major.Minor.Patch, more details in `\doc <https://semver.org/>`_), and then add a new section named as the new version number in this file, the content should include the new modifications and everything from the *Pending* section. Finally, update the `VERSION` variable in `setup.py` with this new version number.

Pending
+++++++

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
