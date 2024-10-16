# Data Collection

## vmss run-command in azure-cli

### use case: invoke

```bash
az vmss run-command invoke -g MC_azcli-aks-dev_dev100_westus2 -n aks-nodepool1-28844989-vmss --command-id RunShellScript --instance-id 0 --scripts 'for i in $(seq $1 $2); do echo $i; done' --parameters 1 100000
```

- synchronous operation, need to wait until the operation is completed
- the output will be truncated and cannot be automatically exported to external storage

### use case: CRUD

```bash
az vmss run-command list -g  MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0"
az vmss run-command show -g MC_azcli-aks-dev_dev100_westus2 -n aks-nodepool1-28844989-vmss --instance-id 0 --name 

# run command for the first time
az vmss run-command create -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --script 'for i in $(seq $abc $xyz); do echo $i; done' --parameters abc=1 xyz=100000
az vmss run-command show -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --instance-view  # show command result

# run command for the second time
az vmss run-command update -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --script 'for i in $(seq $abc $xyz); do echo $i; done' --parameters abc=1 xyz=1000000 --output-blob-uri "https://aksclidebug.blob.core.windows.net/aksclidebug/abc?xxx"

# generate storage account container sas token
end=`date -u -d "30 minutes" '+%Y-%m-%dT%H:%MZ'`
az storage container generate-sas --account-name aksclidebug -n aksclidebug --permissions acrw --expiry $end --https-only

# run command for the third time
az vmss run-command update -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --script 'for i in $(seq $abc $xyz); do echo $i; done' --parameters abc=1 xyz=1000000 --output-blob-uri "https://aksclidebug.blob.core.windows.net/aksclidebug/xyz?xxx"
```

- asynchronous operation, could be executed multiple times via update command
- the output will be truncated, but it can be automatically exported to external storage in its entirety

## kubectl debug

### use busybox to debug

```bash
node_name=$(kubectl get no -o json | jq -r '.items[0].metadata.name')
kubectl debug no/${node_name} -i --image=mcr.microsoft.com/cbl-mariner/busybox:2.0
busybox_pod_name=$(kubectl get po -o json | jq '.items[]|select(.status.phase=="Running")|select(.spec.containers[0].image=="mcr.microsoft.com/cbl-mariner/busybox:2.0")|.metadata.name')
kubectl exec ${busybox_pod_name} -- nslookup google.com
```

### get journal log

```bash
node_name=$(kubectl get no -o json | jq -r '.items[0].metadata.name')
kubectl debug no/${node_name} -i --image=mcr.microsoft.com/cbl-mariner/base/core:2.0
debug_pod_name=$(kubectl get po -o json | jq '.items[]|select(.status.phase=="Running")|select(.spec.containers[0].image=="mcr.microsoft.com/cbl-mariner/base/core:2.0")|.metadata.name')
kubectl exec ${debug_pod_name} -- tdnf install systemd tar -y
kubectl exec ${debug_pod_name} -- chroot /host sh -c "journalctl > journal.log"
kubectl cp ${debug_pod_name}:/host/journal.log journal.log
```
