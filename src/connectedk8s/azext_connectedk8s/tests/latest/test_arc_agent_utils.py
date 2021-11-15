# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import patch

from azext_connectedk8s._arc_agent_utils import ArcAgentUtils

class ArcAgentUtilsTest(unittest.TestCase):

    chart_path = "chart_path"
    subscription_id = 'test_sub_id'
    kubernetes_distro = "test_distribution"
    kubernetes_infra = "generic"
    resource_group_name = "test_rg"
    cluster_name = "test_cluster"
    location = "test_location"
    onboarding_tenant_id = "test_onboarding_tenant_id"
    private_key_pem = "test_private_key_pem"
    no_wait = False
    cloud_name = "test"
    enable_custom_locations = True
    custom_locations_oid = "test_custom_locations_oid"
    release_namespace = "test_release_namespace"

    @patch('azext_connectedk8s._arc_agent_utils._execute_helm_command', return_value=True)
    def test_execute_arc_agent_install(self, input):
        arc_agent = ArcAgentUtils()
        kube_config = "test_config"
        arc_agent.set_kube_configuration(kube_config)

        proxy_details = {}
        proxy_details['https_proxy'] = "httpsProxy"
        proxy_details['http_proxy'] = "httpProxy"
        proxy_details['no_proxy'] = "noProxy"
        proxy_details['proxy_cert'] = "cert"
        proxy_details['disable_proxy'] = True

        arc_agent.set_proxy_configuration(proxy_details)
        arc_agent.set_kube_configuration("testKubeConfig", "testContext")
        arc_agent.set_auto_upgrade(True)
        arc_agent.set_values_file("values.txt")

        try:
            arc_agent.execute_arc_agent_install(self.chart_path, self.subscription_id, self.kubernetes_distro,
                                                self.kubernetes_infra, self.resource_group_name, self.cluster_name,
                                                self.location, self.onboarding_tenant_id, self.private_key_pem,
                                                self.no_wait, self.cloud_name, self.enable_custom_locations,
                                                self.custom_locations_oid)
        except Exception:
            self.fail("No error should have occured")

    @patch('azext_connectedk8s._arc_agent_utils._execute_helm_command', return_value=True)
    def test_execute_arc_agent_update(self, input):
        arc_agent = ArcAgentUtils()
        try:
            arc_agent.execute_arc_agent_update(self.chart_path, self.release_namespace)
        except Exception:
            self.fail("No error should have occured")

    @patch('azext_connectedk8s._arc_agent_utils._execute_helm_command', return_value=True) # check again
    def test_execute_arc_agent_upgrade(self, input):
        arc_agent = ArcAgentUtils()

        existing_user_values = "{'global': {'isProxyEnabled' : 'True', 'httpProxy': 'testProxy'," \
                               " 'kubernetesDistro': 'default', 'kubernetesInfra' : 'generic' } }"
        try:
            arc_agent.execute_arc_agent_upgrade(self.chart_path, self.release_namespace, 100, existing_user_values)
        except Exception:
            self.fail("No error should have occured")

    @patch('azext_connectedk8s._arc_agent_utils._execute_helm_command', return_value=True)
    def test_execute_arc_agent_enable_features(self, input):
        arc_agent = ArcAgentUtils()

        try:
            arc_agent.execute_arc_agent_enable_features(self.chart_path, self.release_namespace, True,
                                                        True, True, self.custom_locations_oid,
                                                        "test_azrbac_client_id", "test_azrbac_client_secret",
                                                        True)
        except Exception:
            self.fail("No error should have occured")

    @patch('azext_connectedk8s._arc_agent_utils._execute_helm_command', return_value=True)
    def test_execute_arc_agent_disable_features(self, input):
        arc_agent = ArcAgentUtils()

        try:
            arc_agent.execute_arc_agent_disable_features(self.chart_path, self.release_namespace, True,
                                                         True, True)
        except Exception:
            self.fail("No error should have occured")

    @patch('azext_connectedk8s._arc_agent_utils._execute_helm_command', return_value=True)
    @patch('azext_connectedk8s._kube_core_utils.ensure_namespace_cleanup', return_value=True)
    def test_execute_delete_arc_agents(self, input, input2):
        arc_agent = ArcAgentUtils()

        try:
            arc_agent.execute_delete_arc_agents(self.chart_path, None)
        except Exception:
            self.fail("No error should have occured")
