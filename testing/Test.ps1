param (
    [string] $Path,
    [switch] $SkipInstall,
    [switch] $CI,
    [switch] $ParallelCI,
    [switch] $OnlyPublicTests,

    [Parameter(Mandatory=$True)]
    [ValidateSet('k8s-extension','k8s-configuration', 'k8s-extension-private')]
    [string]$Type
)

# Disable confirm prompt for script
# Only show errors, don't show warnings
az config set core.disable_confirm_prompt=true
az config set core.only_show_errors=true

$ENVCONFIG = Get-Content -Path $PSScriptRoot/settings.json | ConvertFrom-Json

az account set --subscription $ENVCONFIG.subscriptionId

$Env:KUBECONFIG="$PSScriptRoot/tmp/KUBECONFIG"
$TestFileDirectory="$PSScriptRoot/results"

if (-not (Test-Path -Path $TestFileDirectory)) {
    New-Item -ItemType Directory -Path $TestFileDirectory
}

if ($Type -eq 'k8s-extension') {
    $k8sExtensionVersion = $ENVCONFIG.extensionVersion.'k8s-extension'
    $Env:K8sExtensionName = "k8s-extension"

    if (!$SkipInstall) {
        Write-Host "Removing the old k8s-extension extension..."
        az extension remove -n k8s-extension
        Write-Host "Installing k8s-extension version $k8sExtensionVersion..."
        az extension add --source ./bin/k8s_extension-$k8sExtensionVersion-py3-none-any.whl
        if (!$?) {
            Write-Host "Unable to find k8s-extension version $k8sExtensionVersion, exiting..."
            exit 1
        }
    }
    if ($OnlyPublicTests) {
        $testFilePath = "$PSScriptRoot/test/extensions/public"
    } else {
        $testFilePath = "$PSScriptRoot/test/extensions"
    }
} elseif ($Type -eq 'k8s-extension-private') {
    $k8sExtensionPrivateVersion = $ENVCONFIG.extensionVersion.'k8s-extension-private'
    $Env:K8sExtensionName = "k8s-extension-private"

    if (!$SkipInstall) {
        Write-Host "Removing the old k8s-extension-private extension..."
        az extension remove -n k8s-extension-private
        Write-Host "Installing k8s-extension-private version $k8sExtensionPrivateVersion..."
        az extension add --source ./bin/k8s_extension_private-$k8sExtensionPrivateVersion-py3-none-any.whl
        if (!$?) {
            Write-Host "Unable to find k8s-extension-private version $k8sExtensionPrivateVersion, exiting..."
            exit 1
        }
    }
    if ($OnlyPublicTests) {
        $testFilePath = "$PSScriptRoot/test/extensions/public"
    } else {
        $testFilePath = "$PSScriptRoot/test/extensions"
    }
} elseif ($Type -eq 'k8s-configuration') {
    $k8sConfigurationVersion = $ENVCONFIG.extensionVersion.'k8s-configuration'
    if (!$SkipInstall) {
        Write-Host "Removing the old k8s-configuration extension..."
        az extension remove -n k8s-configuration
        Write-Host "Installing k8s-configuration version $k8sConfigurationVersion..."
        az extension add --source ./bin/k8s_configuration-$k8sConfigurationVersion-py3-none-any.whl
    }
    $testFilePaths = "$PSScriptRoot/test/configurations"
}

if ($ParallelCI) {
    # This runs the tests in parallel during the CI pipline to speed up testing

    Write-Host "Invoking Pester to run tests from '$testFilePath'..."
    $testFiles = @()
    foreach ($paths in $testFilePaths) 
    {
        $temp = Get-ChildItem $paths
        $testFiles += $temp
    }
    $resultFileNumber = 0
    foreach ($testFile in $testFiles)
    {
        $resultFileNumber++
        $testName = Split-Path $testFile –leaf
        Start-Job -ArgumentList $testName, $testFile, $resultFileNumber, $TestFileDirectory -Name $testName -ScriptBlock {
            param($name, $testFile, $resultFileNumber, $testFileDirectory)

            Write-Host "$testFile to result file #$resultFileNumber"
            $testResult = Invoke-Pester $testFile -Passthru -Output Detailed
            $testResult | Export-JUnitReport -Path "$testFileDirectory/$name.xml"
        }
    }

    do {
        Write-Host ">> Still running tests @ $(Get-Date –Format "HH:mm:ss")" –ForegroundColor Blue
        Get-Job | Where-Object { $_.State -eq "Running" } | Format-Table –AutoSize 
        Start-Sleep –Seconds 30
    } while((Get-Job | Where-Object { $_.State -eq "Running" } | Measure-Object).Count -ge 1)

    Get-Job | Wait-Job
    $failedJobs = Get-Job | Where-Object { -not ($_.State -eq "Completed")}
    Get-Job | Receive-Job –AutoRemoveJob –Wait –ErrorAction 'Continue'

    if ($failedJobs.Count -gt 0) {
        Write-Host "Failed Jobs" –ForegroundColor Red
        $failedJobs
        throw "One or more tests failed"
    }
} elseif ($CI) {
    if ($Path) {
        $testFilePath = "$PSScriptRoot/$Path"
    }
    Write-Host "Invoking Pester to run tests from '$testFilePath'..."
    $testResult = Invoke-Pester $testFilePath -Passthru -Output Detailed
    $testName = Split-Path $testFilePath –leaf
    $testResult | Export-JUnitReport -Path "$testFileDirectory/$testName.xml"
} else {
    if ($Path) {
        Write-Host "Invoking Pester to run tests from '$PSScriptRoot/$Path'"
        Invoke-Pester -Output Detailed $PSScriptRoot/$Path
    } else {
        Write-Host "Invoking Pester to run tests from '$testFilePath'..."
        Invoke-Pester -Output Detailed $testFilePath
    }
}
