Describe 'Proxy Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1
    }

    It 'Check if basic onboarding works correctly with proxy enabled' {
        az connectedk8s connect -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup -l $ARC_LOCATION --proxy-skip-range logcollector --no-wait
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            Write-Host "Provisioning State: $provisioningState"
            if ($provisioningState -eq $SUCCEEDED) {
                $isProxyEnabled = helm get values -n azure-arc-release azure-arc -o yaml | grep isProxyEnabled
                Write-Host "$isProxyEnabled"
                if ($isProxyEnabled -match "isProxyEnabled: true") {
                    break
                }
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Disable proxy' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --disable-proxy
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            Write-Host "Provisioning State: $provisioningState"
            if ($provisioningState -eq $SUCCEEDED) {
                $isProxyEnabled = helm get values -n azure-arc-release azure-arc -o yaml | grep isProxyEnabled
                Write-Host "$isProxyEnabled"
                if ($isProxyEnabled -match "isProxyEnabled: false") {
                    break
                }
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Delete the connected instance" {
        az connectedk8s delete -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --force -y
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
        $? | Should -BeFalse
    }
}