# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Constants for the workload-orchestration support bundle feature."""

# Bundle defaults
DEFAULT_TAIL_LINES = 1000
DEFAULT_TIMEOUT_SECONDS = 600  # 10 minutes total
DEFAULT_API_TIMEOUT_SECONDS = 30  # per-API-call timeout
DEFAULT_LOG_TIMEOUT_SECONDS = 60  # per-container log fetch timeout
DEFAULT_MAX_LOG_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB per container
DEFAULT_MAX_BUNDLE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB total
BUNDLE_PREFIX = "wo-support-bundle"

# Retry defaults
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_BASE = 1.0  # seconds; retries wait 1s, 2s, 4s

# WO-relevant namespaces
WO_NAMESPACE = "workloadorchestration"
CERT_MANAGER_NAMESPACE = "cert-manager"
KUBE_SYSTEM_NAMESPACE = "kube-system"
DEFAULT_NAMESPACES = [KUBE_SYSTEM_NAMESPACE, WO_NAMESPACE, CERT_MANAGER_NAMESPACE]

# Protected namespaces — deploying workloads here is not recommended
PROTECTED_NAMESPACES = [
    "kube-system",
    "kube-public",
    "kube-node-lease",
    "azure-arc",
    "azure-arc-release",
    "azure-extensions",
    "gatekeeper-system",
    "azure-workload-identity-system",
    "cert-manager",
    "flux-system",
]

# DNS
DNS_SERVICE_LABEL = "k8s-app=kube-dns"
DNS_INTERNAL_HOST = "kubernetes.default.svc.cluster.local"
DNS_EXTERNAL_HOST = "mcr.microsoft.com"

# Test pod
TEST_POD_IMAGE = "busybox:1.36"
TEST_POD_TIMEOUT = 60  # seconds
TEST_POD_PREFIX = "wo-diag-"

# API groups for capability detection
API_GROUP_GATEKEEPER_TEMPLATES = "templates.gatekeeper.sh"
API_GROUP_GATEKEEPER_CONSTRAINTS = "constraints.gatekeeper.sh"
API_GROUP_KYVERNO = "kyverno.io"
API_GROUP_CERT_MANAGER = "cert-manager.io"
API_GROUP_SYMPHONY = "solution.symphony"
API_GROUP_OPENSHIFT_SECURITY = "security.openshift.io"
API_GROUP_METRICS = "metrics.k8s.io"

# cert-manager CRD detection
CERT_MANAGER_CRD_SUFFIX = ".cert-manager.io"
CERT_MANAGER_ISSUER_PLURAL = "clusterissuers"

# StorageClass annotations (check both v1 and beta)
SC_DEFAULT_ANNOTATION_V1 = "storageclass.kubernetes.io/is-default-class"
SC_DEFAULT_ANNOTATION_BETA = "storageclass.beta.kubernetes.io/is-default-class"

# PSA label prefix
PSA_LABEL_PREFIX = "pod-security.kubernetes.io/"

# Check categories
CATEGORY_CLUSTER_INFO = "cluster-info"
CATEGORY_NODE_HEALTH = "node-health"
CATEGORY_DNS_HEALTH = "dns-health"
CATEGORY_STORAGE = "storage"
CATEGORY_REGISTRY_ACCESS = "registry-access"
CATEGORY_CERT_MANAGER = "cert-manager"
CATEGORY_WO_COMPONENTS = "wo-components"
CATEGORY_ADMISSION_CONTROLLERS = "admission-controllers"
CATEGORY_CONNECTIVITY = "connectivity"
CATEGORY_RBAC = "rbac"

# Check result statuses
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARN = "WARN"
STATUS_SKIP = "SKIP"
STATUS_ERROR = "ERROR"

# Minimum resource requirements
MIN_CPU_CORES = 2
MIN_MEMORY_GI = 4
MIN_NODE_COUNT_PROD = 3

# Bundle folder structure
FOLDER_LOGS = "logs"
FOLDER_RESOURCES = "resources"
FOLDER_CHECKS = "checks"
FOLDER_CLUSTER_INFO = "cluster-info"
