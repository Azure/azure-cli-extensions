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

    It "Updates the helm operator params and performs a show" {
        Set-ItResult -Skipped -Because "Update is not a valid scenario for now"
        
        az k8s-configuration update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --helm-operator-params $customOperatorParams
        $? | Should -BeTrue

        $output = az k8s-configuration show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeTrue

        $configData = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        ($configData.helmOperatorProperties.chartValues -eq $customOperatorParams) | Should -BeTrue

        # Loop and retry until the configuration updates
        $n = 0
        do
        {
            $helmOperatorChartValues = (Get-ConfigData $configurationName).spec.helmOperatorProperties.chartValues
            if ($helmOperatorChartValues -ne $null -And $helmOperatorChartValues.ToString() -eq $customOperatorParams) {
                if (Get-ConfigStatus $configurationName -Match $SUCCESS_MESSAGE) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Updates the helm operator chart version and performs a show" {
        Set-ItResult -Skipped -Because "Update is not a valid scenario for now"
        
        az k8s-configuration update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --helm-operator-chart-version $customChartVersion
        $? | Should -BeTrue

        $output = az k8s-configuration show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeTrue

        # Check that the helmOperatorProperties chartValues didn't change
        $configData = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        ($configData.helmOperatorProperties.chartValues -eq $customOperatorParams) | Should -BeTrue
        ($configData.helmOperatorProperties.chartVersion -eq $customChartVersion) | Should -BeTrue

        # Loop and retry until the configuration updates
        $n = 0
        do
        {
            $helmOperatorChartVersion = (Get-ConfigData $configurationName).spec.helmOperatorProperties.chartVersion
            if ($helmOperatorChartVersion -ne $null -And $helmOperatorChartVersion.ToString() -eq $customChartVersion) {
                if (Get-ConfigStatus $configurationName -Match $SUCCESS_MESSAGE) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Disables the helm operator on the cluster" {
        Set-ItResult -Skipped -Because "Update is not a valid scenario for now"

        az k8s-configuration update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --enable-helm-operator=false
        $? | Should -BeTrue

        $output = az k8s-configuration show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeTrue

        $helmOperatorEnabled = ($output | ConvertFrom-Json).enableHelmOperator
        $helmOperatorEnabled.ToString() -eq "False" | Should -BeTrue

        # Loop and retry until the configuration updates
        $n = 0
        do {
            $helmOperatorEnabled = (Get-ConfigData $configurationName).spec.enableHelmOperator
            if ($helmOperatorEnabled -ne $null -And $helmOperatorEnabled.ToString() -eq "False") {
                if (Get-ConfigStatus $configurationName -Match $SUCCESS_MESSAGE) {
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