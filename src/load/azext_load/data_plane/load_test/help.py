# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

helps = {}

helps[
    "load test create"
] = """
type: command
short-summary: Create a new load test.
examples:
    - name: Create a test with load test config file.
      text: |
        az load test create --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {test_id} --load-test-config-file {load_test_config_file}
    - name: Create a test with arguments.
      text: |
        az load test create --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --display-name {display_name} --description {test_description} --test-plan {test_plan} --engine-instances {engine_instances} --env {env} 
    - name: Create a test with load test config file and override engine-instance and env using arguments.
      text: |
        az load test create --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {test_id} --load-test-config-file {load_test_config_file} --engine-instances {engine_instances} --env {env}
    - name: Create a test with secrets and environment variables.
      text: |
        az load test create --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --display-name {display_name} --description {test_description} --test-plan {test_plan} --secret {secret_name1:secret_uri1 secret_name2:secret_uri2} --env {env}
    - name: Create a test with secrets using user assigned Managed Identity to access the Key Vault.
      text: |
        az load test create --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --display-name {display_name} --secret {secret_name1:secret_uri1 secret_name2:secret_uri2} --keyvault-reference-id {keyvault_reference_id}
    - name: Create a test for a private endpoint in a Virtual Network with split CSV option enabled.
      text: |
        az load test create --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --display-name {display_name} --subnet-id {subnet_id} --split-csv true
"""

helps[
    "load test list"
] = """
type: command
short-summary: List all tests in the given load test resource.
examples:
    - name: List all load tests in a resource.
      text: |
        az load test list --load-test-resource {load_test_resource} --resource-group {resource_group}
"""

helps[
    "load test show"
] = """
type: command
short-summary: Show details of test.
examples:
    - name: Get the details of a load test.
      text: |
        az load test show --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} 
"""

helps[
    "load test update"
] = """
type: command
short-summary: Update an existing load test.
examples:
    - name: Update a test with load test config file.
      text: |
        az load test update --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {existing_test_id} --load-test-config-file {load_test_config_file}
    - name: Update the display name and description for a test.
      text: |
        az load test update --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {existing_test_id} --description {description} --display-name {display_name}
    - name: Update a test with load test config file and override parameters using arguments.
      text: |
        az load test update --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {existing_test_id} --load-test-config-file {load_test_config_file} --engine-instances {engine_instances} --env {name:value name:value}
    - name: Remove the secrets from a test.
      text: |
        az load test update --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {existing_test_id} --secret secret_name1:\"\"
"""

helps[
    "load test delete"
] = """
type: command
short-summary: Delete an existing load test.
examples:
    - name: Delete a load test.
      text: |
        az load test delete --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {existing_test_id}
"""

helps[
    "load test download-files"
] = """
type: command
short-summary: Download files of an existing load test.
examples:
    - name: Download all files of a test. The directory should already exist.
      text: |
        az load test download-files --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --path {path}
    - name: Download all files of a test by creating the directory if it does not exist. 
      text: |
        az load test download-files --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --path {path} --force
"""

helps[
    "load test app-component add"
] = """
type: command
short-summary: Add an app component to a test.
examples:
    - name: Add an app component to a test.
      text: |
        az load test app-component add --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --app-component-name {app_component_name} --app-component-type {app_component_type} --app-component-id {app_component_id} --app-component-kind {app_component_kind}
"""

helps[
    "load test app-component list"
] = """
type: command
short-summary: List all app component of a test.
examples:
    - name: List all app components for a test.
      text: |
        az load test app-component list --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group}
"""

helps[
    "load test app-component remove"
] = """
type: command
short-summary: Remove the given app component from a test.
examples:
    - name: Remove an app component from a test.
      text: |
        az load test app-component remove --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --app-component-id {app_component_id} --yes
"""

helps[
    "load test server-metric add"
] = """
type: command
short-summary: Add a server-metric to a test.
examples:
    - name: Add a server metric for an app component to a test.
      text: |
        az load test server-metric add --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-id {server_metric_id} --metric-name  {server_metric_name} --metric-namespace {server_metric_namespace} --aggregation {aggregation} --app-component-type {app_component_type} --app-component-id {app_component_id}
"""

helps[
    "load test server-metric list"
] = """
type: command
short-summary: List all server-metrics of a test.
examples:
    - name: List all server metrics for a test.
      text: |
        az load test server-metric list --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} 
"""

helps[
    "load test server-metric remove"
] = """
type: command
short-summary: Remove the given server-metric from the test.
examples:
    - name: Remove a server metric from a test.
      text: |
        az load test server-metric remove --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-id {server_metric_id} --yes
"""

helps[
    "load test file delete"
] = """
type: command
short-summary: Delete a file from test.
long-summary: Delete a file from test by providing the file name and test id.
examples:
    - name: Delete a file from a test.
      text: |
        az load test file delete --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --file-name {file_name} --yes
"""

helps[
    "load test file download"
] = """
type: command
short-summary: Download a file of a test.
long-summary: Download a file of a test by providing the file name, test id and path where to download to path.
examples:
    - name: Download a file from a test. The directory should already exist.
      text: |
        az load test file download --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --file-name {file_name} --path {download_path}
        examples:
    - name: Download a file from a test by creating the directory if it does not exist. 
      text: |
        az load test file download --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --file-name {file_name} --path {download_path} --force
"""

helps[
    "load test file list"
] = """
type: command
short-summary: List all files in a test.
long-summary: List details of all the files related to a test by providing the corresponding test id.
examples:
    - name: List all files in a test. 
      text: |
        az load test file list --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} 
"""

helps[
    "load test file upload"
] = """
type: command
short-summary: Upload a file to a test.
long-summary: Upload a file to a test by providing path to file and test id.
examples:
    - name: Upload a JMeter script (JMX file) to a test. 
      text: |
        az load test file upload --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --path {test_plan} --wait
    - name: Upload a CSV file to a test and dont wait for upload. 
      text: |
        az load test file upload --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --path {csv_file_path} --file-type ADDITIONAL_ARTIFACTS
    - name: Upload a user property file to a test. 
      text: |
        az load test file upload --test-id {test_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --path {csv_file_path} --file-type USER_PROPERTIES --wait
"""
