# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from typing import Dict, Optional
from unittest.mock import MagicMock

import pytest
from kubernetes.client.models import V1Node, V1NodeList, V1NodeSpec, V1ObjectMeta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from azext_connectedk8s.custom import (
    expand_proxy_skip_range_keywords,
    get_kubernetes_distro,
    get_kubernetes_infra,
)


def create_node(
    provider_id: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None,
) -> V1Node:
    spec = V1NodeSpec(provider_id=provider_id)
    metadata = V1ObjectMeta(labels=labels or {}, annotations=annotations or {})
    return V1Node(spec=spec, metadata=metadata)


@pytest.mark.parametrize(
    "provider_id, expected",
    [
        ("k3s://node1", "k3s"),
        ("kind://node1", "kind"),
        ("azure://node1", "azure"),
        ("gce://node1", "gcp"),
        ("aws://node1", "aws"),
        ("unknown://node1", "unknown"),
        (None, "generic"),
    ],
)
def test_get_kubernetes_infra(provider_id, expected):
    node = create_node(provider_id) if provider_id is not None else None
    api_response = V1NodeList(items=[node]) if node else None
    assert get_kubernetes_infra(api_response) == expected


def test_empty_items():
    api_response = V1NodeList(items=[])
    assert get_kubernetes_infra(api_response) == "generic"


def test_invalid_provider_id():
    node = create_node(None)
    api_response = V1NodeList(items=[node])
    assert get_kubernetes_infra(api_response) == "None"


# --------------------- Tests for get_kubernetes_distro ---------------------
@pytest.mark.parametrize(
    "labels, annotations, provider_id, expected",
    [
        ({"node.openshift.io/os_id": "rhcos"}, {}, None, "openshift"),
        ({"kubernetes.azure.com/node-image-version": "2022.11.01"}, {}, None, "aks"),
        ({"cloud.google.com/gke-nodepool": "default-pool"}, {}, None, "gke"),
        ({"cloud.google.com/gke-os-distribution": "cos"}, {}, None, "gke"),
        ({"eks.amazonaws.com/nodegroup": "nodegroup-1"}, {}, None, "eks"),
        ({"minikube.k8s.io/version": "v1.25.0"}, {}, None, "minikube"),
        ({}, {"node.aksedge.io/distro": "aks_edge_k3s"}, None, "aks_edge_k3s"),
        ({}, {"node.aksedge.io/distro": "aks_edge_k8s"}, None, "aks_edge_k8s"),
        ({}, {}, "kind://node1", "kind"),
        ({}, {}, "k3s://node1", "k3s"),
        ({}, {"rke.cattle.io/external-ip": "192.168.1.1"}, None, "rancher_rke"),
        ({}, {"rke.cattle.io/internal-ip": "10.0.0.1"}, None, "rancher_rke"),
        ({}, {}, None, "generic"),
    ],
)
def test_get_kubernetes_distro(labels, annotations, provider_id, expected):
    node = create_node(provider_id=provider_id, labels=labels, annotations=annotations)
    api_response = V1NodeList(items=[node])
    assert get_kubernetes_distro(api_response) == expected


def test_distro_empty_items():
    api_response = V1NodeList(items=[])
    assert get_kubernetes_distro(api_response) == "generic"


def test_distro_invalid_metadata():
    node = create_node(provider_id="aws://node1", labels=None, annotations=None)
    api_response = V1NodeList(items=[node])
    assert get_kubernetes_distro(api_response) == "generic"


# --------------------- Tests for expand_proxy_skip_range_keywords ---------------------
def _proxy_cmd(active_directory="https://login.microsoftonline.com"):
    cmd = MagicMock()
    cmd.cli_ctx.cloud.endpoints.active_directory = active_directory
    return cmd


ARC_PUBLIC = (
    ".his.arc.azure.com,"
    ".dp.kubernetesconfiguration.azure.com,"
    ".guestconfiguration.azure.com"
)


def test_expand_arc_keyword_public_cloud():
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc") == ARC_PUBLIC


@pytest.mark.parametrize("keyword", ["Arc", "arc", "ARC", " aRc "])
def test_expand_arc_keyword_is_case_and_space_insensitive(keyword):
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), keyword) == ARC_PUBLIC


def test_expand_arc_keyword_preserves_other_entries():
    out = expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc,10.0.0.0/16,.svc")
    assert out == ARC_PUBLIC + ",10.0.0.0/16,.svc"


def test_expand_arc_keyword_china_cloud():
    cmd = _proxy_cmd("https://login.chinacloudapi.cn")
    out = expand_proxy_skip_range_keywords(cmd, "Arc")
    assert out == (
        ".his.arc.azure.cn,"
        ".dp.kubernetesconfiguration.azure.cn,"
        ".guestconfiguration.azure.cn"
    )


def test_expand_arc_keyword_usgov_cloud():
    cmd = _proxy_cmd("https://login.microsoftonline.us")
    out = expand_proxy_skip_range_keywords(cmd, "Arc")
    assert out == (
        ".his.arc.azure.us,"
        ".dp.kubernetesconfiguration.azure.us,"
        ".guestconfiguration.azure.us"
    )


def test_expand_no_keyword_returns_unchanged():
    val = "10.0.0.0/16,.svc,localhost"
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), val) == val


def test_expand_empty_returns_unchanged():
    assert expand_proxy_skip_range_keywords(_proxy_cmd(), "") == ""


def test_expand_arc_keyword_deduplicates():
    out = expand_proxy_skip_range_keywords(_proxy_cmd(), "Arc,Arc")
    assert out == ARC_PUBLIC
