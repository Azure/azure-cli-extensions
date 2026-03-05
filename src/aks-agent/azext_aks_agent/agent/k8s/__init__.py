# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Kubernetes managers package for AKS agent.

This package contains specialized manager classes for different Kubernetes operations:
- HelmManager: OS-agnostic helm binary management and operations
- AKSAgentManager: AKS agent deployment, upgrading, and lifecycle management
- exec_command_in_pod: Standalone function for pod command execution
"""

from .aks_agent_manager import AKSAgentManager, AKSAgentManagerClient
from .helm_manager import HelmManager, create_helm_manager
from .pod_exec import exec_command_in_pod

__all__ = [
    "HelmManager",
    "AKSAgentManager",
    "AKSAgentManagerClient",
    "exec_command_in_pod",
    "create_helm_manager",
]
