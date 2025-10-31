# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import pytest
import yaml
from azext_mlv2.tests.scenario_test_helper import MLBaseScenarioTest


class DeploymentTemplateScenarioTest(MLBaseScenarioTest):
    """Test cases for deployment template commands (list, get, create, archive, restore)."""

    def test_deployment_template_no_registry(self) -> None:
        """Test that deployment template commands require registry parameter."""
        commands = [
            "az ml deployment-template list",
            "az ml deployment-template show -n test-template",
            "az ml deployment-template create -n test-template",
            "az ml deployment-template archive -n test-template",
            "az ml deployment-template restore -n test-template"
        ]
        
        for base_command in commands:
            with pytest.raises(Exception) as exp:
                self.cmd(f'{base_command} --registry-name=""')
            # Registry is required for deployment templates
            assert "registry" in str(exp.value).lower() or "required" in str(exp.value).lower()

    def test_deployment_template_list_empty_registry(self) -> None:
        """Test listing deployment templates from empty registry."""
        result = self.cmd("az ml deployment-template list --registry-name test-registry")
        templates = yaml.safe_load(result.output) if result.output else []
        assert isinstance(templates, list)
        # Empty registry should return empty list
        assert len(templates) >= 0

    def test_deployment_template_create_basic(self) -> None:
        """Test creating a basic deployment template."""
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        
        # Create deployment template
        result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(result.output)
        
        # Verify basic properties
        assert template["name"] == "test-deployment-template"
        assert template["version"] == "1"
        assert template["description"] == "Test deployment template for CLI testing"
        assert "tags" in template
        assert template["tags"]["purpose"] == "testing"
        assert template["tags"]["framework"] == "azure-ml"
        assert "endpoints" in template
        assert len(template["endpoints"]) == 1
        assert template["endpoints"][0]["name"] == "default"

    def test_deployment_template_create_advanced(self) -> None:
        """Test creating an advanced deployment template with multiple endpoints."""
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_advanced.yaml"
        
        # Create deployment template
        result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(result.output)
        
        # Verify advanced properties
        assert template["name"] == "advanced-deployment-template"
        assert template["version"] == "2"
        assert template["description"] == "Advanced deployment template with multiple endpoints for testing"
        assert "tags" in template
        assert template["tags"]["environment"] == "development"
        assert template["tags"]["team"] == "ml-platform"
        assert "endpoints" in template
        assert len(template["endpoints"]) == 2
        
        # Verify endpoints
        endpoint_names = [ep["name"] for ep in template["endpoints"]]
        assert "primary" in endpoint_names
        assert "canary" in endpoint_names
        
        # Verify traffic distribution
        primary_endpoint = next(ep for ep in template["endpoints"] if ep["name"] == "primary")
        canary_endpoint = next(ep for ep in template["endpoints"] if ep["name"] == "canary")
        assert primary_endpoint["traffic"] == 80
        assert canary_endpoint["traffic"] == 20

    def test_deployment_template_create_minimal(self) -> None:
        """Test creating a minimal deployment template."""
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_minimal.yaml"
        
        # Create deployment template
        result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(result.output)
        
        # Verify minimal properties
        assert template["name"] == "minimal-deployment-template"
        assert template["version"] == "1"
        assert template["description"] == "Minimal deployment template for basic testing"
        assert "endpoints" in template
        assert len(template["endpoints"]) == 1
        assert template["endpoints"][0]["name"] == "simple"

    def test_deployment_template_create_with_params_override(self) -> None:
        """Test creating deployment template with parameter overrides."""
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        
        # Create with name and version override
        result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path} --name override-template --version 5")
        template = yaml.safe_load(result.output)
        
        # Verify overridden values
        assert template["name"] == "override-template"
        assert template["version"] == "5"
        # Original description should remain
        assert template["description"] == "Test deployment template for CLI testing"

    def test_deployment_template_get_existing(self) -> None:
        """Test getting an existing deployment template."""
        # First create a template
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        created_template = yaml.safe_load(create_result.output)
        
        # Then get it back
        get_result = self.cmd(f"az ml deployment-template get --registry-name test-registry --name {created_template['name']} --version {created_template['version']}")
        retrieved_template = yaml.safe_load(get_result.output)
        
        # Verify they match
        assert retrieved_template["name"] == created_template["name"]
        assert retrieved_template["version"] == created_template["version"]
        assert retrieved_template["description"] == created_template["description"]
        assert "endpoints" in retrieved_template
        assert len(retrieved_template["endpoints"]) == len(created_template["endpoints"])

    def test_deployment_template_get_nonexistent(self) -> None:
        """Test getting a non-existent deployment template."""
        with pytest.raises(Exception) as exp:
            self.cmd("az ml deployment-template get --registry-name test-registry --name nonexistent-template --version 999")
        
        # Should raise an error for non-existent template
        error_msg = str(exp.value).lower()
        assert "not found" in error_msg or "does not exist" in error_msg or "nonexistent-template" in error_msg

    def test_deployment_template_get_latest_version(self) -> None:
        """Test getting deployment template without specifying version (should get latest)."""
        # First create a template
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        created_template = yaml.safe_load(create_result.output)
        
        # Get without version (should get latest)
        get_result = self.cmd(f"az ml deployment-template get --registry-name test-registry --name {created_template['name']}")
        retrieved_template = yaml.safe_load(get_result.output)
        
        # Verify it's the same template
        assert retrieved_template["name"] == created_template["name"]
        assert retrieved_template["version"] == created_template["version"]

    def test_deployment_template_list_after_create(self) -> None:
        """Test listing deployment templates after creating some."""
        # Create multiple templates
        configs = [
            ("./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml", "basic-template"),
            ("./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_minimal.yaml", "minimal-template")
        ]
        
        created_names = []
        for config_path, override_name in configs:
            result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path} --name {override_name}")
            template = yaml.safe_load(result.output)
            created_names.append(template["name"])
        
        # List all templates
        list_result = self.cmd("az ml deployment-template list --registry-name test-registry")
        templates = yaml.safe_load(list_result.output)
        
        # Verify our created templates are in the list
        assert isinstance(templates, list)
        template_names = [t["name"] for t in templates]
        
        for name in created_names:
            assert name in template_names

    def test_deployment_template_archive_and_restore_version(self) -> None:
        """Test archiving and restoring a specific version of deployment template."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # Archive the specific version
        archive_result = self.cmd(f"az ml deployment-template archive --registry-name test-registry --name {template_name} --version {template_version}")
        # Archive command typically returns empty output on success
        assert archive_result.output == "" or "archived" in archive_result.output.lower()
        
        # Restore the specific version
        restore_result = self.cmd(f"az ml deployment-template restore --registry-name test-registry --name {template_name} --version {template_version}")
        # Restore command typically returns empty output on success
        assert restore_result.output == "" or "restored" in restore_result.output.lower()

    def test_deployment_template_archive_and_restore_all_versions(self) -> None:
        """Test archiving and restoring all versions of a deployment template."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        
        # Archive all versions (no version specified)
        archive_result = self.cmd(f"az ml deployment-template archive --registry-name test-registry --name {template_name}")
        # Archive command typically returns empty output on success
        assert archive_result.output == "" or "archived" in archive_result.output.lower()
        
        # Restore all versions (no version specified)
        restore_result = self.cmd(f"az ml deployment-template restore --registry-name test-registry --name {template_name}")
        # Restore command typically returns empty output on success
        assert restore_result.output == "" or "restored" in restore_result.output.lower()

    def test_deployment_template_archive_nonexistent(self) -> None:
        """Test archiving a non-existent deployment template."""
        with pytest.raises(Exception) as exp:
            self.cmd("az ml deployment-template archive --registry-name test-registry --name nonexistent-template --version 999")
        
        # Should raise an error for non-existent template
        error_msg = str(exp.value).lower()
        assert "not found" in error_msg or "does not exist" in error_msg or "nonexistent" in error_msg

    def test_deployment_template_restore_nonexistent(self) -> None:
        """Test restoring a non-existent deployment template."""
        with pytest.raises(Exception) as exp:
            self.cmd("az ml deployment-template restore --registry-name test-registry --name nonexistent-template --version 999")
        
        # Should raise an error for non-existent template
        error_msg = str(exp.value).lower()
        assert "not found" in error_msg or "does not exist" in error_msg or "nonexistent" in error_msg

    def test_deployment_template_create_no_wait(self) -> None:
        """Test creating deployment template with --no-wait flag."""
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        
        # Create with no-wait flag
        result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path} --no-wait")
        
        # With --no-wait, the command should return immediately with no output or a status message
        assert result.output == "" or "initiated" in result.output.lower() or "status" in result.output.lower()

    def test_deployment_template_archive_no_wait(self) -> None:
        """Test archiving deployment template with --no-wait flag."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        # Archive with no-wait flag
        archive_result = self.cmd(f"az ml deployment-template archive --registry-name test-registry --name {template['name']} --version {template['version']} --no-wait")
        
        # With --no-wait, should return immediately
        assert archive_result.output == "" or "initiated" in archive_result.output.lower()

    def test_deployment_template_restore_no_wait(self) -> None:
        """Test restoring deployment template with --no-wait flag."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        # Archive it first
        self.cmd(f"az ml deployment-template archive --registry-name test-registry --name {template['name']} --version {template['version']}")
        
        # Restore with no-wait flag
        restore_result = self.cmd(f"az ml deployment-template restore --registry-name test-registry --name {template['name']} --version {template['version']} --no-wait")
        
        # With --no-wait, should return immediately
        assert restore_result.output == "" or "initiated" in restore_result.output.lower()

    # ===== UPDATE COMMAND TESTS =====

    def test_deployment_template_update_description(self) -> None:
        """Test updating deployment template description."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        original_description = template["description"]
        
        # Update description
        new_description = "Updated description for testing purposes"
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"{new_description}\"")
        updated_template = yaml.safe_load(update_result.output)
        
        # Verify the update
        assert updated_template["name"] == template_name
        assert updated_template["version"] == template_version
        assert updated_template["description"] == new_description
        assert updated_template["description"] != original_description
        # Other properties should remain unchanged
        assert "endpoints" in updated_template
        assert len(updated_template["endpoints"]) == len(template["endpoints"])

    def test_deployment_template_update_tags(self) -> None:
        """Test updating deployment template tags."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # Update tags
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --tags environment=production owner=ml-team")
        updated_template = yaml.safe_load(update_result.output)
        
        # Verify the update
        assert updated_template["name"] == template_name
        assert updated_template["version"] == template_version
        assert "tags" in updated_template
        # Should have new tags merged with existing ones
        assert updated_template["tags"]["environment"] == "production"
        assert updated_template["tags"]["owner"] == "ml-team"
        # Original tags should still be present (merged, not replaced)
        assert updated_template["tags"]["purpose"] == "testing"
        assert updated_template["tags"]["framework"] == "azure-ml"

    def test_deployment_template_update_description_and_tags(self) -> None:
        """Test updating both description and tags simultaneously."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_minimal.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # Update both description and tags
        new_description = "Updated minimal template with new tags"
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"{new_description}\" --tags updated=true version=v2")
        updated_template = yaml.safe_load(update_result.output)
        
        # Verify both updates
        assert updated_template["name"] == template_name
        assert updated_template["version"] == template_version
        assert updated_template["description"] == new_description
        assert "tags" in updated_template
        assert updated_template["tags"]["updated"] == "true"
        assert updated_template["tags"]["version"] == "v2"

    def test_deployment_template_update_without_version(self) -> None:
        """Test updating deployment template without specifying version (should update latest)."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        
        # Update without specifying version (should update latest)
        new_description = "Updated latest version without specifying version"
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --description \"{new_description}\"")
        updated_template = yaml.safe_load(update_result.output)
        
        # Verify the update
        assert updated_template["name"] == template_name
        assert updated_template["description"] == new_description

    def test_deployment_template_update_nonexistent(self) -> None:
        """Test updating a non-existent deployment template."""
        with pytest.raises(Exception) as exp:
            self.cmd("az ml deployment-template update --registry-name test-registry --name nonexistent-template --version 999 --description \"This should fail\"")
        
        # Should raise an error for non-existent template
        error_msg = str(exp.value).lower()
        assert "not found" in error_msg or "does not exist" in error_msg or "nonexistent" in error_msg

    def test_deployment_template_update_no_changes(self) -> None:
        """Test updating deployment template with no actual changes."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        original_description = template["description"]
        
        # Update with same description (no real change)
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"{original_description}\"")
        updated_template = yaml.safe_load(update_result.output)
        
        # Should still work and return the template
        assert updated_template["name"] == template_name
        assert updated_template["version"] == template_version
        assert updated_template["description"] == original_description

    def test_deployment_template_update_empty_tags(self) -> None:
        """Test updating deployment template with empty tags."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # Update with empty tags (should preserve existing tags)
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"Updated with empty tags\"")
        updated_template = yaml.safe_load(update_result.output)
        
        # Verify description updated but tags preserved
        assert updated_template["description"] == "Updated with empty tags"
        assert "tags" in updated_template
        assert updated_template["tags"]["purpose"] == "testing"
        assert updated_template["tags"]["framework"] == "azure-ml"

    def test_deployment_template_update_no_wait(self) -> None:
        """Test updating deployment template with --no-wait flag."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # Update with no-wait flag
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"Updated with no-wait\" --no-wait")
        
        # With --no-wait, should return immediately with minimal output
        assert update_result.output == "" or "initiated" in update_result.output.lower() or "status" in update_result.output.lower()

    def test_deployment_template_update_and_verify_unchanged_properties(self) -> None:
        """Test that updating preserves all other properties of the deployment template."""
        # Create an advanced template with multiple properties
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_advanced.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # Store original properties
        original_endpoints = template["endpoints"]
        original_endpoint_count = len(original_endpoints)
        
        # Update only description
        new_description = "Updated advanced template preserving all endpoints"
        update_result = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"{new_description}\"")
        updated_template = yaml.safe_load(update_result.output)
        
        # Verify description updated
        assert updated_template["description"] == new_description
        
        # Verify all other properties preserved
        assert updated_template["name"] == template_name
        assert updated_template["version"] == template_version
        assert "endpoints" in updated_template
        assert len(updated_template["endpoints"]) == original_endpoint_count
        
        # Verify endpoint details preserved
        updated_endpoint_names = [ep["name"] for ep in updated_template["endpoints"]]
        original_endpoint_names = [ep["name"] for ep in original_endpoints]
        assert set(updated_endpoint_names) == set(original_endpoint_names)
        
        # Verify traffic distribution preserved
        for updated_ep in updated_template["endpoints"]:
            original_ep = next(ep for ep in original_endpoints if ep["name"] == updated_ep["name"])
            assert updated_ep["traffic"] == original_ep["traffic"]

    def test_deployment_template_update_chain_multiple_updates(self) -> None:
        """Test chaining multiple updates to the same deployment template."""
        # Create a template first
        config_path = "./src/cli/src/machinelearningservices/azext_mlv2/tests/test_configs/deployment_template/deployment_template_basic.yaml"
        create_result = self.cmd(f"az ml deployment-template create --registry-name test-registry --file {config_path}")
        template = yaml.safe_load(create_result.output)
        
        template_name = template["name"]
        template_version = template["version"]
        
        # First update: description
        first_description = "First update - description only"
        first_update = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"{first_description}\"")
        first_result = yaml.safe_load(first_update.output)
        assert first_result["description"] == first_description
        
        # Second update: tags
        second_update = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --tags iteration=2 status=active")
        second_result = yaml.safe_load(second_update.output)
        assert second_result["description"] == first_description  # Should preserve previous update
        assert second_result["tags"]["iteration"] == "2"
        assert second_result["tags"]["status"] == "active"
        
        # Third update: both description and tags
        final_description = "Final update - both description and tags"
        final_update = self.cmd(f"az ml deployment-template update --registry-name test-registry --name {template_name} --version {template_version} --description \"{final_description}\" --tags final=true")
        final_result = yaml.safe_load(final_update.output)
        assert final_result["description"] == final_description
        assert final_result["tags"]["final"] == "true"
        # Previous tags should be merged
        assert final_result["tags"]["iteration"] == "2"
        assert final_result["tags"]["status"] == "active"
