Describe 'Azure Monitor Testing' {
    BeforeAll {
        $extensionType = "microsoft.azuremonitor.containers"
        $extensionName = "azuremonitor-containers"
        $extensionAgentName = "omsagent"
        $extensionAgentNamespace = "kube-system"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Creates the extension and checks that it onboards correctly' {
        $output = az $Env:K8sExtensionName create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --extension-type $extensionType -n $extensionName
        $? | Should -BeTrue

        $output = az $Env:K8sExtensionName show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
                if (Get-PodStatus $extensionAgentName -Namespace $extensionAgentNamespace -eq $POD_RUNNING) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Performs a show on the extension" {
        $output = az $Env:K8sExtensionName show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Runs an update on the extension on the cluster" {
        Set-ItResult -Skipped -Because "Update is not a valid scenario for now"

        # az $Env:K8sExtensionName update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName --auto-upgrade-minor-version false
        # $? | Should -BeTrue

        # $output = az $Env:K8sExtensionName show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName
        # $? | Should -BeTrue

        # $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        # $isAutoUpgradeMinorVersion.ToString() -eq "False" | Should -BeTrue

        # # Loop and retry until the extension config updates
        # $n = 0
        # do 
        # {
        #     $isAutoUpgradeMinorVersion = (Get-ExtensionData $extensionName).spec.autoUpgradeMinorVersion
        #     if (!$isAutoUpgradeMinorVersion) {  #autoUpgradeMinorVersion doesn't exist in ExtensionConfig CRD if false
        #         if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
        #             if (Get-PodStatus $extensionAgentName -Namespace $extensionAgentNamespace -eq $POD_RUNNING) {
        #                 break
        #             }
        #         }
        #     }
        #     Start-Sleep -Seconds 10
        #     $n += 1
        # } while ($n -le $MAX_RETRY_ATTEMPTS)
        # $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Lists the extensions on the cluster" {
        $output = az $Env:K8sExtensionName list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $? | Should -BeTrue

        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType }
        $extensionExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster" {
        az $Env:K8sExtensionName delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue

        # Extension should not be found on the cluster
        az $Env:K8sExtensionName show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $extensionName
        $? | Should -BeFalse
    }

    It "Performs another list after the delete" {
        $output = az $Env:K8sExtensionName list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionName }
        $extensionExists | Should -BeNullOrEmpty
    }
}
