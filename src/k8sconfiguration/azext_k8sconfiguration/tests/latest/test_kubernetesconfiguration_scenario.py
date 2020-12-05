# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)
from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class K8sconfigurationScenarioTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_k8sconfiguration')
    @record_only()
    def test_k8sconfiguration_success(self):

        # --------------------------------------------------------------------
        #  SSH SCENARIO TEST
        # --------------------------------------------------------------------
        self.kwargs.update({
            'name': 'cli-test-config10',
            'cluster_name': 'nanthicluster0923',
            'rg': 'nanthirg0923',
            'repo_url': 'git://github.com/anubhav929/flux-get-started',
            'operator_instance_name': 'cli-test-config10-opin',
            'operator_namespace': 'cli-test-config10-opns',
            'cluster_type': 'connectedClusters',
            'scope': 'namespace',
            'ssh_private_key': 'LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFZRUFxZlBtNlc3YkVLTmVvN3VCQzhTMXYydUpPS1NZWGNmanlpVEk2djNkZUhRSjJtMGFRajB0CmtwM05qMUZkRUsrMkVXTy9xNGFkWUpaS0ZZSjluWTZyREZOSXBZdmVWaVNUQjhITzI5VVdySTRLVGZMRGhiVmVCV0pjQVcKMkFpZ0ZnTU5qdTZXa0JVL1NWK1FCVHJiRVl6RFhpOTVNR1ZveTVKV3drdkdtakRaOHFSaEFxbU0rdUF4S1I4Z1lyRllPZgpRbC9zM2I5ajJKQ1VtVFlwYkxqMkJPd0JNQ1J3NlFQY0lVcVlaaUl3MUNNaXZKZ2tVQTdwUlRCZHVsYXlXNWQ2MTl4RFNsCmZ6N1JuU0tKM3RwanEwZThBTmtkU1h4SjQrMXhpNm5IM0lVY1ZBM1NzcVhWam80ak5sNU5EWkJlTDNpQ0xXSVZYUkpDemsKNGg3a2pXVkQ3UnNDNGJDOTF6MzlZMDlnK3ZIdjErZFplUmNYZWIvNkFzbTBEeHVhRGo2cVVCVm9JOWkwbzFKbndiMnA0MQpGV2prazljc054a2dnajMzU3ozTWJRTVN0bTFLaWU2bHNRamlMUXdGT3Qwd3lFTnova2RUR25idkVMUTN3aWdUdVFrelFOCnlMR2dmK3FXZnhqL1l1MWt5b0xrQVpqT3JxdEttalVILzk3Y3lncWhBQUFGa08zNi9uWHQrdjUxQUFBQUIzTnphQzF5YzIKRUFBQUdCQUtuejV1bHUyeENqWHFPN2dRdkV0YjlyaVRpa21GM0g0OG9reU9yOTNYaDBDZHB0R2tJOUxaS2R6WTlSWFJDdgp0aEZqdjZ1R25XQ1dTaFdDZloyT3F3eFRTS1dMM2xZa2t3ZkJ6dHZWRnF5T0NrM3l3NFcxWGdWaVhBRnRnSW9CWUREWTd1CmxwQVZQMGxma0FVNjJ4R013MTR2ZVRCbGFNdVNWc0pMeHBvdzJmS2tZUUtwalByZ01Ta2ZJR0t4V0RuMEpmN04yL1k5aVEKbEprMktXeTQ5Z1RzQVRBa2NPa0QzQ0ZLbUdZaU1OUWpJcnlZSkZBTzZVVXdYYnBXc2x1WGV0ZmNRMHBYOCswWjBpaWQ3YQpZNnRIdkFEWkhVbDhTZVB0Y1l1cHg5eUZIRlFOMHJLbDFZNk9JelplVFEyUVhpOTRnaTFpRlYwU1FzNU9JZTVJMWxRKzBiCkF1R3d2ZGM5L1dOUFlQcng3OWZuV1hrWEYzbS8rZ0xKdEE4Ym1nNCtxbEFWYUNQWXRLTlNaOEc5cWVOUlZvNUpQWExEY1oKSUlJOTkwczl6RzBERXJadFNvbnVwYkVJNGkwTUJUcmRNTWhEYy81SFV4cDI3eEMwTjhJb0U3a0pNMERjaXhvSC9xbG44WQovMkx0Wk1xQzVBR1l6cTZyU3BvMUIvL2UzTW9Lb1FBQUFBTUJBQUVBQUFHQkFKSnJUVTlqY0Z4ZlE1UHdZUGRRbS95MG10CjR3QUEwYnY0WlNOcjh0dy9hWWtqeWFybnJPMWtwd3BiNkpySkpKcjZRL3Vjdi9CK3RFejhMRVQ1REViMTBKQzVlRWJ5THMKRTdnbEl5Q0Y3eWp1bnJZVkpwbzFiVEZhVWtYd24wTkdlQ2JkWHNlODdhWDFISmdQemdmZ2dhcTk2aks5ZWtKcXJzQXM4VwpGWjZWNDgrR0N3WU9LU1dpclBmdWx5b3YvQURCOVZJVzdTQ3lWek9uTGRGTWRVZXJBMjI3Y3NUaEtTZnI0MzFDQjU2SE43CmFkdnRmNnR4alV0TXBoTjV5ZVBiRmxVZS9Wb2VQY1hNdXA4OXN3V2gvd3ZScklCbytUYXo2SzQxcGFzOEVObjFyemFxL3kKRHlWelJuSGtlMGhKR2ZZelJhbzlZQm5jeHFMOCtXdDQxZFFzQUdhdlIwd3ZNSit5TFpuR0x5amVXaVZkcExjT0FWSGpIOQpITGMrTDdnaGpIZ1VidDNDWG9Wd0gyWktnelI5cmk3bU93YnorejZsN1pwWjlQalJxeU1HcTloYU5vNHVEdjJqbWhGNlZVClBMU2Q3WTczWCtWTFAvWUZqbTBlUzJUbGFRQ3E2Vms0dzJqSHVWcXorcng4SllYb2tidFZXYnFYcmg3VzF5VGk4MXVRQUEKQU1Ba0JaQzF0SThvd29SNDYvL1h1SWQxQjBGRUhGUXBvSHFuVGNSVlVKS2RXb2xJRU5tYVVtdG1UZFVicVYyNGJMa1RtZQpiWHZQdlF3LzJoVk5VVmhWbDNjays1SUZBS0hYVWJ3ZklSWE8vUVlUbFM0ZVdabkFsN0JQSzJQa080SXkvOG1zQVZKRGl4CmkvVm1oaTBYb05lSmxERU9sdzNaY084aTlRZjVSbTNEWmRHUDRha0JsYmk5ekdBWUpqRGFjM0dWdTMxK2pJVG9hUHplbysKeUFDL2svM0J5Slg4enQ1cDRHVXpsNVFKcEVHMnBpQXdJeElKZS8yK3pBMXU5dmhma0FBQURCQU5NZHdhemx5MXNpd0dXbQpJWSs4VFZMN1EwQ1pFTWxTL0VraE1YM2FNQnZYaURXd2cwVk8zKytXUDhlMWhDSUxvNmdqL0N2dFdLdGEzVlozUWFScHZ5CkhCVEp4Q205NHZQOXFPelhTRGZ0WVRrSHh1SFdQaklhb010N0YyL0srejJiZTdESmhvL0ZwMVY0U2x2R1ljWHdqaWhEaDAKbHF1bUltOEJJei9taHpjZTFKR0VMUUdJeXk4RDI0dTNtY2NhSFoxYWY1V3A5Y1VCZ09POXEwa3B1WVhEdHpPSk9UTVozUQpNUm5xdXVVM1ppRHdmRGltZzdsZktwWGkxZzFxeWZUd0FBQU1FQXpoWEdhTVdBM1pUT1hqWWhPTUhkdTk0R2RNcHNXYWo0CjBsMmZ6YzdFWTlzWEdLZ01XMllvRXk5UVNSTDRPUmNMaUFKTDRLZGdZeGZzeVdma1U1d21TbGZXNjlrb0R2WTE0LzNWbWYKZ0NTUkxvL0RnTUZtOGFNK3pUVzhWYTVpclJXWFpEeHNXb0RiNzdIZ2JZaE90M29iOEFWWUh4akk3N1k3MXlBUzhXS2xRSQpYQi9qZ01vN1BCL3BTMVVYSEhCcndxQkdwM3M5aThab0E0L2hLY0pvaEtWSDZGL0Z2Rk1jWHZTNjZOcGNUWHNWQzBVUzNkCkJVY0taNTVvUUhVcnNQQUFBQUdIQnlZWFJvYVd0eVFFeEJVRlJQVUMxU00wZFVUa2xDVXdFQwotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K',
            'ssh_known_hosts': 'Z2l0b3BzLWJpdGJ1Y2tldC10ZXN0LXNlcnZlci5lYXN0dXMuY2xvdWRhcHAuYXp1cmUuY29tIHNzaC1yc2EgQUFBQUIzTnphQzF5YzJFQUFBQURBUUFCQUFBQkFRQytNT0w3bjk2aGs3emVmMDNwak9vMGF3UENISkZ4NU04TjJ2L2tvODgvc202Y2VzOFljdnYyL0hoUlhRSFZHRUxqZjNuTXVGSVJPMEdMdTFabFNreGRUTUhGcXBxYzFjcUM2R3kveUJXRGM1SWFwWnJBMXFxeSsrZVdpelAzQXdMbWsrMUhXWGdtcHljZUtYNU9vd3VNT3cwd3RYRUdTcDhtVk0wV2VpUzEwWnZ5ZVVKK04zbkNvczMyWDhIeVpnc1pMUS9zSTB4NXN6ODQ2am5JZEFOckZsYU9MUTJ1ejRUa0M2ekNvd3lIdzlLWXJ5V2hJZDAraCt5SXQ5dUtqVHZsWFNpdm1ISjViZzdUWWlkbnFtbjI0UGE4WnFpbTE5UGszUjg0cW9qclVmYm1XT3VwUjdYNXZVVWZqYzhERFRxa3FnRmkxcWdVdE1mWGlMRXErZFVa'
        })

        # Check that the configuration does not already exist
        with self.assertRaises(ResourceNotFoundError):
            self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}')

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
                 --ssh-private-key {ssh_private_key}
                 --ssh-known-hosts {ssh_known_hosts}
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
                     self.check('operatorType', 'Flux'),
                     self.check('sshKnownHostsContents', '{ssh_known_hosts}')
                 ])

        # Get the configuration created
        self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux'),
                     self.check('sshKnownHostsContents', '{ssh_known_hosts}')
                 ])

        # Delete the created configuration
        self.cmd('k8sconfiguration delete -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type} -y')

        # --------------------------------------------------------------------
        #  HTTPS SCENARIO TEST
        # --------------------------------------------------------------------
        self.kwargs.update({
            'name': 'cli-test-config11',
            'cluster_name': 'nanthicluster0923',
            'rg': 'nanthirg0923',
            'repo_url': 'https://github.com/jonathan-innis/helm-operator-get-started-private.git',
            'operator_instance_name': 'cli-test-config11-opin',
            'operator_namespace': 'cli-test-config11-opns',
            'cluster_type': 'connectedClusters',
            'scope': 'namespace',
            'https_user': 'fake-username',
            'https_key': 'fakepasswordthatiwoulduseforgithub'
        })

        # Check that the configuration does not already exist
        with self.assertRaises(ResourceNotFoundError):
            self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}')

        self.cmd(''' k8sconfiguration create -g {rg}
                 -n {name}
                 -c {cluster_name}
                 -u {repo_url}
                 --cluster-type {cluster_type}
                 --scope {scope}
                 --operator-instance-name {operator_instance_name}
                 --operator-namespace {operator_namespace}
                 --operator-params \"--git-readonly \"
                 --https-user {https_user}
                 --https-key {https_key}
                 --enable-helm-operator
                 --helm-operator-version 1.2.0
                 --helm-operator-params \"--set tillerNamespace=kube-system\" ''',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux')
                 ])

        # Get the configuration created
        self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux'),
                 ])

        # Delete the created configuration
        self.cmd('k8sconfiguration delete -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type} -y')

    @ResourceGroupPreparer(name_prefix='cli_test_k8sconfiguration')
    @record_only()
    def test_k8sconfiguration_pass_on_good_key(self):
        self.kwargs.update({
            'name': 'cli-test-config12',
            'cluster_name': 'nanthicluster0923',
            'rg': 'nanthirg0923',
            'repo_url': 'git://github.com/anubhav929/flux-get-started',
            'operator_instance_name': 'cli-test-config12-opin',
            'operator_namespace': 'cli-test-config12-opns',
            'cluster_type': 'connectedClusters',
            'scope': 'namespace',
        })

        rsa_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFZRUF1bVA5M09qRHdjdlEyZHZhRlJNNWYrMEhVSnFvOFJnbmdwaGN3NFZidnd1TVNoQTZFc2FyCjFsam1CNUNnT1NGNHJqNDIvcmdxMW1hWndoSUgvckdPSElNa0lIcjFrZmNKMnBrR3ZhK1NxVm4wWUhzMjBpUW02ay92ZXQKdXdVQ2J1QjlxSU5zL2h2b0ppQ21JMUVpVWZ4VGoxRFJCUG15OXR3Qm52bW5FS1kxZ2NhT2YrS2Y1aGhCc09pd00yZnBRTwp0aTlIcHVzM1JhNXpFeElWbjJzVitpRjVvV3ZZM1JQTTlKNXFPMXRObUtOWll6TjgzbDYxMlBzRmR1Vm1QM2NUUlJtK2pzCjdzZW5jY0U0RitzU0hQMlJpMk5DU0JvZ2RJOFR5VTlzeTM3Szl3bFJ5NGZkWWI1K1o3YUZjMjhTNDdDWlo5dTRFVXdWUEYKbjU4dTUzajU0empwdXNpei9ZWmx3MG5NeEQ5SXI0aHlJZ2s0NlUzVmdHR0NPUytZVTVZT2JURGhPRG5udk5VRkg2NVhCagpEM3l6WVJuRDA3b2swQ1JUR3RCOWMzTjBFNDBjUnlPeVpEQ0l5a0FPdHZXYnBUZzdnaXA2UDc4K2pLVlFnanFwRTVQdi9ICnl1dlB6cUJoUkpWcG5VR1dvWnFlcWJhd2N5RWZwdHFLaTNtWUdVMHBBQUFGa0U5cUs3SlBhaXV5QUFBQUIzTnphQzF5YzIKRUFBQUdCQUxwai9kem93OEhMME5uYjJoVVRPWC90QjFDYXFQRVlKNEtZWE1PRlc3OExqRW9RT2hMR3E5Wlk1Z2VRb0RraAplSzQrTnY2NEt0Wm1tY0lTQi82eGpoeURKQ0I2OVpIM0NkcVpCcjJ2a3FsWjlHQjdOdElrSnVwUDczcmJzRkFtN2dmYWlECmJQNGI2Q1lncGlOUklsSDhVNDlRMFFUNXN2YmNBWjc1cHhDbU5ZSEdqbi9pbitZWVFiRG9zRE5uNlVEcll2UjZick4wV3UKY3hNU0ZaOXJGZm9oZWFGcjJOMFR6UFNlYWp0YlRaaWpXV016Zk41ZXRkajdCWGJsWmo5M0UwVVp2bzdPN0hwM0hCT0JmcgpFaHo5a1l0alFrZ2FJSFNQRThsUGJNdCt5dmNKVWN1SDNXRytmbWUyaFhOdkV1T3dtV2ZidUJGTUZUeForZkx1ZDQrZU00CjZicklzLzJHWmNOSnpNUS9TSytJY2lJSk9PbE4xWUJoZ2prdm1GT1dEbTB3NFRnNTU3elZCUit1VndZdzk4czJFWnc5TzYKSk5Ba1V4clFmWE56ZEJPTkhFY2pzbVF3aU1wQURyYjFtNlU0TzRJcWVqKy9Qb3lsVUlJNnFST1Q3L3g4cnJ6ODZnWVVTVgphWjFCbHFHYW5xbTJzSE1oSDZiYWlvdDVtQmxOS1FBQUFBTUJBQUVBQUFHQkFMaElmSXFacUZKSFRXcllyN24rays4alR3ClFtcGJvWmc1YmZSWGdhdGljaEo4ZGlXOGlNblFFRVRBcFd0OU5FZ0tqbDRrSGRuSnoyUERkZzFIN0ExaHppbkNsdzZMTTAKYUkyMGxyR2NrWWpXNDRNd3ozYmRQNHlURTllSXRiM0pmN1pNSGpqek4rSy96bWN0eWdMeXFZSzVXYTljM1JnMXdIRWFNNAplakUvNDg4M25WUmJvSFJDcjFCVi8wQVVFTTZhNisrRHpVZW9WdWdWL3RsV3RVMlJuQlZ4eCtJS0FVSDZRTHJFU2JkUkRoCkVGUEFhRWtEb3crd3dDcFpqTXBhMHdRZXBDSkhwWkJLN1pBU25EU3R3Y2RKRE4yeHZzdVNOOGg0bkN0MlZWd0xRenJKeVAKU2VjcWM3M1hIc3E3VWx6ZU5veHlTVW9KZ2JjNTZoRzhWYS9ITlhsOUtkdkFlWUVzS1l1OW5NRUprVSt3VHo1KzUvM2wwVQpxSkErb0pTVTducjYydlVKQnljbXg0SFdBcjJ6QkR2QnFBUWMzRG9LWHczeVM1Z0c5Zkc0c25OUUkxOHVRSjdOSjdndHZHClpKRU56bTNJMmFTMzl5dndWZnFIMXpXVERxU2VNeWhYeWFnTkFEcGtCVEJIMVJQR2NtTFplclFmWWx1djVVUmFNTXdRQUEKQU1BdE9oNHFwUUhidm5tQ1RVakx4dXRrWnRaRlhNa0hmSTk5NS9Nd2RvWVY1eWRKV0pUVGsyKzB1QVBIcTZEejk2b3dWbQpjUkF2WDBDOVU5d3ZRMkpnR0Y1MDZzcmgzZkVpUzM2d1ArOFd0RjZ6ODd0enJwQnpQVHIxOGRONURCOEx5L3dXRk5BVTdqClBUbXM0dHlUY1VsRXR3eEt4TXJTNC9ROUZwMWozL3JNdnNZdGVaSVgycmN4YUhkWWJDVGJtTUpZS3lVTWVXTk56NXpub1EKcFcyd2NDSmpJc1MvS1F2WmR4cHZwNWd0RXE1WlEva3FvLzJVRWd1NHhwdDNWeUNma0FBQURCQVBOSHVEU1R0ZEpJWjdzcwpaQkVwcUE4TE54b1dMQ2RURnlpRERiUnpYOWVPTldkRFQ3NklaRE9HejczNXJhZUFSM2FiY0FhaUM0dDQwTFJTNGEyN29sCm9wK1dSak9wcjVNYUtOUnk4MCt6VWw3WUlSMjErKzVnMFVnNkRnQlBEdmFJSHFSTnRsZ2gyVXdTL0cva1lOaUlEY0JiS1EKOUcvdTI4ekRIRUtNL21YYS8wYnFtSm16ZUYvY1BLdHdScFE3clFoRnAwUkdFcnZtc0l4dDl6K0ZZZUdncjFBYUVTV0ZlTApmUmZsa0lnOVBWOEl0b09GN25qK2VtMkxkNTNCS1hSUUFBQU1FQXhDTFBueHFFVEsyMW5QOXFxQVYzMEZUUkhGNW9kRHg4ClpiYnZIbjgwdEgxQjYwZjRtTGJFRm56REZFR0NwS2Rwb3dyUXR6WUhnQzNBaGNJUE9BbXFXaDg0UEFPbisreHhFanNaQkwKRWhVWmNFUndkYTMzTnJDNTVEMzZxbDBMZEsrSGRuZUFzVGZhazh0bWVlOTJWb0RxdWovNGFSMjBmUTBJUFVzMU8rWHNRNQpGWVFYQzZndExHZGRzRVFoSDF6MTh6RGtWa1UwdEhlZkJaL2pFZXBiOEZScXoxR1hpT0hGK2xBZVE2b3crS0xlcWtCcXQ4CkZxMHhGdG90SlF4VnFWQUFBQUYycHZhVzV1YVhOQVJFVlRTMVJQVUMxUVRWVkdVRFpOQVFJRAotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K"
        ed25519_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFNd0FBQUF0emMyZ3RaVwpReU5UVXhPUUFBQUNCNjF0RzkrNGFmOTZsWGoyUStjWjJMT2JpV1liMlRtWVR6N3NSV0JDM1hVZ0FBQUtCRzFWRWZSdFZSCkh3QUFBQXR6YzJndFpXUXlOVFV4T1FBQUFDQjYxdEc5KzRhZjk2bFhqMlErY1oyTE9iaVdZYjJUbVlUejdzUldCQzNYVWcKQUFBRURRTStLcCtOSWpJVUhSUklqRFE5VDZ0U0V0SG9Ic0w1QjlwbHpCNlZ2MnluclcwYjM3aHAvM3FWZVBaRDV4bllzNQp1SlpodlpPWmhQUHV4RllFTGRkU0FBQUFGMnB2YVc1dWFYTkFSRVZUUzFSUFVDMVFUVlZHVURaTkFRSURCQVVHCi0tLS0tRU5EIE9QRU5TU0ggUFJJVkFURSBLRVktLS0tLQo="
        esdsa_key = "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFhQUFBQUJObFkyUnpZUwoxemFHRXlMVzVwYzNSd01qVTJBQUFBQ0c1cGMzUndNalUyQUFBQVFRUjBRc1BjWmJKeWZPaXE2a1M1d0VaeE5DbmR2YVJHCm1ETEUvVVBjakpDTDZQTVIyZmdPS2NnWlhzTEZkTUFzSnExS2d6TmNDN0ZXNGE0L0wrYTFWWUxDQUFBQXNIZ1RqTFY0RTQKeTFBQUFBRTJWalpITmhMWE5vWVRJdGJtbHpkSEF5TlRZQUFBQUlibWx6ZEhBeU5UWUFBQUJCQkhSQ3c5eGxzbko4NktycQpSTG5BUm5FMEtkMjlwRWFZTXNUOVE5eU1rSXZvOHhIWitBNHB5Qmxld3NWMHdDd21yVXFETTF3THNWYmhyajh2NXJWVmdzCklBQUFBZ0h1U3laU0NUZzJZbVNpOG9aY2c0cnVpODh0T1NUSm1aRVhkR09hdExySHNBQUFBWGFtOXBibTVwYzBCRVJWTkwKVkU5UUxWQk5WVVpRTmswQgotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K"

        # Test each key type and see if the configuration configuration is created with no error
        for private_key in [rsa_key, ed25519_key, esdsa_key]:
            # Create a configuration
            self.kwargs.update({
                'ssh_private_key': private_key
            })

            # Check that the configuration does not already exist
            with self.assertRaises(ResourceNotFoundError):
                self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}')

            self.cmd(''' k8sconfiguration create -g {rg}
                    -n {name}
                    -c {cluster_name}
                    -u {repo_url}
                    --cluster-type {cluster_type}
                    --scope {scope}
                    --operator-instance-name {operator_instance_name}
                    --operator-namespace {operator_namespace}
                    --operator-params \"--git-readonly \"
                    --ssh-private-key {ssh_private_key}
                    --enable-helm-operator
                    --helm-operator-version 1.2.0
                    --helm-operator-params \"--set git.ssh.secretName=gitops-privatekey-{operator_instance_name} --set tillerNamespace=kube-system\" ''')

            self.cmd('k8sconfiguration show -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('resourceGroup', '{rg}'),
                     self.check('operatorInstanceName', '{operator_instance_name}'),
                     self.check('operatorNamespace', '{operator_namespace}'),
                     self.check('provisioningState', 'Succeeded'),
                     self.check('operatorScope', 'namespace'),
                     self.check('operatorType', 'Flux'),
                 ])
            self.cmd('k8sconfiguration delete -g {rg} -c {cluster_name} -n {name} --cluster-type {cluster_type} -y')

    @ResourceGroupPreparer(name_prefix='cli_test_k8sconfiguration')
    @record_only()
    def test_k8sconfiguration_fail_on_bad_key(self):
        self.kwargs.update({
            'name': 'cli-test-config10',
            'cluster_name': 'nanthicluster0923',
            'rg': 'nanthirg0923',
            'repo_url': 'git://github.com/anubhav929/flux-get-started',
            'operator_instance_name': 'cli-test-config10-opin',
            'operator_namespace': 'cli-test-config10-opns',
            'cluster_type': 'connectedClusters',
            'scope': 'namespace',
        })

        bad_keys = [
            "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0NCmIzQmxibk56YUMxclpYa3RkakVBQUFBQUJHNXZibVVBQUFBRWJtOXVaUUFBQUFBQUFBQUJBQUFCbHdBQUFBZHpjMmd0Y24NCk5oQUFBQUF3RUFBUUFBQVlFQStJY2wvSi9ENkpzUG1Xbjcrak14RHJpcklPUVpGSXB5cE1IRjNJMXM3am1PTzF4UTQ5TDANCnRZQ1FnUldsVk1NK2RoSlBxN2RjWU1iU3p6L1E1WDltMmlCVThMb3VGaGVkQmdUSm1FZGRPRjAyblQ2ZDJLcXJvdFdYWVgNCnpBTFRLQXdoaU5ZelhQdEdZMWhwd3dpN1ZDZUZxbVJWaysxTUt3dy9nL29meUl2L0NzeHZqa25McFRXWFVWUjd3Z1JHekENCnNpSmxkSmp5UExvTjF5cmNiQTR6cXFaV3I2NU9wMmhzVHVwR3pvdkdJMk1xNVg1NnM0T2sxTUJTNXhWQlVWajFPWjIwcnINCno0MU83dWNRV2FHOG1tOXlVTDYra00yT2hyTHBqMVVMWVlrOFN0QjBQbUtZRVBCQTFjY2E2NlJ4NUV1YnJLOWpheDNzWUQNCjlVMC9XcVlvaWZVYS93N29ncE1YV1lEQnFNTWNhZlBubWxyOGlVMmI0Mko0SUtQV0I2WTNyNGQ4dGlDcjlQdm8rUGw0UjENCjE5bi9BdFVlOEg2OFUzL2ZhS2g0dVo3WVNia0JqalVPNWJqTUtSL0Njd2FuczhaNGQrZnR5TjFoTW9WODJKTTNOcDZPdnoNCkZ2TW9DV3RLeDM2ZFlhTFZMS1lTRnJnTzNTYUo1WXF6clZpdDlMZjdBQUFGbU9STzZ6dmtUdXM3QUFBQUIzTnphQzF5YzINCkVBQUFHQkFQaUhKZnlmdytpYkQ1bHArL296TVE2NHF5RGtHUlNLY3FUQnhkeU5iTzQ1amp0Y1VPUFM5TFdBa0lFVnBWVEQNClBuWVNUNnUzWEdERzBzOC8wT1YvWnRvZ1ZQQzZMaFlYblFZRXlaaEhYVGhkTnAwK25kaXFxNkxWbDJGOHdDMHlnTUlZalcNCk0xejdSbU5ZYWNNSXUxUW5oYXBrVlpQdFRDc01QNFA2SDhpTC93ck1iNDVKeTZVMWwxRlVlOElFUnN3TElpWlhTWThqeTYNCkRkY3EzR3dPTTZxbVZxK3VUcWRvYkU3cVJzNkx4aU5qS3VWK2VyT0RwTlRBVXVjVlFWRlk5VG1kdEs2OCtOVHU3bkVGbWgNCnZKcHZjbEMrdnBETmpvYXk2WTlWQzJHSlBFclFkRDVpbUJEd1FOWEhHdXVrY2VSTG02eXZZMnNkN0dBL1ZOUDFxbUtJbjENCkd2OE82SUtURjFtQXdhakRIR256NTVwYS9JbE5tK05pZUNDajFnZW1ONitIZkxZZ3EvVDc2UGo1ZUVkZGZaL3dMVkh2QisNCnZGTi8zMmlvZUxtZTJFbTVBWTQxRHVXNHpDa2Z3bk1HcDdQR2VIZm43Y2pkWVRLRmZOaVROemFlanI4eGJ6S0FsclNzZCsNCm5XR2kxU3ltRWhhNER0MG1pZVdLczYxWXJmUzMrd0FBQUFNQkFBRUFBQUdBVlEwTE52VUYrbWgyWWk0ZkNYVFRhUkpSbmkNClB4WVZJd0FhbytxRWZONjRqTzRBbXJ0UXZRcXZ5Z2QweU5GQUR0TTBMNCtPNzdNak5ZbVl4aFZPalFyZjA2bEZkaXhqUzINCmpBUy9hTm1qVVZLMUNnTVB5Y0kra3E4OTZ5TGlNWldDOHVtc0dUT2xMVHQ5UGQvZHpUSHUyWGxNUlpkUkpVYXJiNlZaUVgNCnBHNGtqZkdBaTlVOVdBQ0xGRTR4UENoeWdnbWRXam1zOXN0dE9GUVFsdC9aeXVtY3ZyQnB4RVZvNHA0cWZTSzRVeC9aSkcNCmI5dGs2bUkyMm9nbTF1WXpRRCtNbjlEWC9qWGV6U2ZETkZtemF2Z0poOG9wcXdvQmQ5d00xRjRlRDk3bk05NzhwYWhwZngNCjNhZmxHdXE3dkY0eGNyOUlyUmZGWU1UNnl0VkFEajVNTjA0Z0doUnd0ZmxpVDRydlRXQ2owUlhPbFhSNkl5QVVMVURuTXQNCk5Ldmg3M21qcDRLaFNWNzdhOC8rZFR1OHV3b1BDanhrM0Y2ZjZieDhwWkoxYUdIZWhMNHZJc3F6YUdRQTc5MVRHbHRockwNCnFJeklLeGMvdVdYY2FaZTNBV24reTdmR1RKcTBkMmliVFJndkphNDZXcGR5aUVwM2VSVy9zTm1lQjVwNHJmYUdHQkFBQUENCndRRGhsZ2hUOVhLc2QvbXpBVDM4Wm45UHJlTGdkTmxqbmE0QUhtY28yVXlid2hWQnBzR1k4MHdtLzJnRmd1clJUdVdsb0gNCmlnNlg1WkpYWG9OUmVrL05PUktVbzczUW8wdTZzbVprUnlvQk5VTnV3UFY3TU9GTm1pa2cyL1RiNXFMOUFQaHQ3MytHbkINCnJxNC9QUE1SVEJxSFAxcjEwUTAwdE9CQ3k3Y2RTRWwrSWZoajZlbk5tM3ZiWmdTOEpFSkZGZlRneEh4OXN1NWxIU01NQ3kNCnUweFlkT1FqRHQ0cHBVb1dtSWJmSEZ0ajRFNGRhL1UvcGRjS2tiZFNHNDcyL1JtQndBQUFEQkFQNTIwcHd4YmxJRjNScHkNCkZ0d3pRK3BybTRjNWpSakpSUC9VVXhJRTNoN1g1bFRHK3c4cmZaRWEzc1FvcWsvRmYydlpqaWtSWEQ1YjZ1WEJJTU00RmsNCkhIbUJZZUh2bUV5T21GdUF4VUVRYndJdFdXZlUyVlp1bDRyQ1FuazlhRjNrV2Y2MzVsdWdMd2NNa3UyUXZHTWpUUndkd2UNClJ1Q0k2ZnVRWWNzakpxcVUzV083cXdmaDg5TmNGc3Zjbm5qUkdMTHY4c2RUK3A0azh0ektqUEFuZk9UcjVUdG02aXFTZHANCllhZzJkV3ZPWU1MbDV2aFRaNkRNS2ZLaWhycFhBNkVRQUFBTUVBK2djblRMRHNPcHNVd3QxamdreUNBZHlJWlRFRjB3MVYNCndMTlkvTzlWTGlHWWZCa2ZFTyt3UkFKMXEvR0ZYU1ozcFFIL0NXc3V3SzdNOFVCVVp3cHR0M1lkVUo3azBqRS9YeEh5TXgNCkV0aEFvb2tHMTBwYUtCTll6amFRQUtpd2UvL2dsQTBMbDVtMWt5b3dGWHM2N3Iyc0hXVmNVYnR3b0NTVVR1ckZoTTFYejINClJsNG5UNnpydUlITHh2bzJpWGp6QUFZRGlWeTNveXNVRlBNcUdrSVNFNUR5VTFia3NFaXlydWQ3WXlwakdUMnFBbUhwNXQNCkZGUGNuWTlteDVlMlZMQUFBQUhtcHZibUYwYUdGdUxXbHVibWx6UUVSRlUwdFVUMUF0UjFBM1JWTXhOZ0VDQXdRPQ0KLS0tLS1FTkQgT1BFTlNTSCBQUklWQQ0K",
            "dGhpc2lzbm90YXZhbGlkcHJpdmF0ZWtleQ==",
            "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0NCmIzQmxibk56YUMxclpYa3RkakVBQUFBQUJHNXZibVVBQUFBRWJtOXVaUUFBQUFBQUFBQUJBQUFCbHdBQUFBZHpjMmd0Y24NCk5oQUFBQUF3RUFBUUFBQVlFQXFmUG02VzdiRUtOZW83dUJDOFMxdjJ1Sk9LU1lYY2ZqeWlUSTZ2M2RlSFFKMm0wYVFqMHQNCmtwM05qMUZkRUsrMkVXTy9xNGFkWUpaS0ZZSjluWTZyREZOSXBZdmVWaVNUQjhITzI5VVdySTRLVGZMRGhiVmVCV0pjQVcNCjJBaWdGZ01OanU2V2tCVS9TVitRQlRyYkVZekRYaTk1TUdWb3k1Sld3a3ZHbWpEWjhxUmhBcW1NK3VBeEtSOGdZckZZT2YNClFsL3MzYjlqMkpDVW1UWXBiTGoyQk93Qk1DUnc2UVBjSVVxWVppSXcxQ01pdkpna1VBN3BSVEJkdWxheVc1ZDYxOXhEU2wNCmZ6N1JuU0tKM3RwanEwZThBTmtkU1h4SjQrMXhpNm5IM0lVY1ZBM1NzcVhWam80ak5sNU5EWkJlTDNpQ0xXSVZYUkpDemsNCjRoN2tqV1ZEN1JzQzRiQzkxejM5WTA5Zyt2SHYxK2RaZVJjWGViLzZBc20wRHh1YURqNnFVQlZvSTlpMG8xSm53YjJwNDENCkZXamtrOWNzTnhrZ2dqMzNTejNNYlFNU3RtMUtpZTZsc1FqaUxRd0ZPdDB3eUVOei9rZFRHbmJ2RUxRM3dpZ1R1UWt6UU4NCnlMR2dmK3FXZnhqL1l1MWt5b0xrQVpqT3JxdEttalVILzk3Y3lncWhBQUFGa08zNi9uWHQrdjUxQUFBQUIzTnphQzF5YzINCkVBQUFHQkFLbno1dWx1MnhDalhxTzdnUXZFdGI5cmlUaWttRjNINDhva3lPcjkzWGgwQ2RwdEdrSTlMWktkelk5UlhSQ3YNCnRoRmp2NnVHbldDV1NoV0NmWjJPcXd4VFNLV0wzbFlra3dmQnp0dlZGcXlPQ2szeXc0VzFYZ1ZpWEFGdGdJb0JZRERZN3UNCmxwQVZQMGxma0FVNjJ4R013MTR2ZVRCbGFNdVNWc0pMeHBvdzJmS2tZUUtwalByZ01Ta2ZJR0t4V0RuMEpmN04yL1k5aVENCmxKazJLV3k0OWdUc0FUQWtjT2tEM0NGS21HWWlNTlFqSXJ5WUpGQU82VVV3WGJwV3NsdVhldGZjUTBwWDgrMFowaWlkN2ENClk2dEh2QURaSFVsOFNlUHRjWXVweDl5RkhGUU4wcktsMVk2T0l6WmVUUTJRWGk5NGdpMWlGVjBTUXM1T0llNUkxbFErMGINCkF1R3d2ZGM5L1dOUFlQcng3OWZuV1hrWEYzbS8rZ0xKdEE4Ym1nNCtxbEFWYUNQWXRLTlNaOEc5cWVOUlZvNUpQWExEY1oNCklJSTk5MHM5ekcwREVyWnRTb251cGJFSTRpME1CVHJkTU1oRGMvNUhVeHAyN3hDME44SW9FN2tKTTBEY2l4b0gvcWxuOFkNCi8yTHRaTXFDNUFHWXpxNnJTcG8xQi8vZTNNb0tvUUFBQUFNQkFBRUFBQUdCQUpKclRVOWpjRnhmUTVQd1lQZFFtL3kwbXQNCjR3QUEwYnY0WlNOcjh0dy9hWWtqeWFybnJPMWtwd3BiNkpySkpKcjZRL3Vjdi9CK3RFejhMRVQ1REViMTBKQzVlRWJ5THMNCkU3Z2xJeUNGN3lqdW5yWVZKcG8xYlRGYVVrWHduME5HZUNiZFhzZTg3YVgxSEpnUHpnZmdnYXE5NmpLOWVrSnFyc0FzOFcNCkZaNlY0OCtHQ3dZT0tTV2lyUGZ1bHlvdi9BREI5VklXN1NDeVZ6T25MZEZNZFVlckEyMjdjc1RoS1NmcjQzMUNCNTZITjcNCmFkdnRmNnR4alV0TXBoTjV5ZVBiRmxVZS9Wb2VQY1hNdXA4OXN3V2gvd3ZScklCbytUYXo2SzQxcGFzOEVObjFyemFxL3kNCkR5VnpSbkhrZTBoSkdmWXpSYW85WUJuY3hxTDgrV3Q0MWRRc0FHYXZSMHd2TUoreUxabkdMeWplV2lWZHBMY09BVkhqSDkNCkhMYytMN2doakhnVWJ0M0NYb1Z3SDJaS2d6UjlyaTdtT3dieit6Nmw3WnBaOVBqUnF5TUdxOWhhTm80dUR2MmptaEY2VlUNClBMU2Q3WTczWCtWTFAvWUZqbTBlUzJUbGFRQ3E2Vms0dzJqSHVWcXorcng4SllYb2tidFZXYnFYcmg3VzF5VGk4MXVRQUENCmxxdW1JbThCSXovbWh6Y2UxSkdFTFFHSXl5OEQyNHUzbWNjYUhaMWFmNVdwOWNVQmdPTzlxMGtwdVlYRHR6T0pPVE1aM1ENCk1SbnF1dVUzWmlEd2ZEaW1nN2xmS3BYaTFnMXF5ZlR3QUFBTUVBemhYR2FNV0EzWlRPWGpZaE9NSGR1OTRHZE1wc1dhajQNCjBsMmZ6YzdFWTlzWEdLZ01XMllvRXk5UVNSTDRPUmNMaUFKTDRLZGdZeGZzeVdma1U1d21TbGZXNjlrb0R2WTE0LzNWbWYNCmdDU1JMby9EZ01GbThhTSt6VFc4VmE1aXJSV1haRHhzV29EYjc3SGdiWWhPdDNvYjhBVllIeGpJNzdZNzF5QVM4V0tsUUkNClhCL2pnTW83UEIvcFMxVVhISEJyd3FCR3AzczlpOFpvQTQvaEtjSm9oS1ZINkYvRnZGTWNYdlM2Nk5wY1RYc1ZDMFVTM2QNCkJVY0taNTVvUUhVcnNQQUFBQUdIQnlZWFJvYVd0eVFFeEJVRlJQVUMxU00wZFVUa2xDVXdFQw0KLS0tLS1FTkQgT1BFTlNTSCBQUklWQVRFIEtFWS0tLS0t"
        ]

        for bad_key in bad_keys:
            self.kwargs.update({
                'ssh_private_key': bad_key
            })
            err = 'Error! ssh private key provided in invalid format'
            with self.assertRaises(InvalidArgumentValueError) as cm:
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
                        --ssh-private-key {ssh_private_key}
                        --enable-helm-operator
                        --helm-operator-version 1.2.0
                        --helm-operator-params \"--set git.ssh.secretName=gitops-privatekey-{operator_instance_name} --set tillerNamespace=kube-system\" ''')
            self.assertEqual(str(cm.exception), err)