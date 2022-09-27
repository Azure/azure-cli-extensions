Describe 'Source Control Configuration (SSH Configs) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $RSA_KEYPATH = "$TMP_DIRECTORY\rsa.private"
        $DSA_KEYPATH = "$TMP_DIRECTORY\dsa.private"
        $ECDSA_KEYPATH = "$TMP_DIRECTORY\ecdsa.private"
        $ED25519_KEYPATH = "$TMP_DIRECTORY\ed25519.private"

        $KEY_ARR = [System.Tuple]::Create("rsa", $RSA_KEYPATH), [System.Tuple]::Create("dsa", $DSA_KEYPATH), [System.Tuple]::Create("ecdsa", $ECDSA_KEYPATH), [System.Tuple]::Create("ed25519", $ED25519_KEYPATH)
        foreach ($keyTuple in $KEY_ARR) {
            # Automattically say yes to overwrite with ssh-keygen
            Write-Output "y" | ssh-keygen -t $keyTuple.Item1 -f $keyTuple.Item2 -P """"
        }

        $SSH_GIT_URL = "git://github.com/anubhav929/flux-get-started.git"
        $HTTP_GIT_URL = "https://github.com/Azure/arc-k8s-demo"

        $configDataRSA = [System.Tuple]::Create("rsa-config", $RSA_KEYPATH)
        $configDataDSA = [System.Tuple]::Create("dsa-config", $DSA_KEYPATH)
        $configDataECDSA = [System.Tuple]::Create("ecdsa-config", $ECDSA_KEYPATH)
        $configDataED25519 = [System.Tuple]::Create("ed25519-config", $ED25519_KEYPATH)

        $CONFIG_ARR = $configDataRSA, $configDataDSA, $configDataECDSA, $configDataED25519
    }

    It 'Creates a configuration with each type of ssh private key' {
        foreach($configData in $CONFIG_ARR) {
            az k8s-configuration create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -u $SSH_GIT_URL -n $configData.Item1 --scope cluster --operator-namespace $configData.Item1 --ssh-private-key-file $configData.Item2
            $? | Should -BeTrue
        }
    
        # Loop and retry until the configuration installs and helm pod comes up
        $n = 0
        do 
        {
            $readyConfigs = 0
            foreach($configData in $CONFIG_ARR) {
                # TODO: Change this to checking the success message after we merge in the bugfix into the agent
                if (Get-PodStatus $configData.Item1 -Namespace $configData.Item1 -eq $POD_RUNNING) {
                    $readyConfigs += 1
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le 30 -And $readyConfigs -ne 4)
        $n | Should -BeLessOrEqual 30
    }

    It 'Fails when trying to create a configuration with ssh url and https auth values' {
        az k8s-configuration create -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -u $HTTP_GIT_URL -n "config-should-fail" --scope cluster --operator-namespace "config-should-fail" --ssh-private-key-file $RSA_KEYPATH
        $? | Should -BeFalse
    }

    It "Lists the configurations on the cluster" {
        $output = az k8s-configuration list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $? | Should -BeTrue

        foreach ($configData in $CONFIG_ARR) {
            $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configData.Item1 }
            $configExists | Should -Not -BeNullOrEmpty
        }
    }

    It "Deletes the configuration from the cluster" {
        foreach ($configData in $CONFIG_ARR) {
            az k8s-configuration delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configData.Item1
            $? | Should -BeTrue

            # Configuration should be removed from the resource model
            az k8s-configuration show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters -n $configData.Item1
            $? | Should -BeFalse
        }
    }

    It "Performs another list after the delete" {
        $output = az k8s-configuration list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type connectedClusters
        $? | Should -BeTrue

        foreach ($configData in $CONFIG_ARR) {
            $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configData.Item1 }
            $configExists | Should -BeNullOrEmpty
        }
    }
}