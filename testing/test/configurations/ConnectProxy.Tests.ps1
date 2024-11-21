Describe 'Connectedk8s Proxy Scenario' {
    BeforeAll {
        . $PSScriptRoot/../helper/Constants.ps1
    }

    It 'Check if basic onboarding works correctly' {
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

    It 'Connectedk8s proxy test with non-empty kubeconfig' {
        # Start the proxy command as a background job
        $proxyJob = Start-Job -ScriptBlock {
            param($ClusterName, $ResourceGroup)

            # Capture output and errors
            try {
                $output = az connectedk8s proxy -n $ClusterName -g $ResourceGroup 2>&1
                return @{ Success = $LASTEXITCODE -eq 0; Output = $output }
            } catch {
                return @{ Success = $false; Output = $_.Exception.Message }
            }
        } -ArgumentList $ENVCONFIG.arcClusterName, $ENVCONFIG.resourceGroup

        # Wait for a certain amount of time (e.g., 20 seconds)
        Start-Sleep -Seconds 20

        # Retrieve the job output
        $result = Receive-Job -Job $proxyJob
        Stop-Job -Job $proxyJob
        Remove-Job -Job $proxyJob

        # Display the output
        Write-Host "Proxy Command Output:"
        Write-Host $result.Output

        # Check if the command ran successfully
        $result.Success | Should -Be $true
    }

    It "Delete the connected instance" {
        az connectedk8s delete -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --force -y
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
        $? | Should -BeFalse
    }
}