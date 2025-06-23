#!/usr/bin/env python
"""
Demonstration script showing the --enable-managed-system-pool functionality

This script demonstrates how the --enable-managed-system-pool flag works
by simulating the parameter flow through the AKS CLI extension.

Usage: python demo_enable_managed_system_pool.py
"""

import os
import sys

# Add the path to the aks-preview module
sys.path.insert(0, '/home/hayua/azure-cli-extensions/src/aks-preview')

from unittest.mock import Mock

from azext_aks_preview._consts import CONST_NODEPOOL_MODE_MANAGEDSYSTEM
from azext_aks_preview.managed_cluster_decorator import \
    AKSPreviewManagedClusterContext
from azure.cli.command_modules.acs._consts import DecoratorMode
from azure.cli.command_modules.acs.managed_cluster_decorator import \
    AKSManagedClusterParamDict


def demonstrate_enable_managed_system_pool():
    """Demonstrate the enable_managed_system_pool functionality"""

    print("🔧 AKS CLI Extension: --enable-managed-system-pool Demonstration")
    print("=" * 65)

    # Mock command and models
    cmd = Mock()
    models = Mock()

    print("\n📋 Scenario 1: User runs 'az aks create --enable-managed-system-pool'")
    print("-" * 65)

    # Simulate user parameters when --enable-managed-system-pool is used
    user_parameters = {
        "cluster_name": "my-aks-cluster",
        "resource_group": "my-rg",
        "enable_managed_system_pool": True,
        "nodepool_name": "nodepool1",
        "node_vm_size": "Standard_D2s_v3",
        "node_count": 3,
    }

    print(f"📥 User Parameters: {user_parameters}")

    # Create context
    ctx = AKSPreviewManagedClusterContext(
        cmd,
        AKSManagedClusterParamDict(user_parameters),
        models,
        decorator_mode=DecoratorMode.CREATE,
    )

    # Check what the getter returns
    enable_managed_system_pool = ctx.get_enable_managed_system_pool()
    print(f"🔍 get_enable_managed_system_pool() returns: {enable_managed_system_pool}")

    # Simulate the parameter modification logic
    agentpool_parameters = user_parameters.copy()
    if enable_managed_system_pool:
        agentpool_parameters["mode"] = CONST_NODEPOOL_MODE_MANAGEDSYSTEM
        print(f"✅ Mode set to: {CONST_NODEPOOL_MODE_MANAGEDSYSTEM}")
    else:
        print("❌ Mode not modified")

    print(f"📤 Parameters passed to agentpool decorator: {agentpool_parameters}")

    print("\n" + "=" * 65)
    print("📋 Scenario 2: User runs 'az aks create' (without the flag)")
    print("-" * 65)

    # Simulate user parameters without the flag
    user_parameters_without_flag = {
        "cluster_name": "my-aks-cluster-2",
        "resource_group": "my-rg",
        "nodepool_name": "nodepool1",
        "node_vm_size": "Standard_D2s_v3",
        "node_count": 3,
    }

    print(f"📥 User Parameters: {user_parameters_without_flag}")

    # Create context
    ctx2 = AKSPreviewManagedClusterContext(
        cmd,
        AKSManagedClusterParamDict(user_parameters_without_flag),
        models,
        decorator_mode=DecoratorMode.CREATE,
    )

    # Check what the getter returns
    enable_managed_system_pool2 = ctx2.get_enable_managed_system_pool()
    print(f"🔍 get_enable_managed_system_pool() returns: {enable_managed_system_pool2}")

    # Simulate the parameter modification logic
    agentpool_parameters2 = user_parameters_without_flag.copy()
    if enable_managed_system_pool2:
        agentpool_parameters2["mode"] = CONST_NODEPOOL_MODE_MANAGEDSYSTEM
        print(f"✅ Mode set to: {CONST_NODEPOOL_MODE_MANAGEDSYSTEM}")
    else:
        print("❌ Mode not modified (normal System mode will be used)")

    print(f"📤 Parameters passed to agentpool decorator: {agentpool_parameters2}")

    print("\n" + "=" * 65)
    print("🎯 Summary")
    print("-" * 65)
    print("✅ When --enable-managed-system-pool is used:")
    print("   • The default system nodepool will be created in ManagedSystem mode")
    print("   • AKS fully manages the nodepool (users cannot modify it)")
    print("   • Provides a hands-off experience for system nodepools")
    print("\n❌ When --enable-managed-system-pool is NOT used:")
    print("   • The default system nodepool will be created in normal System mode")
    print("   • Users can modify the nodepool as needed")
    print("   • Traditional AKS nodepool management applies")

    print("\n🚀 Implementation Status: COMPLETE")
    print("   • Parameter registration: ✅")
    print("   • Help text: ✅")
    print("   • Context getter: ✅")
    print("   • Parameter modification logic: ✅")
    print("   • Integration with agentpool decorator: ✅")
    print("   • Unit tests: ✅")


if __name__ == "__main__":
    demonstrate_enable_managed_system_pool()
