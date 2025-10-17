Describe 'Flux Configuration (OCI Repository - Tls Config) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "oci://ghcr.io/stefanprodan/manifests/podinfo"
        $configurationName = "oci-tls-config"
        $tag = "latest"
        $tlsClientCertificate = "Y2xpZW50Q2VydGlmaWNhdGU="
        $tlsPrivateKey = "cHJpdmF0ZUtleQ=="
        $tlsCaCertificate = "Y2FDZXJ0aWZpY2F0ZQ=="
    }

    It 'Creates a configuration with Tls Config Auth' {
        $output = az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --namespace $configurationName --scope cluster --kind oci -u $url --tag $tag --tls-ca-certificate $tlsCaCertificate --tls-private-key $tlsPrivateKey --tls-client-certificate $tlsClientCertificate --kustomization name=workloadtest path=./ prune=true --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $clientCertificate = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("tlsConfig").GetProperty("clientCertificate").GetString()
            $privateKey = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("tlsConfig").GetProperty("privateKey").GetString()
            $caCertificate = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("tlsConfig").GetProperty("caCertificate").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Client Certificate: $clientCertificate"
            Write-Host "Private Key: $privateKey"
            Write-Host "CA Certificate: $caCertificate"
            if ($provisioningState -eq $SUCCEEDED -and $clientCertificate -eq "<redacted>" -and $privateKey -eq "<redacted>" -and $caCertificate -eq "<redacted>") {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Update caCertificate for the flux configurations on the cluster" {
        $tlsCaCertificate = "YWFDZXJ0aWZpY2F0ZU5ldw=="
        $output = az k8s-configuration flux update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --kind oci --tls-ca-certificate $tlsCaCertificate --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $caCertificate = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("tlsConfig").GetProperty("caCertificate").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "CA Certificate: $caCertificate"
            if ($provisioningState -eq $SUCCEEDED -and $caCertificate -eq "<redacted>") {
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