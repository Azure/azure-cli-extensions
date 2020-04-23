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
          --storage-account testadlsgen2 --file-system testfilesystem \\
          --sql-admin-login-user cliuser1 --sql-admin-login-password Password123! --location "East US"
"""

helps['synapse workspace list'] = """
type: command
short-summary: List all Synapse workspaces.
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
short-summary: Get a Synapse workspace.
examples:
  - name: Get a Synapse workspace.
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
short-summary: Delete a Synapse workspace.
examples:
  - name: Delete a Synapse workspace.
    text: |-
        az synapse workspace delete --name testsynapseworkspace --resource-group rg
"""

helps['synapse workspace check-name'] = """
type: command
short-summary: Check if a Synapse workspace name is available or not.
examples:
  - name: Check if a Synapse workspace name is available or not.
    text: |-
        az synapse workspace check-name --name testsynapseworkspace
"""

helps['synapse workspace wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of the workspace is met.
"""

helps['synapse spark'] = """
type: group
short-summary: Manage Spark pool and submit Spark Batch, Session, Statement.
"""

helps['synapse spark pool'] = """
type: group
short-summary: Manage Spark pools.
"""

helps['synapse spark pool create'] = """
type: command
short-summary: Create a Spark pool.
examples:
  - name: Create a Spark pool.
    text: |-
        az synapse spark pool create --name testpool --workspace-name testsynapseworkspace --resource-group rg \\
        --spark-version 2.4 --node-count 3
"""

helps['synapse spark pool list'] = """
type: command
short-summary: List all Spark pools.
examples:
  - name: List all Spark pools.
    text: |-
        az synapse spark pool list --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse spark pool show'] = """
type: command
short-summary: Get a specific Spark pool.
examples:
  - name: Get a specific Spark pools.
    text: |-
        az synapse spark pool show --name testpool --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse spark pool update'] = """
type: command
short-summary: Update the Spark pool.
examples:
  - name: Update the Spark pool's tags.
    text: |-
        az synapse spark pool update --name testpool --workspace-name testsynapseworkspace --resource-group rg \\
        --tags key1=value1
  - name: Update the Spark pool's auto scale configuration.
    text: |-
        az synapse spark pool update --name testpool --workspace-name testsynapseworkspace --resource-group rg \\
        --enable-auto-scale --min-node-count 3 --max-node-count 100
"""

helps['synapse spark pool delete'] = """
type: command
short-summary: Delete a Spark pool.
examples:
  - name: Delete a Spark pool.
    text: |-
        az synapse spark pool delete --name testpool --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse spark pool wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of a Spark pool is met.
"""

helps['synapse sql'] = """
type: group
short-summary: Manage SQL pools.
"""

helps['synapse sql pool'] = """
type: group
short-summary: Manage SQL pool including Create, Get, List, Delete, Pause, Resume SQL pool.
"""

helps['synapse sql pool create'] = """
type: command
short-summary: Create a SQL pool.
examples:
  - name: Create SQL pool.
    text: |-
        az synapse sql pool create --name sqlpoolcli1 --performance-level "DW1000c" \\
        --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse sql pool show'] = """
type: command
short-summary: Get a SQL pool.
examples:
  - name: Get SQL pool.
    text: |-
        az synapse sql pool show --name sqlpoolcli1 --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse sql pool list'] = """
type: command
short-summary: List all SQL pools.
examples:
  - name: List SQL pools.
    text: |-
        az synapse sql pool list --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse sql pool update'] = """
type: command
short-summary: Update SQL pool.
examples:
  - name: Update SQL pool.
    text: |-
        az synapse sql pool update --name sqlpoolcli1 --workspace-name testsynapseworkspace --resource-group rg \\
        --tags key1=value1
"""

helps['synapse sql pool pause'] = """
type: command
short-summary: Pause a SQL pool.
examples:
  - name: Pause SQL pool.
    text: |-
        az synapse sql pool pause --name sqlpoolcli1 --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse sql pool resume'] = """
type: command
short-summary: Resume a SQL pool.
examples:
  - name: Resume SQL pool.
    text: |-
        az synapse sql pool resume --name sqlpoolcli1 --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse sql pool delete'] = """
type: command
short-summary: Delete a SQL pool.
examples:
  - name: Delete SQL pool.
    text: |-
        az synapse sql pool delete --name sqlpoolcli1 --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse sql pool wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of a SQL pool is met.
"""

helps['synapse workspace firewall-rule'] = """
type: group
short-summary:  Manage a workspace's firewall rules.
"""

helps['synapse workspace firewall-rule create'] = """
type: command
short-summary: Create a firewall Rule.
examples:
  - name: Create a firewall Rule.
    text: |-
        az synapse workspace firewall-rule create --name allowAll --workspace-name testsynapseworkspace \\
        --resource-group rg --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
"""

helps['synapse workspace firewall-rule show'] = """
type: command
short-summary: Get a firewall rule.
examples:
  - name: Get a firewall rule.
    text: |-
        az synapse workspace firewall-rule show --name rule1 --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse workspace firewall-rule list'] = """
type: command
short-summary: List all firewall rules.
examples:
  - name: List all firewall rules.
    text: |-
        az synapse workspace firewall-rule list --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse workspace firewall-rule delete'] = """
type: command
short-summary: Delete a firewall rule.
examples:
  - name: Delete a firewall rule.
    text: |-
        az synapse workspace firewall-rule delete --name rule1 --workspace-name testsynapseworkspace --resource-group rg
"""

helps['synapse workspace firewall-rule wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of a Firewall Rule is met.
"""

helps['synapse spark batch'] = """
type: group
short-summary: Manage Synapse Spark batch jobs.
"""

helps['synapse spark batch create'] = """
type: command
short-summary: Submit spark batch job.
examples:
  - name: Submit a java spark batch job.
    text: |-
        az synapse spark batch create --name WordCount_Java --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool \\
        --main-definition-file abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/wordcount.jar \\
        --main-class-name WordCount \\
        --command-line-arguments abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/shakespeare.txt \\
        abfss://testfilesystem@testadlsgen2.dfs.core.windows.net/samples/java/wordcount/result/ \\
        --executors 2 --executor-size Small
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
examples:
  - name: Get a spark batch job under the specific spark pool with batch id.
    text: |-
        az synapse spark batch show --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark batch cancel'] = """
type: command
short-summary: Cancel a specific spark batch job under the specific spark pool.
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
short-summary: Submit a spark session job.
examples:
  - name: Submit a spark session job.
    text: |-
        az synapse spark session create --name testsession  --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool --executor-size Small --executors 4
"""

helps['synapse spark session list'] = """
type: command
short-summary: List all spark sessions.
examples:
  - name: List all spark sessions.
    text: |-
        az synapse spark session list --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session show'] = """
type: command
short-summary: Get a specific spark session job under the specific spark pool.
examples:
  - name: Get a spark session job under the specific spark pool with session id.
    text: |-
        az synapse spark session show --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session cancel'] = """
type: command
short-summary: Cancel a specific spark session.
examples:
  - name: Cancel a spark session.
    text: |-
        az synapse spark session cancel  --id 1 --workspace-name testsynapseworkspace --spark-pool-name testsparkpool
"""

helps['synapse spark session reset-timeout'] = """
type: command
short-summary: Reset the spark session timeout time.
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
short-summary: Submit a spark statement.
examples:
  - name: Submit a spark statement.
    text: |-
        az synapse spark session-statement create  --session-id 1 --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool --code "print('hello, Azure CLI')" --language pyspark
"""

helps['synapse spark session-statement show'] = """
type: command
short-summary: Get a spark statement.
examples:
  - name: Get a spark statement.
    text: |-
        az synapse spark session-statement show --id 1 --session-id 11 --workspace-name testsynapseworkspace \\
        --spark-pool-name testsparkpool
"""

helps['synapse spark session-statement list'] = """
type: command
short-summary: List all spark statements
examples:
  - name: List all spark statements.
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
