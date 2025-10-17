Describe 'Flux Configuration (OCI Repository - Workload Identity) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "oci://ghcr.io/stefanprodan/manifests/podinfo"
        $configurationName = "oci-workload-identity-config"
        $tag = "latest"
    }

    It 'Creates a configuration with Workload Identity enabled on the cluster' {
        $output = az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --namespace $configurationName --scope cluster --kind oci -u $url --tag $tag --use-workload-identity --kustomization name=workloadtest path=./ prune=true disable-health-check=true --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $urlReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("url").GetString()
            $tagReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("repositoryRef").GetProperty("tag").GetString()
            $workloadIdentityStatus = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("useWorkloadIdentity").GetBoolean()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "OCI Repository URL: $urlReturned"
            Write-Host "OCI Repository Tag: $tagReturned"
            Write-Host "Workload Identity Status: $workloadIdentityStatus"
            if ($provisioningState -eq $SUCCEEDED -and $workloadIdentityStatus -eq $true -and $urlReturned -eq $url -and $tagReturned -eq $tag) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Update tag, url and disable Workload Identity for the flux configurations on the cluster" {
        $newTag = "1.2.0"
        $newUrl = "oci://ghcr.io/stefanprodan/manifests/podinfo2"
        $output = az k8s-configuration flux update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --kind oci -u $newUrl --tag $newTag --use-workload-identity=false --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $urlReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("url").GetString()
            $tagReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("repositoryRef").GetProperty("tag").GetString()
            $workloadIdentityStatus = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("useWorkloadIdentity").GetBoolean()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "OCI Repository URL: $urlReturned"
            Write-Host "OCI Repository Tag: $tagReturned"
            Write-Host "Workload Identity Status: $workloadIdentityStatus"
            if ($provisioningState -eq $SUCCEEDED -and $workloadIdentityStatus -eq $false -and $urlReturned -eq $newUrl -and $tagReturned -eq $newTag) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Deletes the configuration from the cluster" {
        az k8s-configuration flux delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --force
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
        $? | Should -BeFalse
    }

    It "Performs another list after the delete" {
        $output = az k8s-configuration flux list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters"
        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -BeNullOrEmpty
    }
}