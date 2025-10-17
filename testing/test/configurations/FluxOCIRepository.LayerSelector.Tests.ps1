Describe 'Flux Configuration (OCI Repository - Layer Selector) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "oci://ghcr.io/stefanprodan/manifests/podinfo"
        $configurationName = "oci-service-account-config"
        $tag = "latest"
        $mediaType = "application/vnd.cncf.helm.chart.content.v1.tar+gzip"
        $operation = "extract"
    }

    It 'Creates a configuration with layer selector configured for oci artifact' {
        $output = az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --namespace $configurationName --scope cluster --kind oci -u $url --tag $tag --oci-media-type $mediaType --oci-operation $operation --kustomization name=workloadtest path=./ prune=true --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $ociMediaType = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("layerSelector").GetProperty("mediaType").GetString()
            $ociOperation = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("layerSelector").GetProperty("operation").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "OCI Media Type: $ociMediaType"
            Write-Host "OCI Operation: $ociOperation"
            if ($provisioningState -eq $SUCCEEDED -and $ociMediaType -eq $mediaType -and $ociOperation -eq $operation) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Update layer selector values for oci artifact for the flux configurations on the cluster" {
        $mediaType = "application/vnd.cncf.helm.chart.content.v2.tar+gzip"
        $operation = "copy"
        $output = az k8s-configuration flux update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --kind oci --oci-media-type $mediaType --oci-operation $operation --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $ociMediaType = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("layerSelector").GetProperty("mediaType").GetString()
            $ociOperation = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("layerSelector").GetProperty("operation").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "OCI Media Type: $ociMediaType"
            Write-Host "OCI Operation: $ociOperation"
            if ($provisioningState -eq $SUCCEEDED -and $ociMediaType -eq $mediaType -and $ociOperation -eq $operation) {
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