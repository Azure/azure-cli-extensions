.. :changelog:

Release History
===============

1.0.0b2
++++++
* Update every Agent Fabric command and wait to API version ``2026-11-03-preview``.
* Add MCP matching conditions, TLS inspection rules, optional rule actions, and longer resource names.
* Add conditional AKS attachment through ``--if-none-match`` and optional target IDs in the generated PATCH schema.
* Preserve ACI, AKS, and Agent Fabric Sandbox member response fields.

1.0.0b1
++++++
* Initial preview release for Azure Agent Fabric using API version ``2026-10-07-preview``.
* Add Agent Fabric and Policy Group create, show, list, update, delete, and wait commands.
* Add member show, list, and wait commands for existing members; resource providers handle member creation, updates, and deletion.
* Add AKS attach, show, list, update, detach, and wait enrollment commands.
* Add system-assigned Fabric identity and customer-owned Content Safety connection configuration.
* Preserve service/target port mappings and optional Entra agent identity and blueprint metadata when reading existing Agent Fabric Sandbox members.
* Add egress trust bundle show and list commands.