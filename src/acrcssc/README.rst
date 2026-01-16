Microsoft Azure CLI 'acrcssc' Extension
==========================================

Azure Container Registry - Container Secure Supply Chain (Continuous Patching)
==========================================

Overview
========
The `acrcssc` extension for Azure CLI provides continuous patching capabilities for Azure Container Registry (ACR). This extension helps automate the process of scanning and patching container images to ensure they are up-to-date with the latest security patches. Scans your configured list of images for vulnerabilities (CVEs) using Trivy and patch them using Copacetic.

Preview Limitations
===================
Continuous Patching is currently in preview. The following limitations apply:

- Windows-based container images aren’t supported
- Only "OS-level" vulnerabilities will be patched. This includes packages in the image managed by a package manager such as “apt” and “yum”. Vulnerabilities at the “application level” are unable to be patched, such as compiled languages like Go, Python, NodeJS
- Patching is only supported in Public regions, not in Sovereign regions
- CSSC patching is not supported for registries or in regions where Tasks are unavailable.

Features
========
- **Continuous Patching Workflow**: Automates the process of scanning and patching container images.
- **Task Management**: Create, update, delete, show, and cancel continuous patch tasks in the registry.
- **Dry Run Mode**: Validate the configuration without making any changes.
- **Immediate Run**: Trigger the patching workflow immediately.
- **Run Status**: Monitor the status of the scanning and patching tasks.

Commands
========
- `az acr supply-chain workflow create`: Create a continuous patch task in the registry.
- `az acr supply-chain workflow update`: Update an existing continuous patch task.
- `az acr supply-chain workflow delete`: Delete a continuous patch task.
- `az acr supply-chain workflow list`: List all continuous patch tasks in the registry.
- `az acr supply-chain workflow show`: Show details of a specific continuous patch task.
- `az acr supply-chain workflow cancel-run`: Cancel all running scan and patch tasks.

Usage
=====
1. **Create a Continuous Patch Task**:
   ```sh
   az acr supply-chain workflow create --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1 --schedule <schedule> --config <config-file>
   ```

1. **Update a Continuous Patch Task**:
   ```sh
   az acr supply-chain workflow update --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1 --schedule <schedule> --config <config-file>
   ```

1. **Update with dryrun to test configuration changes**:
   ```sh
   az acr supply-chain workflow update --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1 --config <config-file> --dryrun
   ```

1. **Delete a Continuous Patch Task**:
   ```sh
   az acr supply-chain workflow delete --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1
   ```

1. **List Continuous Patch Tasks**:
   ```sh
   az acr supply-chain workflow list --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1 --run-status <status>
   ```

1. **Show a Continuous Patch Task**:
   ```sh
   az acr supply-chain workflow show --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1
   ```

1. **Cancel all Scan and Patch Running Tasks**:
   ```sh
   az acr supply-chain workflow cancel-run --resource-group <resource-group> --registry <registry-name> --type continuouspatchv1
   ```

Configuration
=============
The configuration file for the continuous patch task should define the repositories to be scanned and patched, the schedule for the task, and any other relevant settings.

Example Configuration:

```JSON
{
  "repositories": [
    {
      "repository": "alpine",
      "tags": ["tag1", "tag2"],
      "enabled": true
    },
    {
      "repository": "python",
      "tags": ["*"],
      "enabled": false
    }
  ],
  "version": "v1",
  "tag-convention": "floating"
}
```

Tag Convention
==============
The `tag-convention` property in the configuration file determines how the tags for patched images are managed. It can have the following values:

- **incremental**: This is the default behavior. It increases the patch version of the tag. For example, if the original tag is `1.0`, the patched tags will be `1.0-1`, `1.0-2`, etc.
- **floating**: This reuses the tag postfix `patched` for patching. For example, if the original tag is `1.0`, the patched tag will be `1.0-patched`.
