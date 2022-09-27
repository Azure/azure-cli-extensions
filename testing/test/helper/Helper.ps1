function Get-ExtensionData {
    param(
        [string]$extensionName
    )

    $output = kubectl get extensionconfigs -A -o json | ConvertFrom-Json
    return $output.items | Where-Object { $_.metadata.name -eq $extensionName }
}

function Has-ExtensionData {
    param(
        [string]$extensionName
    )
    $extensionData = Get-ExtensionData $extensionName
    if ($extensionData) {
        return $true
    }
    return $false
}


function Has-Identity-Provisioned {
    $output = kubectl get azureclusteridentityrequests -n azure-arc container-insights-clusteridentityrequest -o json | ConvertFrom-Json
    return ($null -ne $output.status.expirationTime) -and ($null -ne $output.status.tokenReference.dataName) -and ($null -ne $output.status.tokenReference.secretName)
}

function Get-ExtensionStatus {
    param(
        [string]$extensionName
    )

    $extensionData = Get-ExtensionData $extensionName
    if ($extensionData) {
        return $extensionData.status.status
    }
    return $null
}

function Get-PodStatus {
    param(  
        [string]$podName,
        [string]$Namespace
    )

    $allPodData = kubectl get pods -n $Namespace -o json | ConvertFrom-Json
    $podData = $allPodData.items | Where-Object { $_.metadata.name -Match $podName }
    if ($podData.Length -gt 1) {
        return $podData[0].status.phase
    }
    return $podData.status.phase
}

function Get-ExtensionConfigurationSettings {
    param(
        [string]$extensionName,
        [string]$configKey
    )

    $extensionData = Get-ExtensionData $extensionName
    if ($extensionData) {
        return $extensionData.spec.parameter."$configKey"
    }
    return $null
}

function Check-Error {
    param(
        [string]$output
    )
    $hasError = $output -CMatch "ERROR"
    return $hasError
}