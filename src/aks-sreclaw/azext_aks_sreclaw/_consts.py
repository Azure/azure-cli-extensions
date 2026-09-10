# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

# Configuration paths
home_dir = os.path.expanduser("~")

AGENT_NAMESPACE = "kube-system"
AKS_SRECLAW_LABEL_SELECTOR = "app.kubernetes.io/name=aks-sreclaw"

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

# AKS SREClaw Version (shared by helm chart and docker image)
AKS_SRECLAW_VERSION = "0.0.0"

# Helm Configuration
HELM_VERSION = "3.16.0"
