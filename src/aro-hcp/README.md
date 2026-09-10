# Azure CLI aro-hcp Extension

This extension adds the `az aro hcp` command group to manage Azure Red Hat OpenShift clusters with hosted control planes.

## How to Use 

- `az aro hcp get-versions --location <location>`
- `az aro hcp cluster create -g <rg> -n <name> --location <location> --version <x.y> --subnet-id <subnet-id> ...`
- `az aro hcp cluster show -g <rg> -n <name>`
- `az aro hcp cluster list -g <rg>`
- `az aro hcp cluster update -g <rg> -n <name> ...`
- `az aro hcp cluster request-credential -g <rg> -n <name> --admin -f <path|->`