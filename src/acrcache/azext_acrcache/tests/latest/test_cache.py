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

if __name__ == '__main__':
    unittest.main()