# Workload Orchestration

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
