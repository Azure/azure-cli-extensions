# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class K8sconfigurationScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_k8sconfiguration')
    @record_only()
    def test_k8sconfiguration(self):
        self.kwargs.update({
            'name': 'cli-test-config1028a',
            'cluster_name': 'nanthicluster0923',
            'rg': 'nanthirg0923',
            'repo_url': 'git://github.com/anubhav929/flux-get-started',
            'operator_instance_name': 'cli-test-config1028a-opin',
            'operator_namespace': 'cli-test-config1028a-opns',
            'cluster_type': 'connectedClusters',
            'scope': 'namespace'
        })

        # List Configurations and get the count
        config_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {cluster_name} '
                                    '--cluster-type {cluster_type}').get_output_in_json())
        self.greater_than(config_count, 10)

        # Create a configuration
        self.cmd(''' k8sconfiguration create -g {rg}
                 -n {name}
                 -c {cluster_name}
                 -u {repo_url}
                 --cluster-type {cluster_type}
                 --scope {scope}
                 --operator-instance-name {operator_instance_name}
                 --operator-namespace {operator_namespace}
                 --operator-params \"--git-readonly \"
                 --ssh-private-key \"LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFZRUFxZlBtNlc3YkVLTmVvN3VCQzhTMXYydUpPS1NZWGNmanlpVEk2djNkZUhRSjJtMGFRajB0CmtwM05qMUZkRUsrMkVXTy9xNGFkWUpaS0ZZSjluWTZyREZOSXBZdmVWaVNUQjhITzI5VVdySTRLVGZMRGhiVmVCV0pjQVcKMkFpZ0ZnTU5qdTZXa0JVL1NWK1FCVHJiRVl6RFhpOTVNR1ZveTVKV3drdkdtakRaOHFSaEFxbU0rdUF4S1I4Z1lyRllPZgpRbC9zM2I5ajJKQ1VtVFlwYkxqMkJPd0JNQ1J3NlFQY0lVcVlaaUl3MUNNaXZKZ2tVQTdwUlRCZHVsYXlXNWQ2MTl4RFNsCmZ6N1JuU0tKM3RwanEwZThBTmtkU1h4SjQrMXhpNm5IM0lVY1ZBM1NzcVhWam80ak5sNU5EWkJlTDNpQ0xXSVZYUkpDemsKNGg3a2pXVkQ3UnNDNGJDOTF6MzlZMDlnK3ZIdjErZFplUmNYZWIvNkFzbTBEeHVhRGo2cVVCVm9JOWkwbzFKbndiMnA0MQpGV2prazljc054a2dnajMzU3ozTWJRTVN0bTFLaWU2bHNRamlMUXdGT3Qwd3lFTnova2RUR25idkVMUTN3aWdUdVFrelFOCnlMR2dmK3FXZnhqL1l1MWt5b0xrQVpqT3JxdEttalVILzk3Y3lncWhBQUFGa08zNi9uWHQrdjUxQUFBQUIzTnphQzF5YzIKRUFBQUdCQUtuejV1bHUyeENqWHFPN2dRdkV0YjlyaVRpa21GM0g0OG9reU9yOTNYaDBDZHB0R2tJOUxaS2R6WTlSWFJDdgp0aEZqdjZ1R25XQ1dTaFdDZloyT3F3eFRTS1dMM2xZa2t3ZkJ6dHZWRnF5T0NrM3l3NFcxWGdWaVhBRnRnSW9CWUREWTd1CmxwQVZQMGxma0FVNjJ4R013MTR2ZVRCbGFNdVNWc0pMeHBvdzJmS2tZUUtwalByZ01Ta2ZJR0t4V0RuMEpmN04yL1k5aVEKbEprMktXeTQ5Z1RzQVRBa2NPa0QzQ0ZLbUdZaU1OUWpJcnlZSkZBTzZVVXdYYnBXc2x1WGV0ZmNRMHBYOCswWjBpaWQ3YQpZNnRIdkFEWkhVbDhTZVB0Y1l1cHg5eUZIRlFOMHJLbDFZNk9JelplVFEyUVhpOTRnaTFpRlYwU1FzNU9JZTVJMWxRKzBiCkF1R3d2ZGM5L1dOUFlQcng3OWZuV1hrWEYzbS8rZ0xKdEE4Ym1nNCtxbEFWYUNQWXRLTlNaOEc5cWVOUlZvNUpQWExEY1oKSUlJOTkwczl6RzBERXJadFNvbnVwYkVJNGkwTUJUcmRNTWhEYy81SFV4cDI3eEMwTjhJb0U3a0pNMERjaXhvSC9xbG44WQovMkx0Wk1xQzVBR1l6cTZyU3BvMUIvL2UzTW9Lb1FBQUFBTUJBQUVBQUFHQkFKSnJUVTlqY0Z4ZlE1UHdZUGRRbS95MG10CjR3QUEwYnY0WlNOcjh0dy9hWWtqeWFybnJPMWtwd3BiNkpySkpKcjZRL3Vjdi9CK3RFejhMRVQ1REViMTBKQzVlRWJ5THMKRTdnbEl5Q0Y3eWp1bnJZVkpwbzFiVEZhVWtYd24wTkdlQ2JkWHNlODdhWDFISmdQemdmZ2dhcTk2aks5ZWtKcXJzQXM4VwpGWjZWNDgrR0N3WU9LU1dpclBmdWx5b3YvQURCOVZJVzdTQ3lWek9uTGRGTWRVZXJBMjI3Y3NUaEtTZnI0MzFDQjU2SE43CmFkdnRmNnR4alV0TXBoTjV5ZVBiRmxVZS9Wb2VQY1hNdXA4OXN3V2gvd3ZScklCbytUYXo2SzQxcGFzOEVObjFyemFxL3kKRHlWelJuSGtlMGhKR2ZZelJhbzlZQm5jeHFMOCtXdDQxZFFzQUdhdlIwd3ZNSit5TFpuR0x5amVXaVZkcExjT0FWSGpIOQpITGMrTDdnaGpIZ1VidDNDWG9Wd0gyWktnelI5cmk3bU93YnorejZsN1pwWjlQalJxeU1HcTloYU5vNHVEdjJqbWhGNlZVClBMU2Q3WTczWCtWTFAvWUZqbTBlUzJUbGFRQ3E2Vms0dzJqSHVWcXorcng4SllYb2tidFZXYnFYcmg3VzF5VGk4MXVRQUEKQU1Ba0JaQzF0SThvd29SNDYvL1h1SWQxQjBGRUhGUXBvSHFuVGNSVlVKS2RXb2xJRU5tYVVtdG1UZFVicVYyNGJMa1RtZQpiWHZQdlF3LzJoVk5VVmhWbDNjays1SUZBS0hYVWJ3ZklSWE8vUVlUbFM0ZVdabkFsN0JQSzJQa080SXkvOG1zQVZKRGl4CmkvVm1oaTBYb05lSmxERU9sdzNaY084aTlRZjVSbTNEWmRHUDRha0JsYmk5ekdBWUpqRGFjM0dWdTMxK2pJVG9hUHplbysKeUFDL2svM0J5Slg4enQ1cDRHVXpsNVFKcEVHMnBpQXdJeElKZS8yK3pBMXU5dmhma0FBQURCQU5NZHdhemx5MXNpd0dXbQpJWSs4VFZMN1EwQ1pFTWxTL0VraE1YM2FNQnZYaURXd2cwVk8zKytXUDhlMWhDSUxvNmdqL0N2dFdLdGEzVlozUWFScHZ5CkhCVEp4Q205NHZQOXFPelhTRGZ0WVRrSHh1SFdQaklhb010N0YyL0srejJiZTdESmhvL0ZwMVY0U2x2R1ljWHdqaWhEaDAKbHF1bUltOEJJei9taHpjZTFKR0VMUUdJeXk4RDI0dTNtY2NhSFoxYWY1V3A5Y1VCZ09POXEwa3B1WVhEdHpPSk9UTVozUQpNUm5xdXVVM1ppRHdmRGltZzdsZktwWGkxZzFxeWZUd0FBQU1FQXpoWEdhTVdBM1pUT1hqWWhPTUhkdTk0R2RNcHNXYWo0CjBsMmZ6YzdFWTlzWEdLZ01XMllvRXk5UVNSTDRPUmNMaUFKTDRLZGdZeGZzeVdma1U1d21TbGZXNjlrb0R2WTE0LzNWbWYKZ0NTUkxvL0RnTUZtOGFNK3pUVzhWYTVpclJXWFpEeHNXb0RiNzdIZ2JZaE90M29iOEFWWUh4akk3N1k3MXlBUzhXS2xRSQpYQi9qZ01vN1BCL3BTMVVYSEhCcndxQkdwM3M5aThab0E0L2hLY0pvaEtWSDZGL0Z2Rk1jWHZTNjZOcGNUWHNWQzBVUzNkCkJVY0taNTVvUUhVcnNQQUFBQUdIQnlZWFJvYVd0eVFFeEJVRlJQVUMxU00wZFVUa2xDVXdFQwotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K\"
                 --enable-helm-operator
                 --helm-operator-version 1.2.0
                 --helm-operator-params \"--set git.ssh.secretName=gitops-privatekey-{operator_instance_name} --set tillerNamespace=kube-system\" ''',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # List the configurations again to see if we have one additional
        new_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {cluster_name} '
                                 '--cluster-type {cluster_type}').get_output_in_json())
        self.assertEqual(new_count, config_count + 1)

        # Get the configuration created
        self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # Delete the created configuration
        self.cmd('k8sconfiguration delete -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type} -y')

        # List Configurations and confirm the count is the same as we started
        new_count = len(self.cmd('k8sconfiguration list -g {rg} --cluster-name {cluster_name} '
                                 '--cluster-type {cluster_type}').get_output_in_json())
        self.assertEqual(new_count, config_count)
