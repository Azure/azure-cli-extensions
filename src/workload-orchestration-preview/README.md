# Workload Orchestration

## What is Workload Orchestration?

Workload orchestration for Azure Arc is a comprehensive, cloud-native, cross-platform service engine that simplifies the deployment, management, and update of application workloads across edge environments. It addresses typical application lifecycle management problems for customers who need application deployments across multiple fleets with site-specific configurations and natively supports Kubernetes workloads.

## What Problems Does Workload Orchestration Solve?

Workload orchestration addresses several key challenges faced by organizations managing applications at the edge:

- **Distributed Configuration Authoring**: Managing configuration files for multiple applications often requires input from different stakeholders across various edge locations, making collaboration and consistency difficult.
- **Edge Contextualization**: Edge environments typically include diverse devices and complex topologies, each requiring tailored configurations to meet site-specific needs.
- **Configuration Validation**: Ensuring that configuration parameters are correct before deployment is critical to prevent misconfigurations and avoid costly downtime or productivity loss.
- **Version Management**: Maintaining multiple versions of application code and configuration files can complicate auditing and tracking changes across deployments.
- **Lack of Visibility**: Without a unified view of applications and deployment status, identifying failures and optimizing operations becomes a manual, resource-intensive process.
- **Role-Based Access Control (RBAC)**: Enforcing role-based access ensures that only authorized users can manage and operate within their designated scope, improving security and governance.
- **Logging and Traceability**: Comprehensive logging and error tracing are essential for effective debugging, remediation, and compliance.

## Key Features

- **Template Framework and Schema Inheritance**: Define solution configurations and schemas once, then reuse or extend them for multiple deployments. Central IT teams can create a single source of truth for app configurations, which sites can inherit and customize as needed.
- **Dependent Application Management**: Deploy and manage interdependent applications using orchestrated workflows. Supports configuring and deploying apps with dependencies through the CLI or workload orchestration portal.
- **Custom and External Validation Rules**: Administrators can define pre-deployment validation rules to check parameter inputs and settings, preventing misconfigurations. External validation lets you verify templates through services like Azure Functions or webhooks.
- **Integrated Monitoring and Unified Control**: Monitor deployments and workload health from a centralized dashboard. Pause, retry, or roll back deployments as needed, with full logging and compliance visibility.
- **No-Code Authoring Experience with RBAC**: The workload orchestration portal offers a no-code UI for defining and updating application settings, secured with role-based access control and audit logging.
- **CLI and Automation Support**: IT admins and DevOps engineers can use the CLI for scripted deployments, automation, and CI/CD integration, enabling bulk management of application lifecycles across sites.
- **Fast Onboarding and Setup**: Guided workflows help you quickly configure your organizational hierarchy, user roles, and access policies.

## How It Works

Workload orchestration uses both cloud and edge components to deliver a unified management experience. The cloud-based control plane leverages a dedicated Azure resource provider, allowing you to centrally define deployment templates. These templates are then consumed by workload orchestration agents running at edge locations, which automatically adapt and apply the necessary customizations for each site.

All workload orchestration resources are managed through Azure Resource Manager, enabling fine-grained Role-Based Access Control (RBAC) and consistent governance. You can interact with workload orchestration using the CLI and Azure portal, while non-code onsite staff benefit from a user-friendly interface for authoring, monitoring, and deploying solutions with site-specific configurations.

---

## Getting Started

This guide will help you get started with Workload Orchestration for authoring, deploying, and monitoring application configurations using the converged object model.

Key features of the public preview release include end-to-end flows for application dependencies, along with an enhanced UI experience offering additional capabilities like Compare, Copy, Delete, Uninstall, and more.

---

## User Personas

- **IT Persona**
  - *IT Admin*: Responsible for initial setup via CLI.
  - *IT Developer/DevOps*: Manages applications and configurations using CLI.
- **OT Persona**
  - No-code users, using the portal for day-to-day activities.

| Profile         | How to use Workload Orchestration |
|-----------------|-----------------------------------|
| IT Admin/DevOps | Use CLI as described below        |
| OT personas     | Use [the portal](https://int.test.digitaloperations.configmanager.azure.com/#/browse/overview) |

---

## Workload Orchestration CLI Steps

### 1. Install Extension & Login

```sh
az extension add --source <path-to-extension-file-workload-orchestration.whl>
az login
```

---

### 2. Create/Update Context

```sh
az workload-orchestration context create \
  --subscription <subscription-id> \
  --resource-group <resource-group> \
  --location <location> \
  --name <context-name> \
  --capabilities "@context-capabilities.json" \
  --hierarchies [0].name=country [0].description=Country [1].name=region [1].description=Region [2].name=factory [2].description=Factory [3].name=line [3].description=Line
```

---

### 3. Create Site Reference

```sh
az workload-orchestration context.site-reference create \
  --subscription <subscription-id> \
  --resource-group <resource-group> \
  --context-name <context-name> \
  --name <site-reference-name> \
  --site-id "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Edge/sites/<site-name>"
```

---

### 4. Create Target

```sh
az workload-orchestration target create \
  --resource-group <resource-group> \
  --location <location> \
  --name <target-name> \
  --display-name <display-name> \
  --hierarchy-level line \
  --capabilities <capability> \
  --description "<description>" \
  --solution-scope "new" \
  --target-specification '@targetspecs.json' \
  --extended-location '@custom-location.json'
```

---

### 5. Create Schema

```sh
az workload-orchestration schema create \
  --resource-group <resource-group> \
  --version "1.0.0" \
  --schema-name <schema-name> \
  --schema-file ./shared-schema.yaml \
  --location <location>
```

Or, if version is in the file, omit `--version`.

---

### 6. Create Solution Template and Version

```sh
az workload-orchestration solution-template create \
  --solution-template-name <solution-template-name> \
  -g <resource-group> \
  -l <location> \
  --capabilities <capability> \
  --description "<description>" \
  --configuration-template-file ./hotmelt-config-template.yaml \
  --specification "@specs.json" \
  --version "1.0.0"
```

```sh
az workload-orchestration solution-template-version create \
  --template-name <solution-template-name> \
  --version 1.0.0 \
  --file solution-template-version.yaml
```

---

### 7. Set Configuration Values

```sh
az workload-orchestration configuration set \
  -g <resource-group> \
  --solution-template-name <solution-template-name> \
  --target-name <target-name>
```

---

### 8. Resolve and Review

```sh
az workload-orchestration target review \
  --solution-template-name <solution-template-name> \
  --solution-template-version 1.0.0 \
  --resource-group <resource-group> \
  --target-name <target-name>
```
*Review the output for `reviewId` and new solution version.*

---

### 9. Publish and Install

**Publish:**
```sh
az workload-orchestration target publish \
  --solution-name <solution-template-name> \
  --solution-version <new-version> \
  --review-id <review-id> \
  --resource-group <resource-group> \
  --target-name <target-name>
```

**Install:**
```sh
az workload-orchestration target install \
  --solution-name <solution-template-name> \
  --solution-version <new-version> \
  --resource-group <resource-group> \
  --target-name <target-name>
```

---
