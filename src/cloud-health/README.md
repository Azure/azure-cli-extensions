# az cloud-health

Azure CLI extension for the Microsoft.CloudHealth resource provider (API version `2026-01-01-preview`).

## Install (local dev)

```bash
pip install -e /path/to/azure-mgmt-cloudhealth
pip install -e .
```

## Commands

```
az cloud-health health-model   create|show|list|update|delete
az cloud-health entity         create|show|list|delete|get-history|get-signal-history|ingest
az cloud-health signal-definition  create|show|list|delete
az cloud-health relationship   create|show|list|delete
az cloud-health auth-setting   create|show|list|delete
az cloud-health discovery-rule create|show|list|delete
```
