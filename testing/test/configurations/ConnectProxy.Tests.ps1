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

        # Wait for a certain amount of time (e.g., 30 seconds)
        Start-Sleep -Seconds 60

        # Display the output
        Write-Host "Proxy Job State: $($proxyJob.State)"

        # Check if the job ran successfully
        $proxyJob.State | Should -Be 'Running'
        
        # Check if the kubeconfig file has been updated to use the proxy
        $kubeconfigPath = "~/.kube/config"
        $kubeconfig = Get-Content $kubeconfigPath -Raw | ConvertFrom-Yaml
        # Extract the current context
        $currentContext = $kubeconfig.'current-context'

        # Validate that the current context is for the arc machine
        $currentContext | Should -Be $ENVCONFIG.arcClusterName

        # Find the cluster associated with the current context
        $context = $kubeconfig.contexts | Where-Object { $_.name -eq $currentContext }
        $clusterName = $context.context.cluster

        # Retrieve the server URL for the cluster
        $cluster = $kubeconfig.clusters | Where-Object { $_.name -eq $clusterName }
        $server = $cluster.cluster.server

        # Validate the server URL
        $server | Should -Match "^https://127.0.0.1:47011/proxies/"
                
        # Check if the proxy command ran successfully
        $kubectlJob = Start-Job -ScriptBlock {
            try {
                $output =  kubectl get pods -n azure-arc 2>&1
                return @{ Success = $LASTEXITCODE -eq 0; Output = $output }
            } catch {
                return @{ Success = $false; Output = $_.Exception.Message }
            }
        }

        $kubectlJob | Wait-Job
        $kubectlResult = Receive-Job -Job $kubectlJob

        # Assert that the result is 0
        $kubectlResult.Success | Should -BeTrue

        Stop-Job -Job $proxyJob
        Remove-Job -Job $proxyJob
    }

    It "Delete the connected instance" {
        az connectedk8s delete -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --force -y
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az connectedk8s show -n $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup
        $? | Should -BeFalse
    }
}