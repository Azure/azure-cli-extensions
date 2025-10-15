Describe 'ConnectedK8s Enable Disable Features Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1

        function Invoke-AzCommand {
            param (
                [string]$Command
            )
            Write-Host "Executing: $Command" -ForegroundColor Yellow
            $result = Invoke-Expression $Command
            return $result
        }

        function Wait-ForProvisioning {
            param (
                [string]$expectedProvisioningState,
                [string]$expectedAutoUpdate
            )
            $n = 0
            do {
                $output = Invoke-AzCommand "az connectedk8s show -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup)"
                $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
                $provisioningState = ($output | ConvertFrom-Json).provisioningState
                $autoUpdate = $jsonOutput.RootElement.GetProperty("arcAgentProfile").GetProperty("agentAutoUpgrade").GetString()
                Write-Host "Provisioning State: $provisioningState"
                Write-Host "Auto Update: $autoUpdate"
                if ($provisioningState -eq $expectedProvisioningState -and $autoUpdate -eq $expectedAutoUpdate) {
                    break
                }
                Start-Sleep -Seconds 10
                $n += 1
            } while ($n -le $MAX_RETRY_ATTEMPTS)
            $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
        }
    }

    It 'Onboard Connected cluster with no features enabled' {
        Invoke-AzCommand "az connectedk8s connect -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) -l $ARC_LOCATION --no-wait"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Enable azure-rbac feature' {
        Invoke-AzCommand "az connectedk8s enable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features azure-rbac"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Disable azure-rbac feature' {
        Invoke-AzCommand "az connectedk8s disable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features azure-rbac --yes"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Enable cluster-connect feature' {
        Invoke-AzCommand "az connectedk8s enable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features cluster-connect"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Disable cluster-connect feature' {
        Invoke-AzCommand "az connectedk8s disable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features cluster-connect --yes"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Enable custom-locations feature' {
        Invoke-AzCommand "az connectedk8s enable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features custom-locations --custom-locations-oid $($ENVCONFIG.customLocationsOid)"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Disable custom-locations feature' {
        Invoke-AzCommand "az connectedk8s disable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features custom-locations --yes"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Enable all features (cluster-connect, custom-locations, azure-rbac) together' {
        Invoke-AzCommand "az connectedk8s enable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features cluster-connect custom-locations azure-rbac --custom-locations-oid $($ENVCONFIG.customLocationsOid)"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It 'Disable all features (cluster-connect, custom-locations, azure-rbac) together' {
        Invoke-AzCommand "az connectedk8s disable-features -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --features cluster-connect custom-locations azure-rbac --yes"
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
        Wait-ForProvisioning -expectedProvisioningState $SUCCEEDED -expectedAutoUpdate "Enabled"
    }

    It "Delete the connected instance" {
        Invoke-AzCommand "az connectedk8s delete -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) -y"
        $? | Should -BeTrue

        # Wait for deletion to propagate through the resource model
        Start-Sleep -Seconds 30

        # Configuration should be removed from the resource model - expect ResourceNotFound error
        $output = Invoke-AzCommand "az connectedk8s show -n $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup)" 2>&1
        $output | Should -Match "(ResourceNotFound|could not be found|not found)"
    }
}