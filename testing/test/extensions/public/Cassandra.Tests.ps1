Describe 'Cassandra Testing' {
    BeforeAll {
        $extensionType = "microsoft.contoso.clusters"
        $extensionName = "cassandra"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Creates the extension and checks that it onboards correctly' {
        az $Env:K8sExtensionName create -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType -n $extensionName --no-wait
        $? | Should -BeTrue        

        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Check that we get the principal id back for the created identity
        $principalId = ($output | ConvertFrom-Json).identity.principalId
        $principalId | Should -Not -BeNullOrEmpty

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            # Only check the extension config, not the pod since this doesn't bring up pods
            $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            Write-Host "Got ProvisioningState: $provisioningState for the extension"  
            if ((Has-ExtensionData $extensionName) -And ($provisioningState -eq "Succeeded")) {
                break
            }
            Start-Sleep -Seconds 40
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Performs a show on the extension" {
        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Runs an update on the extension on the cluster" {
        $output = az $Env:K8sExtensionName update -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName --auto-upgrade false --no-wait
        $? | Should -BeTrue

        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "False" | Should -BeTrue

        # Loop and retry until the extension config updates
        $n = 0
        do 
        {
            $isAutoUpgradeMinorVersion = (Get-ExtensionData $extensionName).spec.autoUpgradeMinorVersion
            if (!$isAutoUpgradeMinorVersion) {  #autoUpgradeMinorVersion doesn't exist in ExtensionConfig CRD if false
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Lists the extensions on the cluster" {
        $output = az $Env:K8sExtensionName list -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters
        $? | Should -BeTrue

        $output | Should -Not -BeNullOrEmpty
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType }
        $extensionExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster" {
        $output = az $Env:K8sExtensionName delete -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName --force
        $? | Should -BeTrue

        # Extension should not be found on the cluster
        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
        $? | Should -BeFalse
        $output | Should -BeNullOrEmpty
    }

    It "Performs another list after the delete" {
        $output = az $Env:K8sExtensionName list -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
        
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionName }
        $extensionExists | Should -BeNullOrEmpty
    }
}
