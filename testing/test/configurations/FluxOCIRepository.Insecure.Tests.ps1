Describe 'Flux Configuration (OCI Repository - Insecure Mode) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "oci://ghcr.io/stefanprodan/manifests/podinfo"
        $configurationName = "oci-insecure-config"
        $tag = "latest"
    }

    It 'Creates a configuration with insecure mode enabled on the cluster' {
        az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --namespace $configurationName --scope cluster --kind oci -u $url --tag $tag --oci-insecure --kustomization name=insecuretest path=./ prune=true disable-health-check=true --no-wait
        $? | Should -BeTrue

        $n = 0
        do {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            if ($?) {
                $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
                $provisioningState = ($output | ConvertFrom-Json).provisioningState
                $urlReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("url").GetString()
                $tagReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("repositoryRef").GetProperty("tag").GetString()
                $insecureFlag = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("insecure").GetBoolean()

                Write-Host "Provisioning State: $provisioningState"
                Write-Host "OCI Repository URL: $urlReturned"
                Write-Host "OCI Repository Tag: $tagReturned"
                Write-Host "Insecure Flag: $insecureFlag"

                if ($provisioningState -eq $SUCCEEDED -and $insecureFlag -eq $true -and $urlReturned -eq $url -and $tagReturned -eq $tag) {
                    break
                }
            } else {
                Write-Host "Show command failed (attempt $n)."
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Toggle the insecure setting for ociRepo' {
        az k8s-configuration flux update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --kind oci --oci-insecure=false --no-wait
        $? | Should -BeTrue

        $n = 0
        do {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            if ($?) {
                $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
                $provisioningState = ($output | ConvertFrom-Json).provisioningState
                $ociRepo = $jsonOutput.RootElement.GetProperty("ociRepository")

                $insecureFlag = $false
                $hasProp = $false
                try {
                    $insecureFlag = $ociRepo.GetProperty("insecure").GetBoolean()
                    $hasProp = $true
                } catch { $hasProp = $false }

                Write-Host "Provisioning State: $provisioningState"
                Write-Host "Insecure Present: $hasProp  Value: $insecureFlag"

                # Accept either explicit false or property removed (treated as secure)
                if ($provisioningState -eq $SUCCEEDED -and (-not $hasProp -or ($hasProp -and -not $insecureFlag))) {
                    break
                }
            } else {
                Write-Host "Show command failed (attempt $n)."
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Deletes the configuration from the cluster' {
        az k8s-configuration flux delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --force
        $? | Should -BeTrue

        az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
        $? | Should -BeFalse
    }

    It 'Performs another list after the delete' {
        $output = az k8s-configuration flux list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters"
        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -BeNullOrEmpty
    }
}