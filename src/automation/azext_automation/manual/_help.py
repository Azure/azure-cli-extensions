# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps

helps['automation'] = """
    type: group
    short-summary: Manage Automation
"""

helps['automation account'] = """
    type: group
    short-summary: Automation Account
"""

helps['automation account list'] = """
    type: command
    short-summary: "Retrieve a list of accounts within a given resource group. And Retrieve a list of accounts within \
a given subscription."
    examples:
      - name: List automation accounts by resource group
        text: |-
               az automation account list --resource-group "rg"
      - name: List automation accounts by resource group
        text: |-
               az automation account list
"""

helps['automation account show'] = """
    type: command
    short-summary: "Get information about an Automation Account."
    examples:
      - name: Get automation account
        text: |-
               az automation account show --name "myAutomationAccount" --resource-group "rg"
"""

helps['automation account create'] = """
    type: command
    short-summary: "Create automation account."
    examples:
      - name: Create an automation account
        text: |-
               az automation account create --automation-account-name "myAutomationAccount" --location "East US 2" \
               --sku "Free" --resource-group "rg"
"""

helps['automation account update'] = """
    type: command
    short-summary: "Update an automation account."
    examples:
      - name: Update an automation account
        text: |-
               az automation account update --automation-account-name "myAutomationAccount" --tags KEY=VALUE \
               --resource-group "rg"
"""

helps['automation account delete'] = """
    type: command
    short-summary: "Delete an automation account."
    examples:
      - name: Delete automation account
        text: |-
               az automation account delete --name "myAutomationAccount" --resource-group "rg"
"""

helps['automation runbook'] = """
    type: group
    short-summary: Automation Runbook
"""

helps['automation runbook list'] = """
    type: command
    short-summary: "Retrieve a list of runbooks."
    examples:
      - name: List runbooks by automation account
        text: |-
               az automation runbook list --automation-account-name "myAutomationAccount" --resource-group "rg"
"""

helps['automation runbook show'] = """
    type: command
    short-summary: "Retrieve the runbook identified by runbook name."
    examples:
      - name: Get runbook
        text: |-
               az automation runbook show --automation-account-name "myAutomationAccount" --resource-group "rg" \
               --name "myRunbook"
"""

helps['automation runbook create'] = """
    type: command
    short-summary: "Create the runbook identified by runbook name."
    examples:
      - name: Create a runbook
        text: |-
               az automation runbook create --automation-account-name "myAutomationAccount" --resource-group "rg" \
               --name "myRunbook" --type "PowerShell" --location "East US 2"
"""

helps['automation runbook update'] = """
    type: command
    short-summary: "Update the runbook identified by runbook name."
    examples:
      - name: Update a runbook
        text: |-
               az automation runbook update --automation-account-name "myAutomationAccount" --description \
               "Runbook Description" --log-activity-trace 1 --log-progress true --log-verbose false \
               --resource-group "rg" --runbook-name "myRunbook"
"""

helps['automation runbook delete'] = """
    type: command
    short-summary: "Delete the runbook by name."
    examples:
      - name: Delete a runbook
        text: |-
               az automation runbook delete --automation-account-name "myAutomationAccount" --resource-group "rg" \
               --name "myRunbook"
"""

helps['automation runbook publish'] = """
    type: command
    short-summary: "Publish runbook draft."
    examples:
      - name: Publish runbook draft
        text: |-
               az automation runbook publish --automation-account-name "myAutomationAccount" --resource-group \
               "rg" --name "myRunbook"
"""

helps['automation runbook wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the automation runbook is met.
    examples:
      - name: Pause executing next line of CLI script until the automation runbook is successfully created.
        text: |-
               az automation runbook wait --automation-account-name "myAutomationAccount" --resource-group "rg" \
               --name "myRunbook" --created
"""

helps['automation runbook start'] = """
    type: command
    short-summary: "Start the runbook"
    examples:
      - name: Start the runbook
        text: |-
               az automation runbook start --automation-account-name "myAutomationAccount" --resource-group "rg" \
               --name "myRunbook"
"""

helps['automation runbook replace-content'] = """
    type: command
    short-summary: "Replace content of the runbook"
    examples:
      - name: Replace content of the runbook
        text: |-
               az automation runbook replace-content --automation-account-name "myAutomationAccount" --resource-group \
               "rg" --name "myRunbook" --content @/path/to/script
"""

helps['automation runbook revert-to-published'] = """
    type: command
    short-summary: "Revert the runbook content to last known published state"
    examples:
      - name: Replace content of the runbook
        text: |-
               az automation runbook revert-to-published --automation-account-name "myAutomationAccount" \
               --resource-group "rg" --name "myRunbook"
"""

helps['automation job'] = """
    type: group
    short-summary: Automation Job
"""

helps['automation job list'] = """
    type: command
    short-summary: "Retrieve a list of jobs."
    examples:
      - name: List jobs by automation account
        text: |-
               az automation job list --automation-account-name "myAutomationAccount" --resource-group "rg"
"""

helps['automation job show'] = """
    type: command
    short-summary: "Retrieve the job identified by job name."
    examples:
      - name: Get job
        text: |-
               az automation job show --automation-account-name "myAutomationAccount" --name "foo" --resource-group "rg"
"""

helps['automation job resume'] = """
    type: command
    short-summary: "Resume the job identified by jobName."
    examples:
      - name: Resume job
        text: |-
               az automation job resume --automation-account-name "myAutomationAccount" --name "foo" \
               --resource-group "rg"
"""

helps['automation job stop'] = """
    type: command
    short-summary: "Stop the job identified by jobName."
    examples:
      - name: Stop job
        text: |-
               az automation job stop --automation-account-name "myAutomationAccount" --name "foo" --resource-group "rg"
"""

helps['automation job suspend'] = """
    type: command
    short-summary: "Suspend the job identified by job name."
    examples:
      - name: Suspend job
        text: |-
               az automation job suspend --automation-account-name "myAutomationAccount" --name "foo" \
               --resource-group "rg"
"""

helps['automation schedule'] = """
    type: group
    short-summary: Automation Schedule
"""

helps['automation schedule list'] = """
    type: command
    short-summary: "Retrieve a list of schedules."
    examples:
      - name: List schedules by automation account
        text: |-
               az automation schedule list --automation-account-name "myAutomationAccount" --resource-group "rg"
"""

helps['automation schedule show'] = """
    type: command
    short-summary: "Retrieve the schedule identified by schedule name."
    examples:
      - name: Get schedule
        text: |-
               az automation schedule show --automation-account-name "myAutomationAccount" --resource-group "rg" \
               --name "mySchedule"
"""

helps['automation schedule create'] = """
    type: command
    short-summary: "Create automation schedule."
    examples:
      - name: Create an automation schedule
        text: |-
               az automation schedule create --automation-account-name "myAutomationAccount"  --resource-group "rg" \
               -n mySchedule --frequency Hour --interval 1 --start-time 2022-08-10 18:00:00 --time-zone UTC+08:00

"""

helps['automation schedule update'] = """
    type: command
    short-summary: "Update an automation schedule."
    examples:
      - name: Update an automation schedule
        text: |-
               az automation schedule update --automation-account-name "myAutomationAccount" --description test \
               -n mySchedule --resource-group "rg" --is-enabled false
"""

helps['automation schedule delete'] = """
    type: command
    short-summary: "Delete an automation schedule."
    examples:
      - name: Delete automation schedule
        text: |-
               az automation schedule delete --name "myAutomationSchedule" --resource-group "rg" \
               --automation-account-name "myAutomationAccount"
"""

helps['automation software-update-configuration'] = """
    type: group
    short-summary: Automation software-update-configuration
"""

helps['automation software-update-configuration list'] = """
    type: command
    short-summary: "List all software-update-configurations for the account."
    examples:
      - name: List software-update-configurations by automation account
        text: |-
               az automation software-update-configuration list --automation-account-name "myAutomationAccount" \
                --resource-group "rg"
"""

helps['automation software-update-configuration show'] = """
    type: command
    short-summary: "Get a single software-update-configuration by name."
    examples:
      - name: Get software-update-configuration
        text: |-
               az automation software-update-configuration show --automation-account-name "myAutomationAccount" \
               --resource-group "rg" --name "mySoftwareUpdateConfiguration"
"""

helps['automation software-update-configuration create'] = """
    type: command
    short-summary: "Create automation software-update-configuration."
    examples:
      - name: Create an automation software-update-configuration
        text: |-
               az automation software-update-configuration create --automation-account-name "myAutomationAccount" \
                 --resource-group "rg" -n mySoftwareUpdateConfiguration --frequency Hour --interval 1 \
                 --operating-system windows --excluded-kb-numbers 16800,16800 -n confgname \
                 --included-update-classifications Critical --duration pT2H0M --azure-virtual-machines \
                 /subscriptions/{subid}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/myVM
"""

helps['automation software-update-configuration delete'] = """
    type: command
    short-summary: "Delete an automation software-update-configuration."
    examples:
      - name: Delete automation software-update-configuration
        text: |-
               az automation software-update-configuration delete --name "mySoftwareUpdateConfiguration" \
               --resource-group "rg" --automation-account-name "myAutomationAccount"
"""

helps['automation software-update-configuration runs'] = """
    type: group
    short-summary: "Software Update Configuration Runs."
"""

helps['automation software-update-configuration runs list'] = """
    type: command
    short-summary: "Return list of software update configuration runs."
    examples:
      - name: List software-update-configurations by automation account
        text: |-
               az automation software-update-configuration runs list --automation-account-name "myAutomationAccount" \
                --resource-group "rg"
"""

helps['automation software-update-configuration runs show'] = """
    type: command
    short-summary: "Get a single software update configuration runs by Id."
    examples:
      - name: List software-update-configurations runs by Id
        text: |-
               az automation software-update-configuration runs show --automation-account-name \
               "myAutomationAccount" --resource-group "rg" --software-update-configuration-run-id \
               "MyconfigurationRunId"
"""
helps['automation software-update-configuration machine-runs'] = """
    type: group
    short-summary: "Software Update Configuration Machine Runs."
"""

helps['automation software-update-configuration machine-runs list'] = """
    type: command
    short-summary: "List software update configuration machine-runs."
    examples:
      - name: List software-update-configurations machine-runs by automation account
        text: |-
               az automation software-update-configuration machine-runs list --automation-account-name \
               "myAutomationAccount" --resource-group "rg"
"""

helps['automation software-update-configuration machine-runs show'] = """
    type: command
    short-summary: "Get a single software update configuration machine runs by Id."
    examples:
      - name: List software-update-configurations machine-runs by Id
        text: |-
               az automation software-update-configuration machine-runs show --automation-account-name \
               "myAutomationAccount" --resource-group "rg" --software-update-configuration-machine-run-id \
               "MyconfigurationMachineRunId"
"""
