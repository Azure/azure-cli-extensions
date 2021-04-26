param (
    [string] $Path,
    [switch] $SkipInstall,
    [switch] $CI,
    [switch] $OnlyPublicTests,

    [Parameter(Mandatory=$True)]
    [ValidateSet('Public','Private')]
    [string]$ExtensionType
)

# Disable confirm prompt for script
az config set core.disable_confirm_prompt=true

$ENVCONFIG = Get-Content -Path $PSScriptRoot/settings.json | ConvertFrom-Json

az account set --subscription $ENVCONFIG.subscriptionId

$Env:KUBECONFIG="$PSScriptRoot/tmp/KUBECONFIG"

if ($ExtensionType -eq "Public") {
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
} else {
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
}

if ($CI) {
    if ($OnlyPublicTests) {
        Write-Host "Invoking Pester to run tests from '$PSScriptRoot/test/extensions/public'"
        $testResult = Invoke-Pester $PSScriptRoot/test/extensions/public -Passthru -Output Detailed
        $testResult | Export-JUnitReport -Path TestResults.xml
    }
    else {
        Write-Host "Invoking Pester to run tests from '$PSScriptRoot/test/extensions'"
        $testResult = Invoke-Pester $PSScriptRoot/test/extensions -Passthru -Output Detailed
        $testResult | Export-JUnitReport -Path TestResults.xml
    }
} else {
    if ($Path) {
        Write-Host "Invoking Pester to run tests from '$PSScriptRoot/$Path'"
        Invoke-Pester -Output Detailed $PSScriptRoot/$Path
    } else {
        if ($OnlyPublicTests) {
            Write-Host "Invoking Pester to run tests from '$PSScriptRoot/test/extensions/public'"
            Invoke-Pester -Output Detailed $PSScriptRoot/test/extensions/public
        }
        else {
            Write-Host "Invoking Pester to run tests from '$PSScriptRoot/test/extensions'"
            Invoke-Pester -Output Detailed $PSScriptRoot/test/extensions
        }
    }
}
