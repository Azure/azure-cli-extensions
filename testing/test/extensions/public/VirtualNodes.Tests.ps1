Describe 'Azure VirtualNodes Testing' {
    BeforeAll {
        $extensionType = "microsoft.virtualnodes"
        $extensionName = "virtualnodes"

        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Creates the extension and checks that it onboards correctly' {
        $output = az $Env:K8sExtensionName create -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters --extension-type $extensionType -n $extensionName --no-wait
        $? | Should -BeTrue

        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters -n $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        $autoUpgradeMode = ($output | ConvertFrom-Json).autoUpgradeMode
        $autoUpgradeMode -eq "compatible" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do
        {
            if (Has-ExtensionData $extensionName) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Performs a show on the extension" {
        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters -n $extensionName
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Lists the extensions on the cluster" {
        $output = az $Env:K8sExtensionName list -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters
        $? | Should -BeTrue

        $output | Should -Not -BeNullOrEmpty
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType }
        $extensionExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster" {
        $output = az $Env:K8sExtensionName delete -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters -n $extensionName --force
        $? | Should -BeTrue

        # Extension should not be found on the cluster
        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters -n $extensionName
        $? | Should -BeFalse
        $output | Should -BeNullOrEmpty
    }

    It "Performs another list after the delete" {
        $output = az $Env:K8sExtensionName list -c $($ENVCONFIG.aksClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type managedClusters
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty

        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.name -eq $extensionName }
        $extensionExists | Should -BeNullOrEmpty
    }
}
