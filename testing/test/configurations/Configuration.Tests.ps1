Describe 'Basic Source Control Configuration Testing' {
    BeforeAll {
        $configurationName = "basic-config"
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1
    }

    It 'Creates a configuration and checks that it onboards correctly' {
        az k8s-configuration create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -u "https://github.com/Azure/arc-k8s-demo" -n $configurationName --scope cluster --enable-helm-operator=false --operator-namespace $configurationName
        $? | Should -BeTrue

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            if (Get-ConfigStatus $configurationName -Match $SUCCESS_MESSAGE) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Performs a show on the configuration" {
        $output = az k8s-configuration show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Runs an update on the configuration on the cluster" {
        Set-ItResult -Skipped -Because "Update is not a valid scenario for now"

        az k8s-configuration update -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName --enable-helm-operator
        $? | Should -BeTrue

        $output = az k8s-configuration show --cluster-name $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configurationName
        $? | Should -BeTrue

        $helmOperatorEnabled = ($output | ConvertFrom-Json).enableHelmOperator
        $helmOperatorEnabled.ToString() -eq "True" | Should -BeTrue

        # Loop and retry until the configuration updates
        $n = 0
        do {
            $helmOperatorEnabled = (Get-ConfigData $configurationName).spec.enableHelmOperator
            if ($helmOperatorEnabled -And $helmOperatorEnabled.ToString() -eq "True") {
                if (Get-ConfigStatus $configurationName -Match $SUCCESS_MESSAGE) {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Performs a re-PUT of the configuration on the cluster, with HTTPS in caps" {
        az k8s-configuration create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -u "HTTPS://github.com/Azure/arc-k8s-demo" -n $configurationName --scope cluster --enable-helm-operator=false --operator-namespace $configurationName
        $? | Should -BeTrue
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