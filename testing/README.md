# K8s Partner Extension Test Suite

This repository serves as the integration testing suite for the `k8s-extension` Azure CLI module.

## Testing Requirements

All partners who wish to merge their __Custom Private Preview Release__ (owner: _Partner_) into the __Official Private Preview Release__ are required to author additional integration tests for their extension to ensure that their extension will continue to function correctly as more extensions are added into the __Official Private Preview Release__.

For more information on creating these tests, see [Authoring Tests](docs/test_authoring.md)

## Pre-Requisites

In order to properly test all regression tests within the test suite, you must onboard an AKS cluster which you will use to generate your Azure Arc resource to test the extensions. Ensure that you have a resource group where you can onboard this cluster.

### Required Installations

The following installations are required in your environment for the integration tests to run correctly:

1. [Helm 3](https://helm.sh/docs/intro/install/)
2. [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
3. [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

## Setup

### Step 1: Install Pester

This project contains [Pester](https://pester.dev/) test framework commands that are required for the integration tests to run. In an admin powershell terminal, run

```powershell
Install-Module Pester -Force -SkipPublisherCheck
Import-Module Pester -PassThru
```

If you run into issues installing the framework, refer to the [Installation Guide](https://pester.dev/docs/introduction/installation) provided by the Pester docs.

### Step 2: Get Test suite files

You can either clone this repo (preferred option, since you will be adding your tests to this suite) or copy the files in this repo locally. Rest of the instructions here assume your working directory is k8spartner-extension-testing.

### Step 3: Update the `k8s-extension`/`k8s-extension-private` .whl package

This integration test suite references the .whl packages found in the `\bin` directory. After generating your `k8s-extension`/`k8s-extension-private` .whl package, copy your updated package into the `\bin` directory.

### Step 4: Create a `settings.json`

To onboard the AKS and Arc clusters correctly, you will need to create a `settings.json` configuration. Create a new `settings.json` file by copying the contents of the `settings.template.json` into this file. Update the subscription id, resource group, and AKS and Arc cluster name fields with your specific values.

### Step 5: Update the extension version value in `settings.json`

To ensure that the tests point to your `k8s-extension-private` `.whl` package, change the value of the `k8s-extension-private` to match your package versioning in the format (Major.Minor.Patch.Extension). For example, the `k8s_extension_private-0.1.0.openservicemesh_5-py3-none-any.whl` whl package would have extension versions set to
```json
{
    "k8s-extension": "0.1.0",
    "k8s-extension-private": "0.1.0.openservicemesh_5",
    "connectedk8s": "0.3.5"
}

```

_Note: Updates to the `connectedk8s` version and `k8s-extension` version can also be made by adding a different version of the `connectedk8s` and `k8s-extension` whl packages and changing the `connectedk8s` and `k8s-extension` values to match the (Major.Minor.Patch) version format shown above_

### Step 6: Run the Bootstrap Command
To bootstrap the environment with AKS and Arc clusters, run
```powershell
.\Bootstrap.ps1
```
This script will provision the AKS and Arc clusters needed to run the integration test suite

## Testing

### Testing All Extension Suites
To test all extension test suites, you must call `.\Test.ps1` with the `-ExtensionType` parameter set to either `Public` or `Private`. Based on this flag, the test suite will install the extension type specified below

| `-ExtensionType` |  Installs `az extension`             |
| ---------------- | ---------------------                |
| `Public`         | `k8s-extension`                      |
| `Private`        | `k8s-extension-private`              |

For example, when calling
```bash
.\Test.ps1 -ExtensionType Public
```
the script will install your `k8s-extension` whl package and run the full test suite of `*.Tests.ps1` files included in the `\test\extensions` directory

### Testing Public Extensions Only
If you only want to run the test cases against public-preview or GA extension test cases, you can use the `-OnlyPublicTests` flag to specify this
```bash
.\Test.ps1 -ExtensionType Public -OnlyPublicTests
```

### Testing Specific Extension Suite

If you only want to run the test script on your specific test file, you can do so by specifying path to your extension test suite in the execution call

```powershell
.\Test.ps1 -Path <path\to\extensionsuite>
```
For example to call the `AzureMonitor.Tests.ps1` test suite, we run
```powershell
.\Test.ps1 -ExtensionType Public -Path .\test\extensions\public\AzureMonitor.Tests.ps1
```

### Skipping Extension Re-Install

By default the `Test.ps1` script will uninstall any old versions of `k8s-extension`/'`k8s-extension-private` and re-install the version specified in `settings.json`. If you do not want this re-installation to occur, you can specify the `-SkipInstall` flag to skip this process.

```powershell
.\Test.ps1 -ExtensionType Public -SkipInstall
```

## Cleanup
To cleanup the AKS and Arc clusters you have provisioned in testing, run
```powershell
.\Cleanup.ps1
```
This will remove the AKS and Arc clusters as well as the `\tmp` directory that were created by the bootstrapping script.