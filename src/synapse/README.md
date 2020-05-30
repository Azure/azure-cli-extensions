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

- Create a Synapse workspace
```bash
az synapse workspace create \
    --name fromcli4 \
    --resource-group rg \
    --storage-account testadlsgen2 \
    --file-system testfilesystem \
    --sql-admin-login-user cliuser1 \
    --sql-admin-login-password Password123! \
    --location "East US"
```
- Get a Synapse workspace
```bash
az synapse workspace show \
    --name testsynapseworkspace \
    --resource-group rg
```
- Update a Synapse workspace
```bash
az synapse workspace update \
    --name fromcli4 \
    --resource-group rg \
    --tags key1=value1 
```
- Delete a Synapse workspace
```bash
az synapse workspace delete \
    --name testsynapseworkspace \
    --resource-group rg
```
- List all Synapse workspaces
```bash
az synapse workspace list
```

```bash
az synapse workspace list \
    --resource-group rg
```
- Check if a Synapse workspace name is available or not
```bash
az synapse workspace check-name \
    --name testsynapseworkspace
```

#### Workapce fireall rule

Manage Synapse workspace's firewall rules

- Create a firewall rule
```bash
az synapse workspace firewall-rule create \
    --name allowAll \
    --workspace-name testsynapseworkspace \
    --resource-group rg \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 255.255.255.255
```
- Get a firewall rule
```bash
az synapse workspace firewall-rule show \
    --name rule1 \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- List all firewall rules
```bash
az synapse workspace firewall-rule list \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- Delete a firewall rule
```bash
az synapse workspace firewall-rule delete \
    --name rule1 \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```

#### Spark Pool

Manage Synapse Spark pools.

- Create a Spark pool
```bash
az synapse spark pool create \
    --name testpool \
    --resource-group rg \
    --workspace-name testsynapseworkspace \
    --spark-version 2.4 \
    --node-count 3 \
    --node-size Medium
```
- List all Spark pools
```bash
az synapse spark pool list \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- Get a Spark pool
```bash
az synapse spark pool show \
    --name testpool \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- Update Spark pool
```bash
az synapse spark pool update \
    --name testpool \
    --workspace-name testsynapseworkspace 
    --resource-group rg \
    --tags key1=value1
```
```bash
az synapse spark pool update \
    --name testpool \
    --workspace-name testsynapseworkspace 
    --resource-group rg \
    --enable-auto-scale \
    --min-node-count 3 \
    --max-node-count 100
```
- Delete a Spark pool
```bash
az synapse spark pool delete \
    --name testpool \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```

#### SQL Pool

Manage Synapse SQL pools

- Create s SQL pool

```bash
az synapse sql pool create \
    --name sqlpoolcli1 \
    --performance-level DW1000c \
    --resource-group rg \
    --workspace-name testsynapseworkspace
```
- Get a SQL pool
```bash
az synapse sql pool show \
    --name sqlpoolcli1 \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- List SQL pools
```bash
az synapse sql pool list \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- Update a SQL pool
```bash
az synapse sql pool update \
    --name sqlpoolcli1 \
    --workspace-name testsynapseworkspace 
    --resource-group rg \
    --tags key1=value1
```
- Pause a SQL pool
```bash
az synapse sql pool pause \
    --name sqlpoolcli1 \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```
- Resume a SQL pool
```bash
az synapse sql pool resume \
    --name sqlpoolcli1 \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```

- Delete a SQL pool

```bash
az synapse sql pool delete \
    --name sqlpoolcli1 \
    --workspace-name testsynapseworkspace \
    --resource-group rg
```

#### Spark Job

Manage Spark jobs.

- Submit a Spark java job.

```bash
az synapse spark job submit \
    --name WordCount_Java \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --main-definition-file abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/wordcount.jar \
    --main-class-name WordCount \
    --command-line-arguments abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/shakespeare.txt \
    abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/result/ \
    --executor-size Small \
    --executors 2
```

- Submit a spark dotnet job

```bash
az synapse spark job submit \
    --name WordCount_DotNet \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --language SparkDotNet \
    --main-defin
ition-file abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/dotnet/wordcount/wordcount.zip --main-class-name WordCount --command-line-arguments abfss://testfilesystem@testadlsgen2.dfs.co
re.windows.net/samples/dotnet/wordcount/shakespeare.txt abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/dotnet/wordcount/result --executors 2 --executor-size Medium
```

- Get a Spark job
```bash
az synapse spark job show \
    --livy-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- Cancel a Spark job
```bash
az synapse spark job cancel \
    --livy-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- List all Spark jobs
```bash
az synapse spark job list \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```
#### Spark Session

Manage Spark sessions.

- Create a Spark session

```bash
az synapse spark session create \
    --name testsession  \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --executor-size Small \
    --executors 4
```

- List all Spark sessions
```bash
az synapse spark session list \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- Get a Spark session
```bash
az synapse spark session show \
    --livy-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- Cancel a Spark session
```bash
az synapse spark session cancel  \
    --livy-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- Reset a Spark session's timeout time
```bash
az synapse spark session reset-timeout \
    --livy-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```


#### Spark Statement

Manage Spark session statements.

- Invoke a Spark statement

```bash
az synapse spark statement invoke \
    --session-id 1 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool \
    --code "print(\"hello, Azure CLI\")" \
    --language pyspark
```

- Get a Spark statement
```bash
az synapse spark statement show \
    --livy-id 1 \
    --session-id 11 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- List all Spark statements

```bash
az synapse spark statement list \
    --session-id 11 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```

- Cancel a Spark statement

```bash
az synapse spark statement cancel \
    --livy-id 1 \
    --session-id 11 \
    --workspace-name testsynapseworkspace \
    --spark-pool-name testsparkpool
```