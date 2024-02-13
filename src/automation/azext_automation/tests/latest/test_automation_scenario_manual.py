# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from unittest import mock
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import tempfile
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

RUNBOOK_CONTENT = '''
<#
    .DESCRIPTION
        An example runbook which gets all the ARM resources using the Run As Account (Service Principal)

    .NOTES
        AUTHOR: Azure Automation Team
        LASTEDIT: Mar 14, 2016
#>

$connectionName = "AzureRunAsConnection"
try
{
    # Get the connection "AzureRunAsConnection "
    $servicePrincipalConnection=Get-AutomationConnection -Name $connectionName

    "Logging in to Azure..."
    Add-AzureRmAccount `
        -ServicePrincipal `
        -TenantId $servicePrincipalConnection.TenantId `
        -ApplicationId $servicePrincipalConnection.ApplicationId `
        -CertificateThumbprint $servicePrincipalConnection.CertificateThumbprint
}
catch {
    if (!$servicePrincipalConnection)
    {
        $ErrorMessage = "Connection $connectionName not found."
        throw $ErrorMessage
    } else{
        Write-Error -Message $_.Exception
        throw $_.Exception
    }
}

#Get all ARM resources from all resource groups
$ResourceGroups = Get-AzureRmResourceGroup

foreach ($ResourceGroup in $ResourceGroups)
{
    Write-Output ("Showing resources in resource group " + $ResourceGroup.ResourceGroupName)
    $Resources = Find-AzureRmResource -ResourceGroupNameContains $ResourceGroup.ResourceGroupName | Select ResourceName, ResourceType
    ForEach ($Resource in $Resources)
    {
        Write-Output ($Resource.ResourceName + " of type " +  $Resource.ResourceType)
    }
    Write-Output ("")
}
'''


def _uuid():
    return 'ef6919bf-b827-4b18-8475-8d4a03a49d0e'


class AutomationScenarioTest(ScenarioTest):
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_automation_', key='rg', location='westus2')
    def test_automation(self, resource_group):
        self.kwargs.update({
            'account_name': self.create_random_name(prefix='test-account-', length=24),
            'runbook_name': self.create_random_name(prefix='test-runbook-', length=24),
            'runbook_content': RUNBOOK_CONTENT,
            'hybrid_runbook_worker_group_name' : self.create_random_name(prefix='hwg-', length=10),
            'python3Package_name': self.create_random_name(prefix='py3-package-', length=24),
            'python3PackageContentUri':'uri=https://files.pythonhosted.org/packages/7f/e2/85dfb9f7364cbd7a9213caea0e91fc948da3c912a2b222a3e43bc9cc6432/requires.io-0.2.6-py2.py3-none-any.whl'
        })
        self.cmd('automation account create --resource-group {rg} --name {account_name} --location "West US 2"',
                 checks=[self.check('name', '{account_name}')])
        self.cmd('automation account update --resource-group {rg} --name {account_name} --tags A=a', checks=[
            self.check('name', '{account_name}'),
            self.check('tags.A', 'a')
        ])
        self.cmd('automation account show --resource-group {rg} --name {account_name}', checks=[
            self.check('name', '{account_name}'),
        ])
        self.cmd('automation account list --resource-group {rg}', checks=[
            self.check('length(@)', 1)
        ])

        self.cmd('automation runbook create --resource-group {rg} --automation-account-name {account_name} '
                 '--name {runbook_name} --type PowerShell --location "West US 2"',
                 checks=[self.check('name', '{runbook_name}'),
                         self.check('runbookType', 'PowerShell')])
        self.cmd('automation runbook update --resource-group {rg} --automation-account-name {account_name} '
                 '--name {runbook_name} --log-activity-trace 1 --log-verbose true --log-progress true',
                 checks=[self.check('name', '{runbook_name}'),
                         self.check('logActivityTrace', '1'),
                         self.check('logProgress', True),
                         self.check('logVerbose', True)])

        tempdir = os.path.realpath(tempfile.gettempdir())
        script_path = os.path.join(tempdir, 'PowerShell.ps')
        with open(script_path, 'w') as fp:
            fp.write(RUNBOOK_CONTENT)
        self.kwargs.update({
            'script_path': script_path
        })
        self.cmd('automation runbook replace-content --resource-group {rg} --automation-account-name {account_name} '
                 '--name {runbook_name} --content @{script_path}')
        self.cmd('automation runbook publish --resource-group {rg} --automation-account-name {account_name} '
                 '--name {runbook_name}')

        self.cmd('automation hrwg create --resource-group {rg} --automation-account-name {account_name} --name {hybrid_runbook_worker_group_name}',
        checks=[self.check('name', '{hybrid_runbook_worker_group_name}')])

        self.cmd('automation hrwg create --resource-group {rg} --automation-account-name {account_name} --name {hybrid_runbook_worker_group_name}',
        checks=[self.check('name', '{hybrid_runbook_worker_group_name}')])

        self.cmd('automation hrwg show --resource-group {rg} --automation-account-name {account_name} --name {hybrid_runbook_worker_group_name}',
        checks=[self.check('name', '{hybrid_runbook_worker_group_name}')])

        self.cmd('automation hrwg list --resource-group {rg} --automation-account-name {account_name}',
        checks=[self.check('length(@)', 1)])

        self.cmd('automation hrwg hrw list --automation-account-name {account_name} --hybrid-runbook-worker-group-name {hybrid_runbook_worker_group_name} -g {rg}',
        checks=[self.check('length(@)', 0)])

        self.cmd('automation hrwg delete --resource-group {rg} --automation-account-name {account_name} --name {hybrid_runbook_worker_group_name} --yes')

        self.cmd('automation python3-package  create --resource-group {rg} --automation-account-name {account_name} --name {python3Package_name} --content-link {python3PackageContentUri}',
        checks=[self.check('name', '{python3Package_name}')])

        self.cmd('automation python3-package  update --resource-group {rg} --automation-account-name {account_name} --name {python3Package_name} --content-link {python3PackageContentUri}',
        checks=[self.check('name', '{python3Package_name}')])

        self.cmd('automation python3-package  show --resource-group {rg} --automation-account-name {account_name} --name {python3Package_name}',
        checks=[self.check('name', '{python3Package_name}')])

        self.cmd('automation python3-package  list --resource-group {rg} --automation-account-name {account_name} ',
        checks=[self.check('length(@)', 1)])

        self.cmd('automation python3-package delete --resource-group {rg} --automation-account-name {account_name} --name {python3Package_name} --yes')

        with mock.patch('azext_automation.manual.custom._uuid', side_effect=_uuid):
            job = self.cmd('automation runbook start --resource-group {rg} --automation-account-name {account_name} '
                           '--name {runbook_name}').get_output_in_json()

            self.kwargs.update({
                'job_name': job['name']
            })
            self.cmd('automation job list --resource-group {rg} --automation-account-name {account_name}', checks=[
                self.check('length(@)', 1)
            ])
            self.cmd('automation job show --resource-group {rg} --automation-account-name {account_name} '
                     '--name {job_name}', checks=[self.check('name', '{job_name}')])
            self.cmd('automation runbook show --resource-group {rg} --automation-account-name {account_name} '
                     '--name {runbook_name}', checks=[self.check('name', '{runbook_name}')])
            self.cmd('automation runbook list --resource-group {rg} --automation-account-name {account_name} ', checks=[
                self.check('length(@)', 1)
            ])
            self.cmd('automation runbook delete --resource-group {rg} --automation-account-name {account_name} '
                     '--name {runbook_name} -y')

        self.cmd('automation account delete --resource-group {rg} --name {account_name} -y')

    @ResourceGroupPreparer(name_prefix='cli_test_automation_schedule', key='rg', location='westus2')
    @AllowLargeResponse()
    def test_automation_schedule(self, resource_group):
        self.kwargs.update({
            'account_name': self.create_random_name('account-', 15),
            'schedule_name': self.create_random_name('schedule-', 15),
            'start_time': '2023-03-01 15:38:00',
        })

        self.cmd('automation account create -n {account_name} -g {rg} --location "West US 2"')
        self.cmd('automation schedule create -n {schedule_name} -g {rg} --automation-account-name {account_name} --description test --frequency Hour --interval 1 --start-time {start_time} --time-zone UTC+08:00', checks=[
            self.check('frequency', 'Hour'),
            self.check('interval', '1'),
            self.check('startTime', '2023-03-01T15:38:00+08:00'),
            self.check('timeZone', 'UTC+08:00'),
            self.check('description', 'test'),
            self.check('isEnabled', True)
        ])
        self.cmd('automation schedule update -n {schedule_name} -g {rg} --automation-account-name {account_name} --description test1 --is-enabled false', checks=[
            self.check('frequency', 'Hour'),
            self.check('interval', '1'),
            self.check('startTime', '2023-03-01T15:38:00+08:00'),
            self.check('timeZone', 'UTC+08:00'),
            self.check('description', 'test1'),
            self.check('isEnabled', False)
        ])
        self.cmd('automation schedule list -g {rg} --automation-account-name {account_name} ', checks=[
            self.check('[0].frequency', 'Hour'),
            self.check('[0].interval', '1'),
            self.check('[0].startTime', '2023-03-01T15:38:00+08:00'),
            self.check('[0].timeZone', 'UTC+08:00'),
            self.check('[0].description', 'test1'),
            self.check('[0].isEnabled', False)
        ])
        self.cmd('automation schedule show -n {schedule_name} -g {rg} --automation-account-name {account_name} ', checks=[
            self.check('frequency', 'Hour'),
            self.check('interval', '1'),
            self.check('startTime', '2023-03-01T15:38:00+08:00'),
            self.check('timeZone', 'UTC+08:00'),
            self.check('description', 'test1'),
            self.check('isEnabled', False),
        ])
        self.cmd('automation schedule delete -n {schedule_name} -g {rg} --automation-account-name {account_name} -y')

    @ResourceGroupPreparer(name_prefix='cli_test_automation_software_update_configuration', key='rg', location='westus2')
    @AllowLargeResponse()
    def test_automation_software_update_configuration(self, resource_group):
        self.kwargs.update({
            'account_name': self.create_random_name('account-', 15),
            'conf_name': self.create_random_name('conf-', 15),
            'vm_name':self.create_random_name('vm-', 15),
        })

        sub = '/subscriptions/' + self.get_subscription_id()
        vm_id = self.cmd('vm create -n {vm_name} -g {rg} --image Canonical:UbuntuServer:18.04-LTS:latest --generate-ssh-key --nsg-rule NONE --location "West US 2"').get_output_in_json()['id']
        self.kwargs.update({
            'vm_id': vm_id,
            'sub': sub,
            'start_time': '2023-03-22 18:00:00',
            'expiry_time': '2023-03-29 18:00:00',
            'next_run': '2023-03-25 18:00:00',
        })
        self.cmd('automation account create -n {account_name} -g {rg} --location "West US 2"')
        self.cmd('automation software-update-configuration create -n {conf_name} -g {rg} --automation-account-name {account_name} --description test --frequency Hour --interval 1 --operating-system windows --excluded-kb-numbers 16800 16800 --included-kb-numbers 15000 15000 --included-update-classifications Critical --duration pT2H0M --azure-virtual-machines {vm_id} --time-zone UTC+08:00 --start-time {start_time} --expiry-time {expiry_time} --next-run {expiry_time} --non-azure-computer-names nonvm1 nonvm2 --reboot-setting IfRequired --azure-queries-scope {sub} --azure-queries-location eastus westus --azure-queries-tags tag1 tag2', checks=[
            self.check('name', '{conf_name}'),
            self.check('scheduleInfo.description', 'test'),
            self.check('scheduleInfo.frequency', 'Hour'),
            self.check('scheduleInfo.interval', '1'),
            self.check('scheduleInfo.startTime', '2023-03-22T10:00:00+08:00'),
            self.check('scheduleInfo.timeZone', 'UTC+08:00'),
            self.check('scheduleInfo.description', 'test'),
            self.check('scheduleInfo.isEnabled', True),
            self.check('updateConfiguration.azureVirtualMachines', [vm_id]),
            self.check('updateConfiguration.duration', '2:00:00'),
            self.check('updateConfiguration.nonAzureComputerNames', ['nonvm1', 'nonvm2']),
            self.check('updateConfiguration.operatingSystem', 'Windows'),
            self.check('updateConfiguration.targets.azureQueries[0].locations', ['eastus', 'westus']),
            self.check('updateConfiguration.targets.azureQueries[0].scope', [sub]),
            self.check('updateConfiguration.targets.azureQueries[0].tagSettings.tags.tag',  ['tag1','tag2']),
            self.check('updateConfiguration.windows.excludedKbNumbers', ['16800', '16800']),
            self.check('updateConfiguration.windows.includedKbNumbers', ['15000', '15000']),
            self.check('updateConfiguration.windows.includedUpdateClassifications', 'Critical'),
            self.check('updateConfiguration.windows.rebootSetting', 'IfRequired')
        ])
        self.cmd('automation software-update-configuration list -g {rg} --automation-account-name {account_name}', checks=[
            self.check('value[0].name', '{conf_name}'),
            self.check('value[0].updateConfiguration.azureVirtualMachines', [vm_id]),
            self.check('value[0].updateConfiguration.duration', '2:00:00'),
            self.check('value[0].updateConfiguration.nonAzureComputerNames', ['nonvm1', 'nonvm2']),
            self.check('value[0].updateConfiguration.operatingSystem', 'Windows'),
            self.check('value[0].updateConfiguration.targets.azureQueries[0].locations', ['eastus', 'westus']),
            self.check('value[0].updateConfiguration.targets.azureQueries[0].scope', [sub]),
            self.check('value[0].updateConfiguration.targets.azureQueries[0].tagSettings.tags.tag', ['tag1', 'tag2']),
            self.check('value[0].updateConfiguration.windows.excludedKbNumbers', ['16800', '16800']),
            self.check('value[0].updateConfiguration.windows.includedKbNumbers', ['15000', '15000']),
            self.check('value[0].updateConfiguration.windows.includedUpdateClassifications', 'Critical'),
            self.check('value[0].updateConfiguration.windows.rebootSetting', 'IfRequired')
        ])
        self.cmd('automation software-update-configuration show -n {conf_name} -g {rg} --automation-account-name {account_name} -n {conf_name}', checks=[
            self.check('name', '{conf_name}'),
            self.check('scheduleInfo.description', 'test'),
            self.check('scheduleInfo.frequency', 'Hour'),
            self.check('scheduleInfo.interval', '1'),
            self.check('scheduleInfo.startTime', '2023-03-22T10:00:00+08:00'),
            self.check('scheduleInfo.timeZone', 'UTC+08:00'),
            self.check('scheduleInfo.description', 'test'),
            self.check('scheduleInfo.isEnabled', True),
            self.check('updateConfiguration.azureVirtualMachines', [vm_id]),
            self.check('updateConfiguration.duration', '2:00:00'),
            self.check('updateConfiguration.nonAzureComputerNames', ['nonvm1', 'nonvm2']),
            self.check('updateConfiguration.operatingSystem', 'Windows'),
            self.check('updateConfiguration.targets.azureQueries[0].locations', ['eastus', 'westus']),
            self.check('updateConfiguration.targets.azureQueries[0].scope', [sub]),
            self.check('updateConfiguration.targets.azureQueries[0].tagSettings.tags.tag', ['tag1', 'tag2']),
            self.check('updateConfiguration.windows.excludedKbNumbers', ['16800', '16800']),
            self.check('updateConfiguration.windows.includedKbNumbers', ['15000', '15000']),
            self.check('updateConfiguration.windows.includedUpdateClassifications', 'Critical'),
            self.check('updateConfiguration.windows.rebootSetting', 'IfRequired')
        ])
        self.cmd('automation software-update-configuration runs list -g {rg} --automation-account-name {account_name}', checks=[
            self.check('value', [])
        ])
        self.cmd('automation software-update-configuration machine-runs list -g {rg} --automation-account-name {account_name}', checks=[
            self.check('value', [])
        ])
        self.cmd('automation software-update-configuration delete -n {conf_name} -g {rg} --automation-account-name {account_name} -y')
