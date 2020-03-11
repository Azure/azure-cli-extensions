# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

# pylint: disable=line-too-long, too-many-lines


helps['synapse'] = """
type: group
short-summary: Manage and operate Synapse Workspace, Spark Pool, SQL Pool.
"""

helps['synapse workspace'] = """
type: group
short-summary: Manage Synapse Workspace.
"""

helps['synapse workspace create'] = """
type: command
short-summary: Create a Synapse workspace.
examples:
  - name: Create a Synapse workspace
    text: |-
        az synapse workspace create --name fromcli4 --resource-group rg \\
          --account-url https://testadlsgen2.dfs.core.windows.net --file-system testfilesystem \\
          --sql-admin-login-user cliuser1 --sql-admin-login-password Password123! --location "East US"
"""

helps['synapse workspace list'] = """
type: command
short-summary: List all Synapse workspaces under a subscription or under a specific resource group.
examples:
  - name: List all Synapse workspaces under a subscription
    text: |-
        az synapse workspace list
  - name: List all Synapse workspaces under a specific resource group
    text: |-
        az synapse workspace list --resource-group rg
"""

helps['synapse workspace show'] = """
type: command
short-summary: Get a Synapse workspaces with workspace name.
examples:
  - name: Get a Synapse workspaces with workspace name.
    text: |-
        az synapse workspace show --name testsynapseworkspace --resource-group rg
"""

helps['synapse workspace update'] = """
type: command
short-summary: Update a Synapse workspace.
examples:
  - name: Update a Synapse workspace
    text: |-
        az synapse workspace update --name fromcli4 --resource-group rg \\
          --tags key1=value1
"""

helps['synapse workspace delete'] = """
type: command
short-summary: Delete a Synapse workspaces with workspace name.
examples:
  - name: Delete a Synapse workspaces with workspace name.
    text: |-
        az synapse workspace delete --name testsynapseworkspace --resource-group rg
"""

helps['synapse workspace wait'] = """
type: command
short-summary: Place the CLI in a waiting state a condition of a workspace is met.
"""

helps['synapse spark'] = """
type: group
short-summary: Manage Spark pool and submit Spark Batch, Session, Statement job.
"""

helps['synapse spark pool'] = """
type: group
short-summary: Manage Spark pool including Create, Get, List, Delete Spark pool.
"""

helps['synapse spark pool create'] = """
type: command
short-summary: Create a Spark pool.
long-summary: Create a Spark pool with default configuration.
examples:
  - name: Create a Spark pool.
    text: |-
        az synapse spark pool create --name testpool --resource-group rg --workspace-name \\
        testsynapseworkspace --location "East US" --spark-version 2.4
"""

helps['synapse spark pool list'] = """
type: command
short-summary: List all Spark pools.
long-summary: List all Spark pools under a workspace.
examples:
  - name: List all Spark pools under a workspace.
    text: |-
        az synapse spark pool list --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse spark pool show'] = """
type: command
short-summary: Get a specific Spark pool with Spark pool name.
examples:
  - name: Get a specific Spark pools with Spark pool name.
    text: |-
        az synapse spark pool show --name testpool  --workspace-name testsynapseworkspace \\
        --resource-group rg
"""

helps['synapse spark pool update'] = """
type: command
short-summary: Update the Spark pool's tags.
examples:
  - name: Update the Spark pool's tags.
    text: |-
        az synapse spark pool update --name testpool  --workspace-name testsynapseworkspace --resource-group rg \\
        --tags key1=value1
"""

helps['synapse spark pool delete'] = """
type: command
short-summary: Delete a specific Spark pool with Spark pool name.
examples:
  - name: Delete a specific big Spark pool with Spark pool name.
    text: |-
        az synapse spark pool delete --name testpool --workspace-name testsynapseworkspace \\
        --resource-group rg
"""

helps['synapse spark pool wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of a Spark pool is met.
"""

helps['synapse sql'] = """
type: group
short-summary: Manage SQL pool.
"""

helps['synapse sql pool'] = """
type: group
short-summary: Manage SQL pool including Create, Get, List, Delete, Pause, Resume SQL pool.
"""

helps['synapse sql pool create'] = """
type: command
short-summary: Create a SQL pool.
long-summary: Create a SQL pool with default configuration.
examples:
  - name: Create SQL pool.
    text: |-
        az synapse sql pool create --name sqlpoolcli1 --sku-name "DW1000c" --resource-group rg --workspace-name \\
        testsynapseworkspace --location "East US"
"""

helps['synapse sql pool show'] = """
type: command
short-summary: Get a SQL pool.
long-summary: Get a SQL pool with SQL pool name.
examples:
  - name: Get SQL pool.
    text: |-
        az synapse sql pool show --name sqlpoolcli1 --resource-group rg --workspace-name \\
        testsynapseworkspace
"""

helps['synapse sql pool list'] = """
type: command
short-summary: List all SQL pools.
long-summary: List all SQL pools under a specific workspace.
examples:
  - name: List SQL pools.
    text: |-
        az synapse sql pool list --resource-group rg \\
        --workspace-name testsynapseworkspace
"""

helps['synapse sql pool pause'] = """
type: command
short-summary: Pause a SQL pool.
long-summary: Pause a SQL pool with SQL pool name.
examples:
  - name: Pause SQL pool.
    text: |-
        az synapse sql pool pause --name sqlpoolcli1 --resource-group rg --workspace-name \\
        testsynapseworkspace
"""

helps['synapse sql pool resume'] = """
type: command
short-summary: Resume a SQL pool.
long-summary: Resume a SQL pool with SQL pool name.
examples:
  - name: Resume SQL pool.
    text: |-
        az synapse sql pool resume --name sqlpoolcli1 --resource-group rg --workspace-name \\
        testsynapseworkspace
"""

helps['synapse sql pool delete'] = """
type: command
short-summary: Delete a SQL pool.
long-summary: Delete a SQL pool with SQL pool name.
examples:
  - name: Delete SQL pool.
    text: |-
        az synapse sql pool delete --name sqlpoolcli1 --resource-group rg --workspace-name \\
        testsynapseworkspace
"""

helps['synapse sql pool wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of a SQL pool is met.
"""

helps['synapse spark batch'] = """
type: group
short-summary: Manage Synapse Spark batch jobs.
"""

helps['synapse spark batch create'] = """
type: command
short-summary: Submit spark batch job.
long-summary: Submit a spark batch job to a specific spark pool.
examples:
  - name: Submit a java spark batch job to a specific spark pool.
    text: |-
        az synapse spark batch create --name WordCount_Java --workspace-name testsynapseworkspace \\
          --spark-pool-name testsparkpool \\
          --file abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/wordcount.jar \\
          --class-name WordCount \\
          --args abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/shakespeare.txt \\
          abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/result/ \\
          --driver-memory 4g --driver-cores 4 --executor-memory 4g --executor-cores 4 --num-executors 2
"""

helps['synapse spark batch list'] = """
type: command
short-summary: List all spark batch jobs under the specific spark pool.
examples:
  - name: List all spark batch job under the specific spark pool.
    text: |-
        az synapse spark batch list --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark batch show'] = """
type: command
short-summary: Get a specific spark batch job under the specific spark pool.
long-summary: Get the spark batch job under the specific spark pool with batch id.
examples:
  - name: Get a spark batch job under the specific spark pool with batch id.
    text: |-
        az synapse spark batch show --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark batch cancel'] = """
type: command
short-summary: Cancel a specific spark batch job under the specific spark pool.
long-summary: Cancel the spark batch job under the specific spark pool with batch id.
examples:
  - name: Cancel a spark batch job under the specific spark pool with batch id.
    text: |-
        az synapse spark batch cancel  --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session'] = """
type: group
short-summary: Manage Synapse Spark Session jobs and reset the Spark Session timeout.
"""

helps['synapse spark session create'] = """
type: command
short-summary: Submit a spark session job
long-summary: Submit a spark session job to a specific spark pool.
examples:
  - name: Submit a spark session job under the specific spark pool.
    text: |-
        az synapse spark session create --name testsession  --workspace-name testsynapseworkspace --spark-pool-name testsparkpool \\
        --driver-memory 4g --driver-cores 4 \\
        --executor-memory 4g --executor-cores 4 --num-executors 2
"""

helps['synapse spark session list'] = """
type: command
short-summary: List all spark session jobs under the specific spark pool.
examples:
  - name: List all spark session jobs under the specific spark pool.
    text: |-
        az synapse spark session list --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session show'] = """
type: command
short-summary: Get a specific spark session job under the specific spark pool.
long-summary: Get the spark session job under the specific spark pool with session id.
examples:
  - name: Get a spark session job under the specific spark pool with session id.
    text: |-
        az synapse spark session show --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session cancel'] = """
type: command
short-summary: Cancel a specific spark session job under the specific spark pool.
long-summary: Cancel the spark session job under the specific spark pool with session id.
examples:
  - name: Cancel a spark session job under the specific spark pool with session id.
    text: |-
        az synapse spark session cancel  --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session reset-timeout'] = """
type: command
short-summary: Reset the spark session timeout time.
long-summary: Reset the spark session timeout time under the specific spark pool with session id.
examples:
  - name: Reset the spark session timeout time.
    text: |-
        az synapse spark session reset-timeout --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session-statement'] = """
type: group
short-summary: Manage Synapse Spark Session Statements.
"""

helps['synapse spark session-statement create'] = """
type: command
short-summary: Submit a spark statement to a spark session.
examples:
  - name: Submit a spark statement to a spark session.
    text: |-
        az synapse spark session-statement create  --session-id 1 --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool --code "print('hello, Azure CLI')" --kind pyspark
"""

helps['synapse spark session-statement show'] = """
type: command
short-summary: Get a spark statement with statement id.
examples:
  - name: Get a spark statement with statement id.
    text: |-
        az synapse spark session-statement show --id 1 --session-id 11 --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool
"""

helps['synapse spark session-statement list'] = """
type: command
short-summary: List all spark statements under the specify spark session.
examples:
  - name: List all spark statements under the specify spark session.
    text: |-
        az synapse spark session-statement list --session-id 11 --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool
"""

helps['synapse spark session-statement cancel'] = """
type: command
short-summary: Cancel a spark statement with statement id.
examples:
  - name: Cancel a spark statement with statement id.
    text: |-
        az synapse spark session-statement cancel --id 1 --session-id 11 --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool
"""
