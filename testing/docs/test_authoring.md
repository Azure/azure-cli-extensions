# Test Authoring

All partners are _required_ to author additional integration tests when merging their extension into the __Official Private Preview Release__. The information below outlines how to setup and author these additional tests. 

## Requirements

All partners are required to cover standard CLI scenarios in your extensions testing suite. When adding these tests and preparing to merge your updated extension whl package, your tests along with the other tests in the test suite must pass at 100%. 

Standard CLI scenarios include:

1. `az k8s-extension create`
2. `az k8s-extension show`
3. `az k8s-extension list`
4. `az k8s-extension update`
5. `az k8s-extension delete`

In addition to these standard scenarios, if there are any rigorous parameter validation standards, these should also be included in this test suite.

## Setup

The setup process for test authoring is the same as setup for generic testing. See [Setup](../README.md#setup) for guidance.

## Writing Tests

This section outlines the common flow for creating and running additional extension integration tests for the `k8s-extension` package. 

The suite utilizes the [Pester](https://pester.dev/) framework. For more information on creating generic Pester tests, see the [Create a Pester Test](https://pester.dev/docs/quick-start#creating-a-pester-test) section in the Pester docs.

### Step 1: Create Test File

To create an integration test suite for your extension, create an extension test file in the format `<extension-name>.Tests.ps1` and place the file in one of the following directories
| Extension Type         | Directory                           |
| ---------------------- | ----------------------------------- |
| General Availability   | .\test\extensions\public            |
| Public Preview         | .\test\extensions\public            |
| Private Preview        | .\test\extensions\private-preview   |

For example, to create a test suite file for the Azure Monitor extension, I create the file `AzureMonitor.Tests.ps1` in the `\test\extensions\public` directory because Container Insights extension is in _Public Preview_.

### Step 2: Setup Global Variables

All test suite files must have the following structure for importing the environment config and declaring globals

```powershell
Describe '<INSERT EXTENSION NAME> Testing' {
    BeforeAll {
        $extensionType = "<extension-type>"
        $extensionName = "<extension-name>"
        $extensionAgentName = "<extension-agent-name>"
        $extensionAgentNamespace = "<extension-agent-namespace>"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }
}
```

You can declare additional global variables for your tests by adding additional powershell variable to this `BeforeAll` block.

_Note: Commonly used constants used by all extension test suites are stored in the `Constants.ps1` file_

### Step 3: Add Tests

Adding tests to the test suite can now be performed by adding `It` blocks to the outer `Describe` block. For instance to test create on a extension in the case of AzureMonitor, I write the following test:

```powershell
Describe 'Azure Monitor Testing' {
    BeforeAll {
        $extensionType = "microsoft.azuremonitor.containers"
        $extensionName = "azuremonitor-containers"
        $extensionAgentName = "omsagent"
        $extensionAgentNamespace = "kube-system"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Creates the extension and checks that it onboards correctly' {
        $output = az k8s-extension create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --extension-type $extensionType -n $extensionName
        $? | Should -BeTrue

        $output = az k8s-extension show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
                if (Get-PodStatus $extensionAgentName -Namespace $extensionAgentNamespace -eq $POD_RUNNING) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }
}
```

The above test calls `az k8s-extension create` to create the `azuremonitor-containers` extension and retries checking that the extension resource was actually created on the Arc cluster and that the extension status successfully returns `$SUCCESS_MESSAGE` which is equivalent to `Successfully installed the extension`.

## Tips/Notes

### Accessing Extension Data

`.\Test.ps1` assumes that the user has `kubectl` and `az` installed in their environment; therefore, tests are able to access information on the extension at the service and on the arc cluster. For instance, in the above test, we access the `extensionconfig` CRDs on the arc cluster by calling

```powershell
kubectl get extensionconfigs -A -o json
```

If we want to access the extension data on the cluster with a specific `$extensionName`, we run

```powershell
(kubectl get extensionconfigs -A -o json).items | Where-Object { $_.metadata.name -eq $extensionName }
```

Because some of these commands are so common, we provide the following helper commands in the `test\Helper.ps1` file

| Command                                                       | Description                                                                                                     |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Get-ExtensionData <extensionName>                             | Retrieves the ExtensionConfig CRD in JSON format with `.meatadata.name` matching the `extensionName`            |
| Get-ExtensionStatus <extensionName>                           | Retrieves the `.status.status` from the ExtensionConfig CRD with `.meatadata.name` matching the `extensionName` |
| Get-PodStatus <extensionName> -Namespace <extensionNamespace> | Retrieves the `status.phase` from the first pod on the cluster with `.metadata.name` matching `extensionName`   |

### Stdout for Debugging

To print out to the Console for debugging while writing your test cases use the `Write-Host` command. If you attempt to use the `Write-Output` command, it will not show because of the way that Pester is invoked

```powershell
Write-Host "Some example output"
```

### Global Constants

Looking at the above test, we can see that we are accessing the `ENVCONFIG` to retrieve the environment variables from the `settings.json`. All variables in the `settings.json` are accessible from the `ENVCONFIG`. The most useful ones for testing will be `ENVCONFIG.arcClusterName` and `ENVCONFIG.resourceGroup`.

