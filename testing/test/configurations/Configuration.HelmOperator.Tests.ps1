Describe 'Source Control Configuration (Helm Operator Properties) Testing' {
    BeforeAll {
        $configurationName = "helm-enabled-config"
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $customOperatorParams = "--set helm.versions=v3 --set mycustomhelmvalue=yay"
        $customChartVersion = "0.6.0"
    }

    It 'Creates a configuration with helm enabled on the cluster' {
        $output = az k8s-configuration create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -u "https://github.com/Azure/arc-k8s-demo" -n $configurationName --scope cluster --enable-helm-operator --operator-namespace $configurationName --helm-operator-params "--set helm.versions=v3"
        $? | Should -BeTrue

        # Loop and retry until the configuration installs and helm pod comes up
        $n = 0
        do 
        {
            if (Get-ConfigStatus $configurationName -eq $SUCCESS_MESSAGE) {
                if (Get-PodStatus "$configurationName-helm" -Namespace $configurationName -eq $POD_RUNNING ) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Lists the configurations on the cluster" {
        $output = az k8s-configuration list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $? | Should -BeTrue

        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -Not -BeNullOrEmpty
    }

    It "Deletes the configuration from the cluster" {
        az k8s-configuration delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az k8s-configuration show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeFalse
    }

    It "Performs another list after the delete" {
        $output = az k8s-configuration list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -BeNullOrEmpty
    }
}