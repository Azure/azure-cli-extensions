import unittest
from unittest import mock
from azure.core.serialization import NULL as AzureCoreNull
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.core.util import CLIError
import azext_acrcache.cache as cache


class TestCacheUtilityFunctions(unittest.TestCase):
    """Test utility functions for cache operations"""
    
    def test_create_kql_basic(self):
        """Test KQL query generation with different filters"""
        self.assertEqual(cache._create_kql(), "Tags")
        self.assertEqual(cache._create_kql(starts_with="foo"), "Tags | where Name startswith 'foo'")
        self.assertEqual(cache._create_kql(ends_with="bar"), "Tags | where Name endswith 'bar'")
        self.assertEqual(cache._create_kql(contains="baz"), "Tags | where Name contains 'baz'")
        self.assertEqual(cache._create_kql(starts_with="foo", ends_with="bar"), 
                        "Tags | where Name startswith 'foo' and Name endswith 'bar'")
        self.assertEqual(cache._create_kql(starts_with="foo", contains="baz"), 
                        "Tags | where Name startswith 'foo' and Name contains 'baz'")
        self.assertEqual(cache._create_kql(ends_with="bar", contains="baz"), 
                        "Tags | where Name endswith 'bar' and Name contains 'baz'")
        self.assertEqual(cache._create_kql(starts_with="foo", ends_with="bar", contains="baz"), 
                        "Tags | where Name startswith 'foo' and Name endswith 'bar' and Name contains 'baz'")

    def test_separate_params(self):
        """Test parameter extraction from KQL queries"""
        q = "Tags | where Name startswith 'foo' and Name endswith 'bar' and Name contains 'baz'"
        starts_with, ends_with, contains = cache._separate_params(q)
        self.assertEqual(starts_with, "foo")
        self.assertEqual(ends_with, "bar")
        self.assertEqual(contains, "baz")


class TestCacheOperations(unittest.TestCase):
    """Test cache CRUD operations with mocked clients"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = mock.Mock()
        self.cmd.cli_ctx = mock.Mock()
        self.client = mock.Mock()
        
    @mock.patch('azext_acrcache.cache.get_resource_group_name_by_registry_name')
    def test_acr_cache_show_calls_client_get(self, mock_get_rg):
        """Test that cache show calls the correct client method"""
        mock_get_rg.return_value = "mockrg"
        cache.acr_cache_show(self.cmd, self.client, "mockRegistry", "mockCacheRule")
        self.client.get.assert_called_once_with(
            resource_group_name="mockrg", 
            registry_name="mockRegistry", 
            cache_rule_name="mockCacheRule"
        )

    @mock.patch('azext_acrcache.cache.get_resource_group_name_by_registry_name')
    def test_acr_cache_list_calls_client_list(self, mock_get_rg):
        """Test that cache list calls the correct client method"""
        mock_get_rg.return_value = "mockrg"
        cache.acr_cache_list(self.cmd, self.client, "mockRegistry")
        self.client.list.assert_called_once_with(
            resource_group_name="mockrg", 
            registry_name="mockRegistry"
        )

    @mock.patch('azext_acrcache.cache.get_resource_group_name_by_registry_name')
    def test_acr_cache_delete_calls_client_begin_delete(self, mock_get_rg):
        """Test that cache delete calls the correct client method"""
        mock_get_rg.return_value = "mockrg"
        cache.acr_cache_delete(self.cmd, self.client, "mockRegistry", "mockCacheRule")
        self.client.begin_delete.assert_called_once_with(
            resource_group_name="mockrg", 
            registry_name="mockRegistry", 
            cache_rule_name="mockCacheRule"
        )
class TestCacheCreateValidation(unittest.TestCase):
    """Test cache creation validation logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = mock.Mock()
        self.cmd.cli_ctx = mock.Mock()
        self.client = mock.Mock()
        
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_create_raises_for_missing_rg(self, mock_get_registry):
        """Test that cache create raises error when resource group cannot be determined"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups//providers/xxx"  # Missing RG name
        mock_get_registry.return_value = (mock_registry, None)
        
        with self.assertRaises(CLIError):
            cache.acr_cache_create(
                self.cmd, self.client, "mockRegistry", "mockCacheRule1", "mockRepo1", "mockRepo2", 
                resource_group_name=None, sync="activesync", 
                starts_with="foo", ends_with=None, contains=None
            )

    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_create_mutually_exclusive_artifact_types(self, mock_get_registry):
        """Test that cache create raises error for mutually exclusive artifact type filters"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/xxx"
        mock_get_registry.return_value = (mock_registry, None)
        
        with self.assertRaises(CLIError):
            cache.acr_cache_create(
                self.cmd, self.client, "mockRegistry", "mockCacheRule", "mockRepo1", "mockRepo2", 
                resource_group_name="mockrg", sync="activesync", 
                include_artifact_types="a", exclude_artifact_types="b"
            )

    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_create_mutually_exclusive_image_types(self, mock_get_registry):
        """Test that cache create raises error for mutually exclusive image type filters"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/xxx"
        mock_get_registry.return_value = (mock_registry, None)
        
        with self.assertRaises(CLIError):
            cache.acr_cache_create(
                self.cmd, self.client, "mockRegistry", "mockCacheRule1", "mockRepo1", "mockRepo2", 
                resource_group_name="mockrg", sync="activesync", 
                include_image_types="a", exclude_image_types="b"
            )

    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_create_sync_referrers_requires_activesync(self, mock_get_registry):
        """Test that sync referrers requires active sync mode"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/xxx"
        mock_get_registry.return_value = (mock_registry, None)
        
        with self.assertRaises(CLIError):
            cache.acr_cache_create(
                self.cmd, self.client, "mockRegistry", "mockCacheRule1", "mockRepo1", "mockRepo2", 
                resource_group_name="mockrg", sync="passivesync", 
                sync_referrers="enabled"
            )


class TestCacheUpdateValidation(unittest.TestCase):
    """Test cache update validation logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = mock.Mock()
        self.cmd.cli_ctx = mock.Mock()
        self.client = mock.Mock()
        
        # Set up mock cache rule
        self.dummy_rule = mock.Mock()
        self.dummy_rule.properties = mock.Mock()
        self.dummy_rule.properties.sync_mode = "activeSync"
        self.dummy_rule.properties.sync_referrers = "Disabled"
        self.dummy_rule.properties.artifact_sync_filters = None
        self.dummy_rule.properties.credential_set_resource_id = None
        
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_update_custom_mutually_exclusive_artifact_types(self, mock_get_registry):
        """Test that cache update raises error for mutually exclusive artifact type filters"""
        mock_get_registry.return_value = (mock.Mock(id="id"), "mockrg")
        self.client.get.return_value = self.dummy_rule
        
        with self.assertRaises(CLIError):
            cache.acr_cache_update_custom(
                self.cmd, self.client, "mockRegistry", "mockCacheRule1",
                include_artifact_types="a", exclude_artifact_types="b"
            )

    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_update_custom_mutually_exclusive_image_types(self, mock_get_registry):
        """Test that cache update raises error for mutually exclusive image type filters"""
        mock_get_registry.return_value = (mock.Mock(id="id"), "mockrg")
        self.client.get.return_value = self.dummy_rule
        
        with self.assertRaises(CLIError):
            cache.acr_cache_update_custom(
                self.cmd, self.client, "mockRegistry", "mockCacheRule1",
                include_image_types="a", exclude_image_types="b"
            )


class TestCacheSync(unittest.TestCase):
    """Test cache sync operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = mock.Mock()
        self.cmd.cli_ctx = mock.Mock()
        self.client = mock.Mock()
        
    @mock.patch('azext_acrcache.cache.get_resource_group_name_by_registry_name')
    def test_acr_cache_sync_calls_import_image(self, mock_get_rg):
        """Test that cache sync calls the import image operation"""
        mock_get_rg.return_value = "mockrg"
        
        # Set up mock cache rule
        dummy_rule = mock.Mock()
        dummy_rule.id = "ruleid"
        dummy_rule.source_repository = "repo/source"
        dummy_rule.target_repository = "repo/target"
        
        self.client.cache_rules.get.return_value = dummy_rule
        self.client.registries.begin_import_image = mock.Mock()

        cache.acr_cache_sync(self.cmd, self.client, "mockRegistry", "mockCacheRule1", "tag1")

        self.client.registries.begin_import_image.assert_called_once()
        
        # Verify the import parameters
        call_args = self.client.registries.begin_import_image.call_args
        self.assertEqual(call_args[1]['resource_group_name'], "mockrg")
        self.assertEqual(call_args[1]['registry_name'], "mockRegistry")

        # Verify import parameters structure
        params = call_args[1]['parameters']
        self.assertEqual(params.mode, "Force")
        self.assertEqual(params.target_tags, ["repo/target:tag1"])
        self.assertEqual(params.source.cache_rule_resource_id, "ruleid")

class TestIdentityProcessing(unittest.TestCase):
    """Test identity parameter processing functionality"""

    def test_process_assign_identity_parameter_none(self):
        """Test process_assign_identity_parameter returns None when no identity provided"""
        result = cache.process_assign_identity_parameter(None)
        self.assertIsNone(result)

        result = cache.process_assign_identity_parameter("")
        self.assertIsNone(result)

    def test_process_assign_identity_parameter_valid(self):
        """Test process_assign_identity_parameter with valid resource ID"""
        resource_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity"

        result = cache.process_assign_identity_parameter(resource_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "UserAssigned")
        self.assertIn(resource_id, result.user_assigned_identities)
        self.assertIsInstance(result.user_assigned_identities[resource_id], cache.UserIdentityProperties)
    
    def test_process_assign_identity_parameter_invalid(self):
        """Test process_assign_identity_parameter raises error for invalid resource ID"""
        invalid_ids = [
            "invalid-resource-id",
            "/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity",
            "subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity"
        ]
        
        for invalid_id in invalid_ids:
            with self.assertRaises(CLIError) as context:
                cache.process_assign_identity_parameter(invalid_id)
            self.assertIn("Invalid user-assigned managed identity resource ID", str(context.exception))
    
    def test_is_valid_user_assigned_managed_identity_resource_id(self):
        """Test resource ID validation function"""
        # Valid resource IDs
        valid_ids = [
            "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity",
            "/subscriptions/abcdefgh-1234-5678-9012-123456789012/resourceGroups/test-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/test-identity"
        ]
        
        for valid_id in valid_ids:
            self.assertTrue(cache.is_valid_user_assigned_managed_identity_resource_id(valid_id))
        
        # Invalid resource IDs
        invalid_ids = [
            "invalid-resource-id",
            "/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity",
            "subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity",
            ""
        ]
        
        for invalid_id in invalid_ids:
            self.assertFalse(cache.is_valid_user_assigned_managed_identity_resource_id(invalid_id))


class TestCacheCreateWithIdentity(unittest.TestCase):
    """Test cache creation with identity parameter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = mock.Mock()
        self.cmd.cli_ctx = mock.Mock()
        self.client = mock.Mock()
        self.valid_identity_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity"
        
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    @mock.patch('azext_acrcache.cache.user_confirmation')
    def test_acr_cache_create_with_valid_identity(self, mock_confirmation, mock_get_registry):
        """Test cache creation with valid identity"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.ContainerRegistry/registries/registry1"
        mock_get_registry.return_value = (mock_registry, None)
        
        cache.acr_cache_create(
            self.cmd, self.client, "mockRegistry", "mockCacheRule", "source/repo", "target/repo",
            resource_group_name="mockrg", 
            assign_identity=self.valid_identity_id,
            sync="activesync",
            yes=True
        )
        
        # Verify client.begin_create was called
        self.client.begin_create.assert_called_once()
        
        # Extract the cache rule from the call
        call_args = self.client.begin_create.call_args[1]
        cache_rule = call_args['cache_rule_create_parameters']
        
        # Verify identity was set
        self.assertIsNotNone(cache_rule.identity)
        self.assertEqual(cache_rule.identity.type, "UserAssigned")
        self.assertIn(self.valid_identity_id, cache_rule.identity.user_assigned_identities)
    
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_create_with_invalid_identity(self, mock_get_registry):
        """Test cache creation with invalid identity raises error"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.ContainerRegistry/registries/registry1"
        mock_get_registry.return_value = (mock_registry, None)
        
        with self.assertRaises(CLIError):
            cache.acr_cache_create(
                self.cmd, self.client, "mockRegistry", "mockCacheRule", "source/repo", "target/repo",
                resource_group_name="mockrg", 
                assign_identity="invalid-identity-id"
            )
    
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    @mock.patch('azext_acrcache.cache.user_confirmation')
    def test_acr_cache_create_without_identity(self, mock_confirmation, mock_get_registry):
        """Test cache creation without identity works normally"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.ContainerRegistry/registries/registry1"
        mock_get_registry.return_value = (mock_registry, None)
        
        cache.acr_cache_create(
            self.cmd, self.client, "mockRegistry", "mockCacheRule", "source/repo", "target/repo",
            resource_group_name="mockrg",
            sync="activesync",
            yes=True
        )
        
        # Verify client.begin_create was called
        self.client.begin_create.assert_called_once()
        
        # Extract the cache rule from the call
        call_args = self.client.begin_create.call_args[1]
        cache_rule = call_args['cache_rule_create_parameters']
        
        # Verify identity is None
        self.assertIsNone(cache_rule.identity)

class TestCacheUpdateWithIdentity(unittest.TestCase):
    """Test cache update with identity parameter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = mock.Mock()
        self.cmd.cli_ctx = mock.Mock()
        self.client = mock.Mock()
        self.valid_identity_id = "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity"
        
        # Set up mock cache rule
        self.dummy_rule = mock.Mock()
        self.dummy_rule.properties = mock.Mock()
        self.dummy_rule.properties.sync_mode = "ActiveSync"
        self.dummy_rule.properties.sync_referrers = "Disabled"
        self.dummy_rule.properties.artifact_sync_filters = None
        self.dummy_rule.properties.credential_set_resource_id = None
        
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    @mock.patch('azext_acrcache.cache.user_confirmation')
    def test_acr_cache_update_with_valid_identity(self, mock_confirmation, mock_get_registry):
        """Test cache update with valid identity"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.ContainerRegistry/registries/registry1"
        mock_get_registry.return_value = (mock_registry, "mockrg")
        self.client.get.return_value = self.dummy_rule
        
        cache.acr_cache_update_custom(
            self.cmd, self.client, "mockRegistry", "mockCacheRule",
            assign_identity=self.valid_identity_id,
            yes=True
        )
        
        # Verify client.begin_update was called
        self.client.begin_update.assert_called_once()
        
        # Extract the update parameters from the call
        call_args = self.client.begin_update.call_args[1]
        update_params = call_args['cache_rule_update_parameters']
        
        # Verify identity was set
        self.assertIsNotNone(update_params.identity)
        self.assertEqual(update_params.identity.type, "UserAssigned")
        self.assertIn(self.valid_identity_id, update_params.identity.user_assigned_identities)
    
    @mock.patch('azext_acrcache.cache.get_registry_by_name')
    def test_acr_cache_update_with_invalid_identity(self, mock_get_registry):
        """Test cache update with invalid identity raises error"""
        mock_registry = mock.Mock()
        mock_registry.id = "/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.ContainerRegistry/registries/registry1"
        mock_get_registry.return_value = (mock_registry, "mockrg")
        self.client.get.return_value = self.dummy_rule
        
        with self.assertRaises(CLIError):
            cache.acr_cache_update_custom(
                self.cmd, self.client, "mockRegistry", "mockCacheRule",
                assign_identity="invalid-identity-id"
            )


if __name__ == '__main__':
    unittest.main()