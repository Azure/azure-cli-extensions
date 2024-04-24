# Azure CLI Amlfs Extension #
This is an extension to Azure CLI to manage Amlfs resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name amlfs
```

### Included Features ###
#### amlfs ####
##### Create #####
```
az amlfs create -n amlfs_name -g rg --sku AMLFS-Durable-Premium-250 --storage-capacity 16 --zones [1] --maintenance-window "{dayOfWeek:friday,timeOfDayUtc:'22:00'}" --filesystem-subnet subnet_id

```

##### Delete #####
```
az amlfs delete -n amlfs_name -g rg

```

##### List #####
```
az amlfs list -g rg

```

##### Show #####
```
az amlfs show -n name -g rg

```

##### Update #####
```
az amlfs update -n name -g rg --tags "{tag:test}"

```

##### Archive #####
```
az amlfs archive --amlfs-name name -g rg

```

##### Cancel archive #####
```
az amlfs cancel-archive --amlfs-name name -g rg

```

##### Check amlfs subnet #####
```
az amlfs check-amlfs-subnet --filesystem-subnet subnet_id --sku AMLFS-Durable-Premium-250 --location eastus --storage-capacity-tb 16

```

##### Get subnets size #####
```
az amlfs get-subnets-size --sku AMLFS-Durable-Premium-250 --storage-capacity-tb 16

```
