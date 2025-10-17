Describe 'Flux Configuration (OCI Repository - Service Account) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "oci://ghcr.io/stefanprodan/manifests/podinfo"
        $configurationName = "oci-service-account-config"
        $tag = "latest"
    }

    It 'Creates a configuration with Service Account auth' {
        $output = az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --namespace $configurationName --scope cluster --kind oci -u $url --tag $tag --service-account-name "flux-sa" --kustomization name=workloadtest path=./ prune=true --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $serviceAccountName = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("serviceAccountName").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Service Account Name: $serviceAccountName"
            if ($provisioningState -eq $SUCCEEDED -and $serviceAccountName -eq "flux-sa") {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Update service-account-name for the flux configurations on the cluster" {
        $output = az k8s-configuration flux update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --kind oci --service-account-name "flux-sa2" --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $serviceAccountName = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("serviceAccountName").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Service Account Name: $serviceAccountName"
            if ($provisioningState -eq $SUCCEEDED -and $serviceAccountName -eq "flux-sa2") {
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