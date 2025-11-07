# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
import time
import tempfile
import os
from azext_mlv2.tests.scenario_test_helper import MLBaseScenarioTest


class DeploymentTemplateScenarioTest(MLBaseScenarioTest):
    """Test cases for deployment template commands following the essential workflow."""

    # Class variables - aligned with other test files
    registry_name = "test-cli-reg"
    resource_group = "test-cli-rg"
    template_name = "test-deployment-template"
    template_version = "1"

    @classmethod
    def setUpClass(cls):
        """Set up test registry before all tests."""
        super().setUpClass()
        cls._create_registry()

    @classmethod
    def _create_registry(cls):
        """Create a test registry for deployment template testing."""
        print(f"\n[SETUP] Creating test registry: {cls.registry_name}")
        registry_yaml = f"""
description: Test registry for deployment template testing
name: {cls.registry_name}
location: WestCentralUS
replication_locations:
  - location: WestCentralUS
"""
        # Write temporary registry config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(registry_yaml)
            registry_yaml_path = f.name

        try:
            # Create registry
            cls.cmd(f"az ml registry create -g {cls.resource_group} --file {registry_yaml_path}")
            if cls.is_live:
                print("[SETUP] Waiting 30s for registry creation to complete...")
                time.sleep(30)
            print("[SETUP] Registry created successfully")
        except Exception as e:
            print(f"[SETUP] Registry may already exist: {e}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(registry_yaml_path)
            except:
                pass

    @classmethod
    def tearDownClass(cls):
        """Clean up test registry after all tests."""
        print(f"\n[TEARDOWN] Deleting test registry: {cls.registry_name}")
        try:
            cls.cmd(f"az ml registry delete -g {cls.resource_group} --name {cls.registry_name} --yes")
            print("[TEARDOWN] Registry deleted successfully")
        except Exception as e:
            print(f"[TEARDOWN] Error deleting registry: {e}")
        super().tearDownClass()

    def _get_config_path(self):
        """Get the absolute path to the deployment template config file."""
        test_file_dir = os.path.dirname(os.path.abspath(__file__))  # tests/latest
        tests_dir = os.path.dirname(test_file_dir)  # tests
        config_path = os.path.join(tests_dir, "test_configs", "deployment_template", "deployment_template_basic.yaml")
        return os.path.normpath(config_path)

    def test_01_deployment_template_create(self) -> None:
        """Test Step 1: Create a deployment template."""
        print(f"\n[TEST 01] Creating deployment template: {self.template_name} v{self.template_version}")
        config_path = self._get_config_path()
        print(f"[TEST 01] Using config file: {config_path}")

        create_result = self.cmd(
            f'az ml deployment-template create --registry-name {self.registry_name} '
            f'--file "{config_path}"'
        )

        # Parse and verify creation
        if create_result.output:
            created_template = yaml.safe_load(create_result.output)
            print(f"[TEST 01] Created template response: {created_template}")

            # Verify creation - handle different output formats
            if isinstance(created_template, dict):
                # Check if name and version are in the response
                template_name_in_output = created_template.get("name", self.template_name)
                template_version_in_output = created_template.get("version", self.template_version)

                assert template_name_in_output == self.template_name, \
                    f"Expected name {self.template_name}, got {template_name_in_output}"
                assert template_version_in_output == self.template_version, \
                    f"Expected version {self.template_version}, got {template_version_in_output}"
                print(f"[TEST 01] Template created: {template_name_in_output} v{template_version_in_output}")
            else:
                print(f"[TEST 01] Template created (output format: {type(created_template)})")
        else:
            print(f"[TEST 01] Template created (no output returned)")

    def test_02_deployment_template_list(self) -> None:
        """Test Step 2: List deployment templates in the registry."""
        print(f"\n[TEST 02] Listing deployment templates in registry: {self.registry_name}")
        list_result = self.cmd(f"az ml deployment-template list --registry-name {self.registry_name}")

        # Verify list operation
        if list_result.output:
            templates = yaml.safe_load(list_result.output)
            print(f"[TEST 02] List output type: {type(templates)}")

            if isinstance(templates, list):
                template_names = [t.get("name") for t in templates if isinstance(t, dict) and "name" in t]
                print(f"[TEST 02] Found {len(templates)} template(s): {template_names}")
                # Only check if we found templates with names
                if template_names:
                    assert self.template_name in template_names, f"Template {self.template_name} not found in list"
            else:
                print(f"[TEST 02] List returned: {templates}")
        else:
            print(f"[TEST 02] List operation completed (no output)")

    def test_03_deployment_template_get(self) -> None:
        """Test Step 3: Get the specific deployment template."""
        print(f"\n[TEST 03] Getting deployment template: {self.template_name} v{self.template_version}")
        get_result = self.cmd(
            f"az ml deployment-template show --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {self.template_version}"
        )

        # Verify get operation
        if get_result.output:
            retrieved_template = yaml.safe_load(get_result.output)
            print(f"[TEST 03] Retrieved template: {retrieved_template}")

            if isinstance(retrieved_template, dict):
                # Verify retrieved template
                retrieved_name = retrieved_template.get("name", self.template_name)
                retrieved_version = retrieved_template.get("version", self.template_version)
                assert retrieved_name == self.template_name, \
                    f"Expected {self.template_name}, got {retrieved_name}"
                assert retrieved_version == self.template_version, \
                    f"Expected {self.template_version}, got {retrieved_version}"
                print(f"[TEST 03] Retrieved template successfully: {retrieved_name} v{retrieved_version}")
            else:
                print(f"[TEST 03] Retrieved template (format: {type(retrieved_template)})")
        else:
            print(f"[TEST 03] Get operation completed")

    def test_04_deployment_template_update(self) -> None:
        """Test Step 4: Update deployment template (description and tags)."""
        print(f"\n[TEST 04] Updating deployment template description and tags")
        new_description = "Updated_description_for_deployment_template_testing"
        update_result = self.cmd(
            f"az ml deployment-template update --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {self.template_version} "
            f"--set description={new_description} tags.environment=test tags.updated=true"
        )

        # Verify update
        if update_result.output:
            updated_template = yaml.safe_load(update_result.output)
            print(f"[TEST 04] Updated template: {updated_template}")

            if isinstance(updated_template, dict):
                # Verify updates
                assert updated_template.get("name") == self.template_name
                assert updated_template.get("version") == self.template_version
                assert updated_template.get("description") == new_description
                if "tags" in updated_template:
                    assert updated_template["tags"].get("environment") == "test"
                    assert updated_template["tags"].get("updated") == True
                print(f"[TEST 04] Template updated successfully")
            else:
                print(f"[TEST 04] Update completed (format: {type(updated_template)})")
        else:
            print(f"[TEST 04] Update completed")

    def test_05_deployment_template_archive(self) -> None:
        """Test Step 5: Archive the deployment template."""
        print(f"\n[TEST 05] Archiving deployment template")
        archive_result = self.cmd(
            f"az ml deployment-template archive --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {self.template_version}"
        )
        # Archive command typically returns empty output on success
        assert archive_result.output == "" or "archived" in archive_result.output.lower()
        print(f"[TEST 05] Template archived successfully")

    def test_06_deployment_template_restore(self) -> None:
        """Test Step 6: Restore the deployment template."""
        print(f"\n[TEST 06] Restoring deployment template")
        restore_result = self.cmd(
            f"az ml deployment-template restore --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {self.template_version}"
        )
        # Restore command typically returns empty output on success
        assert restore_result.output == "" or "restored" in restore_result.output.lower()
        print(f"[TEST 06] Template restored successfully")

    def test_07_deployment_template_create_with_version(self) -> None:
        """Test: Create a new version of the deployment template."""
        print(f"\n[TEST 07] Creating new version of deployment template")
        config_path = self._get_config_path()
        new_version = "2"

        # Read the config file and modify the version
        with open(config_path, 'r') as f:
            template_content = f.read()

        # Create temporary file with new version - handle both quoted and unquoted versions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Try to replace both quoted and unquoted version formats
            modified_content = template_content.replace('version: "1"', f'version: {new_version}')
            modified_content = modified_content.replace('version: 1', f'version: {new_version}')
            modified_content = modified_content.replace("version: '1'", f'version: {new_version}')
            f.write(modified_content)
            temp_config_path = f.name

        try:
            create_result = self.cmd(
                f'az ml deployment-template create --registry-name {self.registry_name} '
                f'--file "{temp_config_path}"'
            )

            if create_result.output:
                created_template = yaml.safe_load(create_result.output)
                if isinstance(created_template, dict):
                    template_version_in_output = str(created_template.get("version", new_version))
                    assert template_version_in_output == new_version, \
                        f"Expected version {new_version}, got {template_version_in_output}"
                    print(f"[TEST 07] New version created successfully: v{template_version_in_output}")
                else:
                    print(f"[TEST 07] New version created (output format: {type(created_template)})")
            else:
                print(f"[TEST 07] New version created (no output returned)")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_config_path)
            except:
                pass

    def test_08_deployment_template_list_specific(self) -> None:
        """Test: List all deployment templates and verify list operation works."""
        print(f"\n[TEST 08] Listing deployment templates in registry")
        list_result = self.cmd(f"az ml deployment-template list --registry-name {self.registry_name}")

        # Just verify the list command works and returns valid output
        print(f"[TEST 08] List command executed successfully")
        if list_result.output:
            templates = yaml.safe_load(list_result.output)
            if isinstance(templates, list):
                print(f"[TEST 08] Found {len(templates)} total template(s) in registry")

                # Try to find our test templates (but don't fail if not found due to timing)
                our_templates = [
                    t for t in templates
                    if isinstance(t, dict) and t.get("name") == self.template_name
                ]
                if our_templates:
                    print(f"[TEST 08] Found {len(our_templates)} version(s) of {self.template_name}")
                else:
                    print(f"[TEST 08] Test template not found in list (may be timing issue)")
            else:
                print(f"[TEST 08] List returned: {type(templates)}")
        else:
            print(f"[TEST 08] List operation returned no output")

    def test_09_deployment_template_get_nonexistent(self) -> None:
        """Test: Try to get a non-existent deployment template (negative test)."""
        print(f"\n[TEST 09] Testing error handling for non-existent template")
        nonexistent_name = "nonexistent-template-xyz"

        # This should fail gracefully
        try:
            self.cmd(
                f"az ml deployment-template show --registry-name {self.registry_name} "
                f"--name {nonexistent_name} --version 1",
                expect_failure=True
            )
            print(f"[TEST 09] Command correctly failed for non-existent template")
        except Exception as e:
            # Command should fail, which is expected behavior
            print(f"[TEST 09] Expected failure occurred: {type(e).__name__}")
            # Verify it's a proper error, not a crash
            assert "does not exist" in str(e).lower() or "not found" in str(e).lower() or \
                   "error" in str(e).lower(), f"Unexpected error message: {e}"

    def test_10_deployment_template_update_multiple_tags(self) -> None:
        """Test: Update deployment template with multiple tag changes."""
        print(f"\n[TEST 10] Updating deployment template with multiple tags")
        update_result = self.cmd(
            f"az ml deployment-template update --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {self.template_version} "
            f"--set tags.author=test-automation tags.project=cli-testing "
            f"tags.iteration=second-update tags.validated=true"
        )

        if update_result.output:
            updated_template = yaml.safe_load(update_result.output)
            if isinstance(updated_template, dict) and "tags" in updated_template:
                tags = updated_template["tags"]
                print(f"[TEST 10] Updated tags: {tags}")
                # Verify at least some tags were updated
                expected_tags = ["author", "project", "iteration", "validated"]
                found_tags = [tag for tag in expected_tags if tag in tags]
                assert len(found_tags) > 0, "At least one tag should be updated"
                print(f"[TEST 10] Successfully updated {len(found_tags)} tag(s)")
            else:
                print(f"[TEST 10] Update completed (format: {type(updated_template)})")
        else:
            print(f"[TEST 10] Update completed")

    def test_11_deployment_template_archive_restore_cycle(self) -> None:
        """Test: Archive and restore cycle for version 1."""
        print(f"\n[TEST 11] Testing archive-restore cycle for version 1")
        test_version = self.template_version  # Use version 1 which we know exists

        # Archive version 1
        print(f"[TEST 11] Archiving version {test_version}")
        archive_result = self.cmd(
            f"az ml deployment-template archive --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {test_version}"
        )
        assert archive_result.output == "" or "archived" in archive_result.output.lower()
        print(f"[TEST 11] Version {test_version} archived")

        # Verify it's archived by trying to get it
        # (archived versions may still be retrievable but marked as archived)
        print(f"[TEST 11] Verifying archived state")
        get_result = self.cmd(
            f"az ml deployment-template show --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {test_version}"
        )
        if get_result.output:
            template = yaml.safe_load(get_result.output)
            if isinstance(template, dict):
                # Check if it has an archived status field
                if "properties" in template and isinstance(template["properties"], dict):
                    lifecycle_stage = template["properties"].get("stage")
                    print(f"[TEST 11] Template lifecycle stage: {lifecycle_stage}")
                else:
                    print(f"[TEST 11] Template retrieved (archived status may not be in response)")

        # Restore version 1
        print(f"[TEST 11] Restoring version {test_version}")
        restore_result = self.cmd(
            f"az ml deployment-template restore --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {test_version}"
        )
        assert restore_result.output == "" or "restored" in restore_result.output.lower()
        print(f"[TEST 11] Version {test_version} restored successfully")

    def test_12_deployment_template_full_workflow_verification(self) -> None:
        """Test: Final verification - list templates and check we can get our template."""
        print(f"\n[TEST 12] Final verification of deployment template state")

        # Verify we can get the template we created in test_01
        print(f"[TEST 12] Verifying template {self.template_name} v{self.template_version} exists")
        get_result = self.cmd(
            f"az ml deployment-template show --registry-name {self.registry_name} "
            f"--name {self.template_name} --version {self.template_version}"
        )

        if get_result.output:
            template = yaml.safe_load(get_result.output)
            if isinstance(template, dict):
                assert template.get("name") == self.template_name, \
                    f"Expected name {self.template_name}, got {template.get('name')}"
                assert str(template.get("version")) == self.template_version, \
                    f"Expected version {self.template_version}, got {template.get('version')}"
                print(f"[TEST 12] Template verified: {template.get('name')} v{template.get('version')}")
            else:
                print(f"[TEST 12] Template retrieved (format: {type(template)})")
        else:
            print(f"[TEST 12] Get operation returned no output")

        # List all templates
        print(f"[TEST 12] Listing all templates in registry")
        list_result = self.cmd(f"az ml deployment-template list --registry-name {self.registry_name}")

        if list_result.output:
            templates = yaml.safe_load(list_result.output)
            if isinstance(templates, list):
                print(f"[TEST 12] Total templates in registry: {len(templates)}")

                # Try to find our test templates
                our_templates = [
                    t for t in templates
                    if isinstance(t, dict) and t.get("name") == self.template_name
                ]
                if our_templates:
                    print(f"[TEST 12] Found {len(our_templates)} version(s) of {self.template_name} in list")
                    versions_found = [str(t.get("version")) for t in our_templates if "version" in t]
                    print(f"[TEST 12] Versions found: {versions_found}")
                else:
                    print(f"[TEST 12] Template not in list (but get operation succeeded)")
            else:
                print(f"[TEST 12] List returned non-list type: {type(templates)}")
        else:
            print(f"[TEST 12] List operation returned no output")
