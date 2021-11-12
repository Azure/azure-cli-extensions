Describe 'Flux Configuration (HTTPS) Testing' {
    BeforeAll {
        $configurationName = "https-config"
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $dummyValue = "dummyValue"
        $secretName = "git-auth-$configurationName"
    }

    It 'Creates a configuration with https user and https key on the cluster' {
        $output = az k8s-configuration flux create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -u "https://github.com/Azure/arc-k8s-demo" -n $configurationName --scope cluster --https-user $dummyValue --https-key $dummyValue --namespace $configurationName --branch main --no-wait 
        $? | Should -BeTrue

        # Loop and retry until the configuration installs and helm pod comes up
        $n = 0
        do 
        {
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            Write-Host "Provisioning State: $provisioningState"
            if ($provisioningState -eq $SUCCEEDED) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS

        Secret-Exists $secretName -Namespace $configurationName
    }

    It "Lists the configurations on the cluster" {
        $output = az k8s-configuration flux list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $? | Should -BeTrue

        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the configuration from the cluster" {
        az k8s-configuration flux delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName --force
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeFalse
    }

    It "Performs another list after the delete" {
        $output = az k8s-configuration flux list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -BeNullOrEmpty
    }
}