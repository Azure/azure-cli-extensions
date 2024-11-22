Describe 'Onboarding with Workload Identity Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1
    }

    It 'Check if onboarding works with oidc and workload identity enabled' {
        az connectedk8s connect -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup -l $ARC_LOCATION --enable-oidc-issuer --enable-workload-identity --no-wait
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $securityProfile = $jsonOutput.RootElement.GetProperty("securityProfile").GetProperty("workloadIdentity").GetProperty("enabled").GetBoolean()
            $oidcIssuerProfile = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("enabled").GetBoolean()
            $issuerUrl = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("issuerUrl").GetString()
            $selfHostedIssuerUrl = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("selfHostedIssuerUrl").GetString() 
            $agentState = $jsonOutput.RootElement.GetProperty("arcAgentProfile").GetProperty("agentState").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Security Profile Status: $securityProfile"
            Write-Host "OIDC Issuer Profile Status: $oidcIssuerProfile"
            Write-Host "Issuer Url: $issuerUrl"
            Write-Host "Self Hosted Issuer Url: $selfHostedIssuerUrl"
            Write-Host "Agent State: $agentState"
            if (
                $provisioningState -eq $SUCCEEDED -and 
                $securityProfile -eq $true -and 
                $oidcIssuerProfile -eq $true -and 
                ![string]::IsNullOrEmpty($issuerUrl) -and 
                $issuerUrl -like "*unitedkingdom*" -and 
                [string]::IsNullOrEmpty($selfHostedIssuerUrl) -and
                $agentState -eq $SUCCEEDED
            ) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Disable workload identity' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --disable-workload-identity
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $securityProfile = $jsonOutput.RootElement.GetProperty("securityProfile").GetProperty("workloadIdentity").GetProperty("enabled").GetBoolean()
            $agentState = $jsonOutput.RootElement.GetProperty("arcAgentProfile").GetProperty("agentState").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Security Profile Status: $securityProfile"
            Write-Host "Agent State: $agentState"
            if ($provisioningState -eq $SUCCEEDED -and $securityProfile -eq $false -and $agentState -eq $SUCCEEDED) {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Update the cluster to use workload identity again using update cmd' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --enable-workload-identity
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $securityProfile = $jsonOutput.RootElement.GetProperty("securityProfile").GetProperty("workloadIdentity").GetProperty("enabled").GetBoolean()
            $agentState = $jsonOutput.RootElement.GetProperty("arcAgentProfile").GetProperty("agentState").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Security Profile Status: $securityProfile"
            Write-Host "Agent State: $agentState"
            if (
                $provisioningState -eq $SUCCEEDED -and 
                $securityProfile -eq $true -and
                $agentState -eq $SUCCEEDED
            ) {
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
        Start-Sleep -Seconds 10
    }
}

Describe 'Updating with Workload Identity Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1
    }

    It 'Onboard a cluster to arc' {
        az connectedk8s connect -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup -l $ARC_LOCATION --no-wait
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
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It 'Update the cluster with oidc and workload identity enabled' {
        az connectedk8s update -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --enable-oidc-issuer --enable-workload-identity
        $? | Should -BeTrue
        Start-Sleep -Seconds 10

        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $securityProfile = $jsonOutput.RootElement.GetProperty("securityProfile").GetProperty("workloadIdentity").GetProperty("enabled").GetBoolean()
            $oidcIssuerProfile = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("enabled").GetBoolean()
            $issuerUrl = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("issuerUrl").GetString()
            $selfHostedIssuerUrl = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("selfHostedIssuerUrl").GetString() 
            $agentState = $jsonOutput.RootElement.GetProperty("arcAgentProfile").GetProperty("agentState").GetString()
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "Security Profile Status: $securityProfile"
            Write-Host "OIDC Issuer Profile Status: $oidcIssuerProfile"
            Write-Host "Issuer Url: $issuerUrl"
            Write-Host "Self Hosted Issuer Url: $selfHostedIssuerUrl"
            Write-Host "Agent State: $agentState"
            if (
                $provisioningState -eq $SUCCEEDED -and 
                $securityProfile -eq $true -and 
                $oidcIssuerProfile -eq $true -and 
                ![string]::IsNullOrEmpty($issuerUrl) -and 
                $issuerUrl -like "*unitedkingdom*" -and 
                [string]::IsNullOrEmpty($selfHostedIssuerUrl) -and
                $agentState -eq $SUCCEEDED
            ) {
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
        Start-Sleep -Seconds 10
    }
}

Describe 'Creating with Workload Identity Scenario and Self Hosted Issuer' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1

        $SelfHostedIssuer = "https://eastus.oic.prod-aks.azure.com/fc50e82b-3761-4218-8691-d98bcgb146da/e6c4bf03-84d9-480c-a269-37a41c28c5cb/"
    }

    It 'Check if onboarding works with oidc enabled and self-hosted issuer url passed in' {
        az connectedk8s connect -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup -l $ARC_LOCATION --enable-oidc-issuer --self-hosted-issuer $SelfHostedIssuer --no-wait
        $? | Should -BeTrue
        Start-Sleep -Seconds 10
    
        # Loop and retry until the configuration installs
        $n = 0
        do 
        {
            $output = az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $oidcIssuerProfile = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("enabled").GetBoolean()
            $issuerUrl = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("issuerUrl").GetString() 
            $selfHostedIssuerUrl = $jsonOutput.RootElement.GetProperty("oidcIssuerProfile").GetProperty("selfHostedIssuerUrl").GetString() 
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "OIDC Issuer Profile Status: $oidcIssuerProfile"
            Write-Host "Issuer Url: $issuerUrl"
            Write-Host "Self Hosted Issuer Url: $selfHostedIssuerUrl"
            if (
                $provisioningState -eq $SUCCEEDED -and 
                $oidcIssuerProfile -eq $true -and 
                [string]::IsNullOrEmpty($issuerUrl) -and 
                ![string]::IsNullOrEmpty($selfHostedIssuerUrl) -and
                $selfHostedIssuerUrl -eq $SelfHostedIssuer
            ) {
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