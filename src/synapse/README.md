# Microsoft Azure CLI Synapse Extension #
This is a extension for Synapse features.

### How to use ###

Install this extension using the below CLI command

```bash
az extension add --name synapse
```

### Included Features

#### Workspace

Manage Synapse Workspaces.

*Examples:*

```bash
az synapse workspace create \
    --name fromcli4 \
    --resource-group rg \
    --account-url https://testadlsgen2.dfs.core.windows.net \
    --file-system testfilesystem \
    --sql-admin-login-user cliuser1 \
    --sql-admin-login-password Password123! \
    --location "East US"
```

#### Spark Pool

Manage Synapse Spark pools.

*Examples:*

```bash
az synapse spark pool create \
    --name testpool \
    --resource-group rg \
    --workspace-name testsynapseworkspace \
    --location "East US"
```

#### Sql Pool

Manage Synapse Sql Pools

*Examples:*

```bash
az synapse sql pool create \
    --name sqlpoolcli1 \
    --sku-name DW1000c \
    --resource-group rg \
    --workspace-name testsynapseworkspace \
    --location "East US"
```

#### Spark Batch Job

Manage Spark batch jobs.

*Examples:*

```bash
az synapse spark batch create \
    --name WordCount_Java \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --file abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/wordcount.jar \
    --class-name WordCount \
    --args abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/shakespeare.txt \
    abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/result/ \
    --driver-memory 4g \
    --driver-cores 4 \
    --executor-memory 4g \
    --executor-cores 4 \
    --num-executors 2
```

#### Spark Session Job

Manage Spark session jobs.

*Examples:*

```bash
az synapse spark session create \
    --name testsession  \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --driver-memory 4g \
    --driver-cores 4 \
    --executor-memory 4g \
    --executor-cores 4 \
    --num-executors 2
```

#### Spark Session Statement

Manage Spark session statements.

*Examples:*

```bash
az synapse spark session-statement create \
    --session-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --code "print(\"hello, Azure CLI\")" \
    --kind pyspark
```