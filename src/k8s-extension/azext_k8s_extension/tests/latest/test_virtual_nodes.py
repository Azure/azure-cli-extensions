# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import yaml
from kubernetes.client.exceptions import ApiException
from knack.util import CLIError

from azext_k8s_extension import custom
from azext_k8s_extension.partner_extensions.VirtualNodes import VirtualNodes, _kubernetes_client

PREFIX = "azext_k8s_extension.partner_extensions.VirtualNodes."
INFRA = "vn2-virtualnode"
NODE = INFRA + "-0"
NAMESPACE = "vn-system"


def metadata(name, namespace=NAMESPACE, uid="node-uid", **kwargs):
    return SimpleNamespace(name=name, namespace=namespace, uid=uid, **kwargs)


def virtual_node(name=NODE):
    return SimpleNamespace(metadata=metadata(name, labels={
        "microsoft.containerinstance.virtualnode": "true",
        "virtualization": "virtualnode2",
        "microsoft.containerinstance.virtualnode.podname": name,
        "microsoft.containerinstance.virtualnode.podns": NAMESPACE,
    }))


class VirtualNodesDeleteTest(unittest.TestCase):
    def setUp(self):
        self.cmd = MagicMock()
        self.client = MagicMock()
        self.partner = VirtualNodes()
        self.client.get.return_value = SimpleNamespace(
            name="vn2", extension_type="microsoft.virtualnodes",
            scope=SimpleNamespace(cluster=SimpleNamespace(release_namespace=NAMESPACE)),
        )
        self.sts = SimpleNamespace(metadata=metadata(INFRA, uid="sts-uid", annotations={
            "meta.helm.sh/release-name": "vn2",
            "meta.helm.sh/release-namespace": NAMESPACE,
        }))
        self.nodes = {NODE: virtual_node()}
        self.pods = {}
        self.core, self.apps = MagicMock(), MagicMock()
        self.apps.list_stateful_set_for_all_namespaces.side_effect = (
            lambda **_: SimpleNamespace(items=[self.sts] if self.sts else [])
        )
        self.core.list_node.side_effect = lambda **_: SimpleNamespace(items=list(self.nodes.values()))
        self.core.list_pod_for_all_namespaces.side_effect = lambda field_selector, **_: SimpleNamespace(
            items=self.pods.get(field_selector.split("=", 1)[1], [])
        )
        for patcher in (
            patch(PREFIX + "user_confirmation_factory"),
            patch("azext_k8s_extension.custom.ExtensionFactory", return_value=self.partner),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        cluster = patch(PREFIX + "_kubernetes_client")
        cluster.start().return_value.__enter__.return_value = (self.core, self.apps)
        self.addCleanup(cluster.stop)

    def run_delete(self, **kwargs):
        return custom.delete_k8s_extension(
            self.cmd, self.client, "rg", "cluster", "vn2", "managedClusters", yes=True, **kwargs
        )

    def test_all_assigned_pod_phases_block_even_with_force_or_no_wait(self):
        second = INFRA + "-1"
        self.nodes[second] = virtual_node(second)
        for index, phase in enumerate(("Pending", "Running", "Succeeded", "Failed", "Unknown")):
            node = NODE if index % 2 else second
            self.pods.setdefault(node, []).append(SimpleNamespace(
                metadata=metadata(f"pod-{index}", namespace=f"ns-{index}", deletion_timestamp=None),
                status=SimpleNamespace(phase=phase),
            ))
        self.pods[NODE].append(SimpleNamespace(
            metadata=metadata("terminating", namespace="other", deletion_timestamp="now"),
            status=SimpleNamespace(phase="Running"),
        ))
        for flags in ({}, {"no_wait": True}, {"force": True}, {"no_wait": True, "force": True}):
            with self.subTest(flags=flags), self.assertRaises(CLIError) as raised:
                self.run_delete(**flags)
            for node, pods in self.pods.items():
                for pod in pods:
                    self.assertIn(f"{pod.metadata.namespace}/{pod.metadata.name} on Node {node}", str(raised.exception))
        self.client.begin_delete.assert_not_called()
        self.core.delete_node.assert_not_called()

    def test_no_assigned_pods_allows_azure_delete_without_kubernetes_writes(self):
        foreign = virtual_node("other-virtualnode-0")
        self.nodes[foreign.metadata.name] = foreign
        self.pods[foreign.metadata.name] = [SimpleNamespace(metadata=metadata("foreign-workload"))]
        self.assertIs(self.run_delete(), self.client.begin_delete.return_value)
        self.client.begin_delete.assert_called_once()
        self.client.begin_delete.return_value.result.assert_not_called()
        self.core.list_pod_for_all_namespaces.assert_called_once_with(
            field_selector=f"spec.nodeName={NODE}", _request_timeout=30
        )
        self.core.delete_node.assert_not_called()
        self.core.patch_node.assert_not_called()

    def test_no_nodes_with_or_without_statefulset_allows_uninstall(self):
        self.nodes.clear()
        for statefulset in (self.sts, None):
            with self.subTest(statefulset=statefulset):
                self.sts = statefulset
                self.client.begin_delete.reset_mock()
                self.run_delete()
                self.client.begin_delete.assert_called_once()
        self.core.list_pod_for_all_namespaces.assert_not_called()

    def test_mixed_case_azure_name_matches_lowercase_helm_release(self):
        azure_name = "testExtAndHelm"
        release_name = "testextandhelm"
        node = release_name + "-virtualnode-0"
        self.client.get.return_value.name = azure_name
        self.sts.metadata.name = release_name + "-virtualnode"
        self.sts.metadata.annotations["meta.helm.sh/release-name"] = release_name
        self.nodes = {node: virtual_node(node)}
        self.pods[node] = [SimpleNamespace(metadata=metadata("workload", namespace="customer"))]
        self.apps.list_stateful_set_for_all_namespaces.side_effect = lambda label_selector, **_: SimpleNamespace(
            items=[self.sts] if self.sts and label_selector == f"app.kubernetes.io/instance={release_name}" else []
        )

        def delete():
            return custom.delete_k8s_extension(
                self.cmd, self.client, "rg", "cluster", azure_name, "managedClusters", yes=True
            )

        with self.assertRaisesRegex(CLIError, f"customer/workload on Node {node}"):
            delete()
        self.client.begin_delete.assert_not_called()

        statefulset = self.sts
        self.sts = None
        with self.assertRaisesRegex(CLIError, "Cannot establish ownership"):
            delete()
        self.client.begin_delete.assert_not_called()

        self.sts = statefulset
        self.pods.clear()
        delete()
        self.apps.list_stateful_set_for_all_namespaces.assert_called_with(
            label_selector=f"app.kubernetes.io/instance={release_name}", _request_timeout=30
        )
        self.client.get.assert_called_with("rg", "Microsoft.ContainerService", "managedClusters", "cluster", azure_name)
        self.client.begin_delete.assert_called_once_with(
            "rg", "Microsoft.ContainerService", "managedClusters", "cluster", azure_name, force_delete=False
        )

    def test_flags_keep_existing_sdk_behavior_after_pod_check(self):
        for no_wait, force in ((True, False), (False, True), (True, True)):
            with self.subTest(no_wait=no_wait, force=force):
                self.core.list_pod_for_all_namespaces.reset_mock()
                self.run_delete(no_wait=no_wait, force=force)
                kwargs = self.client.begin_delete.call_args.kwargs
                self.assertEqual(kwargs["force_delete"], force)
                self.assertEqual(kwargs.get("polling"), False if no_wait else None)
                self.core.list_pod_for_all_namespaces.assert_called_once()
        self.core.delete_node.assert_not_called()

    def test_api_error_prevents_azure_delete(self):
        for operation in (self.apps.list_stateful_set_for_all_namespaces, self.core.list_node,
                          self.core.list_pod_for_all_namespaces):
            with self.subTest(operation=operation):
                original = operation.side_effect
                operation.side_effect = ApiException(status=403, reason="Forbidden")
                with self.assertRaises(ApiException):
                    self.run_delete()
                operation.side_effect = original
        self.client.begin_delete.assert_not_called()

    def test_missing_ownership_or_statefulset_blocks_deletion(self):
        original = copy.deepcopy(self.nodes[NODE])
        for label in tuple(original.metadata.labels):
            with self.subTest(label=label):
                self.nodes[NODE] = copy.deepcopy(original)
                del self.nodes[NODE].metadata.labels[label]
                with self.assertRaisesRegex(CLIError, "Cannot establish ownership"):
                    self.run_delete()
        self.nodes[NODE] = original
        self.sts = None
        with self.assertRaisesRegex(CLIError, "Cannot establish ownership"):
            self.run_delete()
        self.client.begin_delete.assert_not_called()


class VirtualNodesCredentialsTest(unittest.TestCase):
    def test_uses_target_user_credentials_isolated_client_and_azurecli_login(self):
        for args in (["get-token", "-l", "devicecode"], ["get-token", "--login", "devicecode"], ["get-token"]):
            kubeconfig = {"users": [{"name": "user", "user": {"exec": {"command": "kubelogin", "args": args}}}]}
            aks = MagicMock()
            aks.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
                SimpleNamespace(value=yaml.safe_dump(kubeconfig).encode("utf-8"))
            ]
            with self.subTest(args=args), patch(PREFIX + "get_mgmt_service_client", return_value=aks), \
                    patch(PREFIX + "config.new_client_from_config_dict") as load, \
                    patch(PREFIX + "config.load_kube_config") as global_load:
                with _kubernetes_client(MagicMock(), "target-rg", "target-cluster"):
                    pass
                aks.managed_clusters.list_cluster_user_credentials.assert_called_once_with(
                    "target-rg", "target-cluster", format="exec"
                )
                actual = load.call_args.args[0]["users"][0]["user"]["exec"]["args"]
                self.assertIn("azurecli", actual)
                self.assertNotIn("devicecode", actual)
                self.assertFalse(load.call_args.kwargs["persist_config"])
                load.return_value.__exit__.assert_called_once()
                global_load.assert_not_called()

    def test_kubernetes_error_is_fail_closed_and_client_is_closed(self):
        aks = MagicMock()
        aks.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
            SimpleNamespace(value=b"users: []")
        ]
        with patch(PREFIX + "get_mgmt_service_client", return_value=aks), \
                patch(PREFIX + "config.new_client_from_config_dict") as load:
            with self.assertRaisesRegex(CLIError, "Cannot access the target Kubernetes API"):
                with _kubernetes_client(MagicMock(), "rg", "cluster"):
                    raise ApiException(status=403, reason="Forbidden")
            load.return_value.__exit__.assert_called_once()

    def test_unauthenticated_or_insecure_credentials_are_rejected(self):
        aks = MagicMock()
        aks.managed_clusters.list_cluster_user_credentials.return_value.kubeconfigs = [
            SimpleNamespace(value=b"users: []")
        ]
        for verify_ssl, token in ((False, "token"), (True, None)):
            with self.subTest(verify_ssl=verify_ssl, token=token), \
                    patch(PREFIX + "get_mgmt_service_client", return_value=aks), \
                    patch(PREFIX + "config.new_client_from_config_dict") as load:
                api = load.return_value.__enter__.return_value
                api.configuration = SimpleNamespace(
                    verify_ssl=verify_ssl, api_key={"authorization": token}, cert_file=None, key_file=None
                )
                with self.assertRaisesRegex(CLIError, "TLS-verified"):
                    with _kubernetes_client(MagicMock(), "rg", "cluster"):
                        self.fail("Unsafe credentials must not reach Kubernetes.")
