Describe 'AzureML Kubernetes Testing' {
    BeforeAll {
        $extensionType = "Microsoft.AzureML.Kubernetes"
        $extensionName = "azureml-kubernetes-connector"
        $extensionAgentNamespace = "azureml"
        $relayResourceIDKey = "relayserver.hybridConnectionResourceID"

        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Creates the extension and checks that it onboards correctly' {
        $output = az k8s-extension create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --extension-type $extensionType --name $extensionName --release-train preview --config enableTraining=true allowInsecureConnections=true
        $? | Should -BeTrue

        $output = az k8s-extension show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --name $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
        
        # check if relay is populated
        $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
        $relayResourceID | Should -Not -BeNullOrEmpty
    }

    It "Performs a show on the extension" {
        $output = az k8s-extension show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --name $extensionName
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Runs an update on the extension on the cluster" {
        Set-ItResult -Skipped -Because "Update is not a valid scenario for now"
        az k8s-extension update --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --name $extensionName --auto-upgrade-minor-version false
        $? | Should -BeTrue

        $output = az k8s-extension show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --name $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "False" | Should -BeTrue

        # Loop and retry until the extension config updates
        $n = 0
        do 
        {
            $isAutoUpgradeMinorVersion = (Get-ExtensionData $extensionName).spec.autoUpgradeMinorVersion
            if (!$isAutoUpgradeMinorVersion) {  #autoUpgradeMinorVersion doesn't exist in ExtensionConfig CRD if false
                if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Lists the extensions on the cluster" {
        $output = az k8s-extension list --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $? | Should -BeTrue

        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType }
        $extensionExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster" {
        az k8s-extension delete --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --name $extensionName
        $? | Should -BeTrue

        # Extension should not be found on the cluster
        az k8s-extension show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters --name $extensionName
        $? | Should -BeFalse
    }

    It "Performs another list after the delete" {
        $output = az k8s-extension list --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionName }
        $extensionExists | Should -BeNullOrEmpty
    }
}
