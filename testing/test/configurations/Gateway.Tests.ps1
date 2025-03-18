Describe 'Onboarding with Gateway Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1

        $gatewayResourceId = "/subscriptions/15c06b1b-01d6-407b-bb21-740b8617dea3/resourceGroups/connectedk8sCLITestResources/providers/Microsoft.HybridCompute/gateways/gateway-test-cli"
    }

    It 'Check if onboarding works with gateway enabled' {
        az connectedk8s connect -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup -l $ARC_LOCATION --gateway-resource-id $gatewayResourceId --no-wait
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $gatewayStatus = $jsonOutput.RootElement.GetProperty("gateway").GetProperty("enabled").GetBoolean()
            $gatewayId = $jsonOutput.RootElement.GetProperty("gateway").GetProperty("resourceId").GetString() 
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Gateway Status: $gatewayStatus"
            Write-Host "Gateway Id: $gatewayId"
            if ($provisioningState -eq $SUCCEEDED -and $gatewayStatus -eq $true -and $gatewayId -eq $gatewayResourceId) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Disable the gateway' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --disable-gateway
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $gatewayStatus = $jsonOutput.RootElement.GetProperty("gateway").GetProperty("enabled").GetBoolean() 
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Gateway Status: $gatewayStatus"
            if ($provisioningState -eq $SUCCEEDED -and $gatewayStatus -eq $false) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Update the cluster to use gateway again using update cmd' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --gateway-resource-id $gatewayResourceId
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $gatewayStatus = $jsonOutput.RootElement.GetProperty("gateway").GetProperty("enabled").GetBoolean()
            $gatewayId = $jsonOutput.RootElement.GetProperty("gateway").GetProperty("resourceId").GetString() 
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Gateway Status: $gatewayStatus"
            Write-Host "Gateway Id: $gatewayId"
            if ($provisioningState -eq $SUCCEEDED -and $gatewayStatus -eq $true -and $gatewayId -eq $gatewayResourceId) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Disable the gateway' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --disable-gateway
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $gatewayStatus = $jsonOutput.RootElement.GetProperty("gateway").GetProperty("enabled").GetBoolean() 
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Gateway Status: $gatewayStatus"
            if ($provisioningState -eq $SUCCEEDED -and $gatewayStatus -eq $false) {
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