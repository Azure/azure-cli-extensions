az vmss run-command invoke -g MC_azcli-aks-dev_dev100_westus2 -n aks-nodepool1-28844989-vmss --command-id RunShellScript --instance-id 0 --scripts 'for i in $(seq $1 $2); do echo $i; done' --parameters 1 100000

az vmss run-command list -g  MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0"
az vmss run-command show -g MC_azcli-aks-dev_dev100_westus2 -n aks-nodepool1-28844989-vmss --instance-id 0 --name 

az vmss run-command create -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --script 'for i in $(seq $abc $xyz); do echo $i; done' --parameters abc=1 xyz=100000

az vmss run-command show -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --instance-view


az vmss run-command update -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --script 'for i in $(seq $abc $xyz); do echo $i; done' --parameters abc=1 xyz=1000000 --output-blob-uri "https://aksclidebug.blob.core.windows.net/aksclidebug/abc?xxx"


end=`date -u -d "30 minutes" '+%Y-%m-%dT%H:%MZ'`
# az storage blob generate-sas --account-name aksclidebug -n aksclidebug -c aksclidebug --permissions acrw --expiry $end --https-only
az storage container generate-sas --account-name aksclidebug -n aksclidebug --permissions acrw --expiry $end --https-only

az vmss run-command update -g MC_azcli-aks-dev_dev100_westus2 --vmss-name aks-nodepool1-28844989-vmss --instance-id "0" --run-command-name "t1" --script 'for i in $(seq $abc $xyz); do echo $i; done' --parameters abc=1 xyz=1000000 --output-blob-uri "https://aksclidebug.blob.core.windows.net/aksclidebug/xyz?xxx"

