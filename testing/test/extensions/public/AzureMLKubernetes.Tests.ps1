Describe 'AzureML Kubernetes Testing' {
    BeforeAll {
        $extensionType = "Microsoft.AzureML.Kubernetes"
        $extensionName = "azureml-kubernetes-connector"
        $extensionAgentNamespace = "azureml"
        $relayResourceIDKey = "relayserver.hybridConnectionResourceID"
        $serviceBusResourceIDKey = "servicebus.resourceID"

        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Creates the extension and checks that it onboards correctly with training enabled' {
        Invoke-Expression "az $Env:K8sExtensionName create -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType -n $extensionName --release-train staging --config enableTraining=true" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty        

        $output = Invoke-Expression "az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
                break
            }
            Start-Sleep -Seconds 20
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
        
        # check if relay is populated
        $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
        $relayResourceID | Should -Not -BeNullOrEmpty
    }

    It "Performs a show on the extension" {
        $output = Invoke-Expression "az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty
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
            Start-Sleep -Seconds 20
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Lists the extensions on the cluster" {
        $output = Invoke-Expression "az $Env:K8sExtensionName list -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty

        $output | Should -Not -BeNullOrEmpty
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType }
        $extensionExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster" {
        # cleanup the relay and servicebus
        $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
        $serviceBusResourceID = Get-ExtensionConfigurationSettings $extensionName $serviceBusResourceIDKey
        $relayNamespaceName = $relayResourceID.split("/")[8]
        $serviceBusNamespaceName = $serviceBusResourceID.split("/")[8]
        az relay namespace delete --resource-group $ENVCONFIG.resourceGroup --name $relayNamespaceName
        az servicebus namespace delete --resource-group $ENVCONFIG.resourceGroup --name $serviceBusNamespaceName

        $output = Invoke-Expression "az $Env:K8sExtensionName delete -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty

        # Extension should not be found on the cluster
        $output = Invoke-Expression "az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -Not -BeNullOrEmpty
        $output | Should -BeNullOrEmpty
    }

    It "Performs another list after the delete" {
        $output = Invoke-Expression "az $Env:K8sExtensionName list -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty
        $output | Should -Not -BeNullOrEmpty
        
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionName }
        $extensionExists | Should -BeNullOrEmpty
    }

    It 'Creates the extension and checks that it onboards correctly with inference enabled' {
        Invoke-Expression "az $Env:K8sExtensionName create -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType -n $extensionName --release-train staging --config enableInference=true identity.proxy.remoteEnabled=True identity.proxy.remoteHost=https://master.experiments.azureml-test.net allowInsecureConnections=True clusterPurpose=DevTest" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty        

        $output = Invoke-Expression "az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            if (Get-ExtensionStatus $extensionName -eq $SUCCESS_MESSAGE) {
                break
            }
            Start-Sleep -Seconds 20
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
        
        # check if relay is populated
        $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
        $relayResourceID | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster with inference enabled" {
        # cleanup the relay and servicebus
        $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
        $serviceBusResourceID = Get-ExtensionConfigurationSettings $extensionName $serviceBusResourceIDKey
        $relayNamespaceName = $relayResourceID.split("/")[8]
        $serviceBusNamespaceName = $serviceBusResourceID.split("/")[8]
        az relay namespace delete --resource-group $ENVCONFIG.resourceGroup --name $relayNamespaceName
        az servicebus namespace delete --resource-group $ENVCONFIG.resourceGroup --name $serviceBusNamespaceName

        $output = Invoke-Expression "az $Env:K8sExtensionName delete -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -BeNullOrEmpty

        # Extension should not be found on the cluster
        $output = Invoke-Expression "az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName" -ErrorVariable badOut
        $badOut | Should -Not -BeNullOrEmpty
        $output | Should -BeNullOrEmpty
    }
}
