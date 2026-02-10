# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

# Configuration paths
home_dir = os.path.expanduser("~")
CONFIG_DIR = os.path.join(home_dir, ".aks-agent")

# Constants to customized holmesgpt
CONST_AGENT_CONFIG_PATH_DIR_ENV_KEY = "HOLMES_CONFIGPATH_DIR"
CONST_AGENT_NAME = "AKS AGENT"
CONST_AGENT_NAME_ENV_KEY = "AGENT_NAME"
CONST_AGENT_CONFIG_FILE_NAME = "aksAgent.yaml"
CONST_PRIVACY_NOTICE_BANNER_ENV_KEY = "PRIVACY_NOTICE_BANNER"
# Privacy Notice Banner displayed in the format of rich.Console
CONST_PRIVACY_NOTICE_BANNER = (
    "When you send Microsoft this feedback, you agree we may combine this information, which might include other "
    "diagnostic data, to help improve Microsoft products and services. Processing of feedback data is governed by "
    "the Microsoft Products and Services Data Protection Addendum between your organization and Microsoft, and the "
    "feedback you submit is considered Personal Data under that addendum. "
    "Privacy Statement: https://go.microsoft.com/fwlink/?LinkId=521839"
)
# Holmesgpt leverages prometheus_api_client for prometheus toolsets and introduces bz2 library.
# Before libbz2-dev is bundled into azure cli python by https://github.com/Azure/azure-cli/pull/32163,
# we ignore loading prometheus toolset to avoid loading error of bz2 module.
CONST_DISABLE_PROMETHEUS_TOOLSET_ENV_KEY = "DISABLE_PROMETHEUS_TOOLSET"

# MCP Integration Constants (ported from previous change)
CONST_MCP_BINARY_NAME = "aks-mcp"
CONST_MCP_DEFAULT_PORT = 8003
CONST_MCP_DEFAULT_URL = "http://localhost:8003/sse"
CONST_MCP_MIN_VERSION = "0.0.10"
CONST_MCP_GITHUB_REPO = "Azure/aks-mcp"
CONST_MCP_BINARY_DIR = "bin"

# Kubernetes WebSocket exec protocol constants
RESIZE_CHANNEL = 4  # WebSocket channel for terminal resize messages
# WebSocket heartbeat configuration (matching kubectl client-go)
# Based on kubernetes/client-go/tools/remotecommand/websocket.go#L59-L65
# pingPeriod = 5 * time.Second
# pingReadDeadline = (pingPeriod * 12) + (1 * time.Second)
# The read deadline is calculated to allow up to 12 missed pings plus 1 second buffer
# This provides tolerance for network delays while detecting actual connection failures
HEARTBEAT_INTERVAL = 5.0                              # pingPeriod: 5 seconds between pings
HEARTBEAT_TIMEOUT = (HEARTBEAT_INTERVAL * 12) + 1    # pingReadDeadline: 61 seconds total timeout

AGENT_NAMESPACE = "kube-system"
AGENT_LABEL_SELECTOR = "app.kubernetes.io/name=aks-agent"
AKS_MCP_LABEL_SELECTOR = "app.kubernetes.io/name=aks-mcp"

# Helm Configuration
HELM_VERSION = "3.16.0"
