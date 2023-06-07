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
        az load test create --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-test-id --load-test-config-file ~/resources/sample-config.yaml
    - name: Create a test with arguments.
      text: |
        az load test create --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --display-name "Sample Name" --description "Test description" --test-plan sample-jmx.jmx --engine-instances 1 --env rps=2 count=1
    - name: Create a test with load test config file and override engine-instance and env using arguments and don't wait for file upload.
      text: |
        az load test create --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-test-id --load-test-config-file ~/resources/sample-config.yaml --engine-instances 1 --env rps=2 count=1 --no-wait
    - name: Create a test with secrets and environment variables.
      text: |
        az load test create --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --display-name "Sample Name" --description "Test description" --test-plan sample-jmx.jmx --secret secret_name1=secret_uri1 secret_name2=secret_uri2 --env rps=2 count=1
    - name: Create a test with secrets using user assigned Managed Identity to access the Key Vault.
      text: |
        az load test create --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --display-name "Sample Name" --secret secret_name1=secret_uri1 secret_name2=secret_uri2 --keyvault-reference-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/microsoft.managedidentity/userassignedidentities/sample-mi"
    - name: Create a test for a private endpoint in a Virtual Network with split CSV option enabled.
      text: |
        az load test create --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --display-name "Sample Name" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.Network/virtualNetworks/SampleVMVNET/subnets/SampleVMSubnet" --split-csv true
"""

helps[
    "load test list"
] = """
type: command
short-summary: List all tests in the given load test resource.
examples:
    - name: List all load tests in a resource.
      text: |
        az load test list --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test show"
] = """
type: command
short-summary: Show details of test.
examples:
    - name: Get the details of a load test.
      text: |
        az load test show --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test update"
] = """
type: command
short-summary: Update an existing load test.
examples:
    - name: Update a test with load test config file and don't wait for file upload.
      text: |
        az load test update --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-existing-test-id --load-test-config-file ~/resources/sample-config.yaml --no-wait
    - name: Update the display name and description for a test.
      text: |
        az load test update --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-existing-test-id --description "Test description" --display-name "Sample Name"
    - name: Update a test with load test config file and override parameters using arguments.
      text: |
        az load test update --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-existing-test-id --load-test-config-file ~/resources/sample-config.yaml --engine-instances 1 --env name=value name=value
    - name: Remove the secrets from a test.
      text: |
        az load test update --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-existing-test-id --secret secret_name1=\"\"
    - name: Update the Key Vault reference identity to system assigned Managed Identity.
      text: |
        az load test update --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-existing-test-id --keyvault-reference-id null
"""

helps[
    "load test delete"
] = """
type: command
short-summary: Delete an existing load test.
examples:
    - name: Delete a load test.
      text: |
        az load test delete --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-existing-test-id
"""

helps[
    "load test download-files"
] = """
type: command
short-summary: Download files of an existing load test.
examples:
    - name: Download all files of a test. The directory should already exist.
      text: |
        az load test download-files --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --path ~/downloads
    - name: Download all files of a test by creating the directory if it does not exist.
      text: |
        az load test download-files --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --path "~/downloads/new folder" --force
"""

helps[
    "load test app-component add"
] = """
type: command
short-summary: Add an app component to a test.
examples:
    - name: Add an app component to a test.
      text: |
        az load test app-component add --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --app-component-name appcomponentresource --app-component-type microsoft.insights/components --app-component-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/samplerg/providers/microsoft.insights/components/appcomponentresource" --app-component-kind web
"""

helps[
    "load test app-component list"
] = """
type: command
short-summary: List all app components for a test.
examples:
    - name: List all app components for a test.
      text: |
        az load test app-component list --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test app-component remove"
] = """
type: command
short-summary: Remove the given app component from a test.
examples:
    - name: Remove an app component from a test.
      text: |
        az load test app-component remove --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --app-component-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/app-comp-name --yes
"""

helps[
    "load test server-metric add"
] = """
type: command
short-summary: Add a server-metric to a test.
examples:
    - name: Add a server metric for an app component to a test.
      text: |
        az load test server-metric add --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/Sample-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU" --metric-name  "Percentage CPU" --metric-namespace microsoft.compute/virtualmachinescalesets --aggregation Average --app-component-type Microsoft.Compute/virtualMachineScaleSets --app-component-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/app-comp-name
"""

helps[
    "load test server-metric list"
] = """
type: command
short-summary: List all server-metrics for a test.
examples:
    - name: List all server metrics for a test.
      text: |
        az load test server-metric list --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test server-metric remove"
] = """
type: command
short-summary: Remove the given server-metric from the test.
examples:
    - name: Remove a server metric from a test.
      text: |
        az load test server-metric remove --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/Sample-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU" --yes
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
        az load test file delete --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --file-name sample-jmx.jmx --yes
"""

helps[
    "load test file download"
] = """
type: command
short-summary: Download a file from a test.
long-summary: Download a file from, a test by providing the file name, test id and path to download the files.
examples:
    - name: Download a file from a test. The directory should already exist.
      text: |
        az load test file download --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --file-name sample-jmx.jmx --path ~/Downloads/
        examples:
    - name: Download a file from a test by creating the directory if it does not exist.
      text: |
        az load test file download --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --file-name sample-jmx.jmx --path ~/Downloads/ --force
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
        az load test file list --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg
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
        az load test file upload --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --path sample-jmx.jmx
    - name: Upload a CSV file to a test and without waiting for the long-running operation to finish.
      text: |
        az load test file upload --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --path ~/Resources/split-csv.csv --file-type ADDITIONAL_ARTIFACTS --no-wait
    - name: Upload a user property file to a test.
      text: |
        az load test file upload --test-id sample-test-id --load-test-resource sample-alt-resource --resource-group sample-rg --path ~/Resources/user-prop.properties --file-type USER_PROPERTIES
"""
