from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class VmRepairTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_vm_repair')
    def test_vm_repair_create_success(self, resource_group):
        self.kwargs.update({
            'vm_name': 'MyVM'
        })

        result = self.cmd('az vm repair create -g {rg} -n {vm_name} --verbose').get_output_in_json()
        self.assertIn('repairVM', result)
