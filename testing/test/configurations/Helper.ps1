function Get-ConfigData {
    param(
        [string]$configName
    )

    $output = kubectl get gitconfigs -A -o json | ConvertFrom-Json
    return $output.items | Where-Object { $_.metadata.name -eq $configurationName }
}

function Get-ConfigStatus {
    param(
        [string]$configName
    )

    $configData = Get-ConfigData $configName
    if ($configData -ne $null) {
        return $configData.status.status
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
    return $podData.status.phase
}

function Secret-Exists {
    param(  
        [string]$secretName,
        [string]$Namespace
    )

    $allSecretData = kubectl get secrets -n $Namespace -o json | ConvertFrom-Json
    $secretData = $allSecretData.items | Where-Object { $_.metadata.name -Match $secretName }
    if ($secretData.Length -ge 1) {
        return $true
    }
    return $false
}