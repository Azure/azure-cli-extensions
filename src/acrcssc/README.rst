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

Scaling
=======
A workflow run can include up to **1,000 images** (the number of matches reported by ``--dryrun``). How quickly a run finishes depends mostly on the images, not on the extension:

- **Scheduling.** The trigger task schedules scan tasks in parallel (10 at a time), about 2 per second. In testing with 1,000 images, all scans were queued within 10 minutes and all patches within 13 minutes of the run starting. Images are scheduled in the order of the configuration file, so list the images that take longest to patch (Azure Linux, CBL-Mariner, UBI) first.
- **Patch time depends on the package manager.** Debian, Ubuntu and Alpine images typically patch in 1–3 minutes. Azure Linux, CBL-Mariner and Red Hat UBI images take about 9–16 minutes because Copacetic installs its RPM tooling for every patch. In testing, a 1,000-image run with about 20% RPM-based images finished 99% of images in 27 minutes.
- **Shared capacity.** Tasks run on the region's shared ACR Tasks agents. When a registry starts many runs at once, ACR Tasks gives its later runs lower priority so other customers aren't delayed; expect queue waits of a few minutes in large runs, and longer near the top of the hour, when many scheduled tasks start.
- **Trivy database.** The trigger task keeps a copy of the Trivy vulnerability database in the registry (``csscpolicies/trivy-db:2``) and refreshes it when the upstream copy changes. Scan and patch tasks read it from the registry and fall back to ``ghcr.io`` and ``public.ecr.aws``.

For larger fleets:

- **Use the floating tag convention** (``"tag-convention": "floating"``) so deployments can follow ``<tag>-patched`` without changing image references.
- **Split images across workflow runs** if you need more than 1,000 images or want to prioritize some images: run ``az acr supply-chain workflow update --config <next-config> --run-immediately`` after the previous trigger run has finished (check with ``az acr task list-runs --name cssc-trigger-workflow``). Each registry has one workflow, so runs for different configurations happen one after another.
- **Roll out patched images** by subscribing to the registry's push events for ``*-patched`` tags (for example with Event Grid) instead of polling.
- Use ``az acr supply-chain workflow list`` to see the scan and patch status for every image in the last schedule period; it reads all task runs, not just the most recent 1,000.

