Describe 'Flux Configuration (Azure Blob Storage - Account Key) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "https://fluxblobstorageclitest.blob.core.windows.net/"
        $containerName = "arc-k8s-demo"
        $accountKey = $(az keyvault secret show --name blobAccountKey --vault-name fluxExtTestingSecrets | jq .value -r)
        $configurationName = "blob-accountkey-config"
    }

    It 'Creates a configuration with account key on the cluster' {
        $output = az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" --kind azblob -u $url -n $configurationName --scope cluster --namespace $configurationName --container-name $containerName --account-key $accountKey --kustomization name=test path=./ prune=true --no-wait
        $? | Should -BeTrue

        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            Write-Host "Provisioning State: $provisioningState"
            if ($provisioningState -eq $SUCCEEDED) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Lists the configurations on the cluster" {
        $output = az k8s-configuration flux list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters"
        $? | Should -BeTrue

        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -Not -BeNullOrEmpty
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