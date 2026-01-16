# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import sys
from typing import Dict, Optional

import pytest
from kubernetes.client.models import V1Node, V1NodeList, V1NodeSpec, V1ObjectMeta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from azext_connectedk8s.custom import get_kubernetes_distro, get_kubernetes_infra


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
