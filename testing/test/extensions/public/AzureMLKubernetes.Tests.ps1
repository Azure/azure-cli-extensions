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

    It 'Creates the extension and checks that it onboards correctly with inference and SSL enabled' {
        $sslKeyPemFile = Join-Path (Join-Path (Join-Path (Split-Path $PSScriptRoot -Parent) "data") "azure_ml") "test_key.pem"
        $sslCertPemFile = Join-Path (Join-Path (Join-Path (Split-Path $PSScriptRoot -Parent) "data") "azure_ml") "test_cert.pem"
        az $Env:K8sExtensionName create -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType -n $extensionName --release-train staging --config enableInference=true identity.proxy.remoteEnabled=True identity.proxy.remoteHost=https://master.experiments.azureml-test.net inferenceRouterServiceType=nodePort sslCname=test.domain --config-protected sslKeyPemFile=$sslKeyPemFile sslCertPemFile=$sslCertPemFile --no-wait
        $? | Should -BeTrue        

        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue

        $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
        $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the extension installs
        $n = 0
        do 
        {
            if (Has-ExtensionData $extensionName) {
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
        $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }


    It "Lists the extensions on the cluster" {
        $output = az $Env:K8sExtensionName list -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters
        $? | Should -BeTrue

        $output | Should -Not -BeNullOrEmpty
        $extensionExists = $output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType }
        $extensionExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the extension from the cluster with inference enabled" {
        # cleanup the relay and servicebus
        $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
        $serviceBusResourceID = Get-ExtensionConfigurationSettings $extensionName $serviceBusResourceIDKey
        $relayNamespaceName = $relayResourceID.split("/")[8]
        $serviceBusNamespaceName = $serviceBusResourceID.split("/")[8]
        az relay namespace delete --resource-group $ENVCONFIG.resourceGroup --name $relayNamespaceName
        az servicebus namespace delete --resource-group $ENVCONFIG.resourceGroup --name $serviceBusNamespaceName

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

    # It 'Creates the extension and checks that it onboards correctly with training enabled' {
    #     az $Env:K8sExtensionName create -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType -n $extensionName --release-train staging --config enableTraining=true
    #     $? | Should -BeTrue        

    #     $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
    #     $? | Should -BeTrue

    #     $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
    #     $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

    #     # Loop and retry until the extension installs
    #     $n = 0
    #     do 
    #     {
    #         if (Has-ExtensionData $extensionName) {
    #             break
    #         }
    #         Start-Sleep -Seconds 20
    #         $n += 1
    #     } while ($n -le $MAX_RETRY_ATTEMPTS)
    #     $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
        
    #     # check if relay is populated
    #     $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
    #     $relayResourceID | Should -Not -BeNullOrEmpty
    # }

    # It "Deletes the extension from the cluster" {
    #     # cleanup the relay and servicebus
    #     $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
    #     $serviceBusResourceID = Get-ExtensionConfigurationSettings $extensionName $serviceBusResourceIDKey
    #     $relayNamespaceName = $relayResourceID.split("/")[8]
    #     $serviceBusNamespaceName = $serviceBusResourceID.split("/")[8]
    #     az relay namespace delete --resource-group $ENVCONFIG.resourceGroup --name $relayNamespaceName
    #     az servicebus namespace delete --resource-group $ENVCONFIG.resourceGroup --name $serviceBusNamespaceName

    #     $output = az $Env:K8sExtensionName delete -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
    #     $? | Should -BeTrue

    #     # Extension should not be found on the cluster
    #     $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
    #     $? | Should -BeFalse
    #     $output | Should -BeNullOrEmpty
    # }

    # It 'Creates the extension and checks that it onboards correctly with inference enabled' {
    #     az $Env:K8sExtensionName create -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType -n $extensionName --release-train staging --config enableInference=true identity.proxy.remoteEnabled=True identity.proxy.remoteHost=https://master.experiments.azureml-test.net allowInsecureConnections=True inferenceLoadBalancerHA=false
    #     $? | Should -BeTrue        

    #     $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
    #     $? | Should -BeTrue

    #     $isAutoUpgradeMinorVersion = ($output | ConvertFrom-Json).autoUpgradeMinorVersion 
    #     $isAutoUpgradeMinorVersion.ToString() -eq "True" | Should -BeTrue

    #     # Loop and retry until the extension installs
    #     $n = 0
    #     do 
    #     {
    #         if (Has-ExtensionData $extensionName) {
    #             break
    #         }
    #         Start-Sleep -Seconds 20
    #         $n += 1
    #     } while ($n -le $MAX_RETRY_ATTEMPTS)
    #     $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
        
    #     # check if relay is populated
    #     $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
    #     $relayResourceID | Should -Not -BeNullOrEmpty
    # }

    # It "Deletes the extension from the cluster with inference enabled" {
    #     # cleanup the relay and servicebus
    #     $relayResourceID = Get-ExtensionConfigurationSettings $extensionName $relayResourceIDKey
    #     $serviceBusResourceID = Get-ExtensionConfigurationSettings $extensionName $serviceBusResourceIDKey
    #     $relayNamespaceName = $relayResourceID.split("/")[8]
    #     $serviceBusNamespaceName = $serviceBusResourceID.split("/")[8]
    #     az relay namespace delete --resource-group $ENVCONFIG.resourceGroup --name $relayNamespaceName
    #     az servicebus namespace delete --resource-group $ENVCONFIG.resourceGroup --name $serviceBusNamespaceName

    #     $output = az $Env:K8sExtensionName delete -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
    #     $? | Should -BeTrue

    #     # Extension should not be found on the cluster
    #     $output = az $Env:K8sExtensionName show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters -n $extensionName
    #     $? | Should -BeFalse
    #     $output | Should -BeNullOrEmpty
    # }
}
