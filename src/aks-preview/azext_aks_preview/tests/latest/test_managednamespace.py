# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

import azext_aks_preview.managednamespace as ns
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azure.cli.command_modules.acs.tests.latest.mocks import MockCLI, MockCmd
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)

class TestAddManagedNamespace(unittest.TestCase):
    def test_add_managed_namespace_with_invalid_labels(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "labels": "x",
        }
        err = "Invalid format 'x'. Expected format key=value."
        with self.assertRaises(ValueError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertEqual(str(cm.exception), err)
    
    def test_add_managed_namespace_with_invalid_annotations(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "labels": "x=y a=b",
            "annotations": "x",
        }
        err = "Invalid format 'x'. Expected format key=value."
        with self.assertRaises(ValueError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertEqual(str(cm.exception), err)

    def test_add_managed_namespace_with_missing_cpu_request(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_limit": "300m",
        }
        err = "Please specify --cpu-request, --cpu-limit, --memory-request, and --memory-limit."
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertEqual(str(cm.exception), err)
    
    def test_add_managed_namespace_with_invalid_ingress_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "deny",
        }
        err = "Invalid ingress_policy 'deny'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertIn(err, str(cm.exception))

    def test_add_managed_namespace_with_invalid_egress_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "DenyAll",
            "egress_policy": "deny",
        }
        err = "Invalid egress_policy 'deny'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertIn(err, str(cm.exception))
        
    def test_add_managed_namespace_with_invalid_adoption_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "DenyAll",
            "egress_policy": "AllowAll",
            "adoption_policy": "abc",
        }
        err = "Invalid adoption policy 'abc'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertIn(err, str(cm.exception))

    def test_add_managed_namespace_with_invalid_delete_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "DenyAll",
            "egress_policy": "AllowAll",
            "adoption_policy": "Always",
            "delete_policy": "abc",
        }
        err = "Invalid delete policy 'abc'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_add(cmd, None, raw_parameters, None, False)
        self.assertIn(err, str(cm.exception))

    # aks_managed_namespace_add(cmd, client, raw_parameters, headers, no_wait):
    # aks_managed_namespace_update(cmd, client, raw_parameters, headers, existedNamespace, no_wait)

class TestUpdateManagedNamespace(unittest.TestCase):
    def test_update_managed_namespace_with_invalid_ingress_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "deny",
        }
        err = "Invalid ingress_policy 'deny'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_update(cmd, None, raw_parameters, None, None, False)
        self.assertIn(err, str(cm.exception))

    def test_update_managed_namespace_with_invalid_egress_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "DenyAll",
            "egress_policy": "deny",
        }
        err = "Invalid egress_policy 'deny'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_update(cmd, None, raw_parameters, None, None, False)
        self.assertIn(err, str(cm.exception))
        
    def test_update_managed_namespace_with_invalid_adoption_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "DenyAll",
            "egress_policy": "AllowAll",
            "adoption_policy": "abc",
        }
        err = "Invalid adoption policy 'abc'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_update(cmd, None, raw_parameters, None, None, False)
        self.assertIn(err, str(cm.exception))

    def test_update_managed_namespace_with_invalid_delete_policy(self):
        register_aks_preview_resource_type()
        cli_ctx = MockCLI()
        cmd = MockCmd(cli_ctx)
        raw_parameters = {
            "resource_group_name": "test_rg",
            "cluster_name": "test_cluster",
            "name": "test_managed_namespace",
            "cpu_request": "300m",
            "cpu_limit": "500m",
            "memory_request": "1Gi",
            "memory_limit": "2Gi",
            "ingress_policy": "DenyAll",
            "egress_policy": "AllowAll",
            "adoption_policy": "Always",
            "delete_policy": "abc",
        }
        err = "Invalid delete policy 'abc'"
        with self.assertRaises(InvalidArgumentValueError) as cm:
            ns.aks_managed_namespace_update(cmd, None, raw_parameters, None, None, False)
        self.assertIn(err, str(cm.exception))
