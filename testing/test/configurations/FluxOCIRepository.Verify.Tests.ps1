Describe 'Flux Configuration (OCI Repository - Verification) Testing' {
    BeforeAll {
        . $PSScriptRoot/Constants.ps1
        . $PSScriptRoot/Helper.ps1

        $url = "oci://ghcr.io/stefanprodan/manifests/podinfo"
        $configurationName = "oci-verification-config"
        $tag = "latest"
        $provider = "cosign"
        $issuer = "https://token.actions.githubusercontent.com$"
        $subject = "https://github.com/stefanprodan/podinfo.*$"
        $verificationConfigKey = "verifyKeys"
        $verificationConfigValue = "Y2xpZW50Q2VydGlmaWNhdGU="
    }

    It 'Creates a configuration with OCI verification enabled on the cluster' {
        $oidcIdentityJsonSafe = '{"issuer":"' + $issuer + '","subject":"' + $subject + '"}'
        Write-Host "Safe OIDC Identity JSON: $oidcIdentityJsonSafe"

        # Create configuration with verification settings
        $output = az k8s-configuration flux create `
            -c $ENVCONFIG.arcClusterName `
            -g $ENVCONFIG.resourceGroup `
            --cluster-type "connectedClusters" `
            -n $configurationName `
            --namespace $configurationName `
            --scope cluster `
            --kind oci `
            -u $url `
            --tag $tag `
            --verification-provider $provider `
            --match-oidc-identity $oidcIdentityJsonSafe `
            --verification-config "$verificationConfigKey=$verificationConfigValue" `
            --kustomization name=verificationtest path=./ prune=true `
            --no-wait

        $? | Should -BeTrue

        $n = 0
        do 
        {
            Start-Sleep -Seconds 10
            $output = az k8s-configuration flux show `
                -c $ENVCONFIG.arcClusterName `
                -g $ENVCONFIG.resourceGroup `
                --cluster-type "connectedClusters" `
                -n $configurationName 2>$null
            if ($?) {
                $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
                $provisioningState = ($output | ConvertFrom-Json).provisioningState
                $urlReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("url").GetString()
                $tagReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("repositoryRef").GetProperty("tag").GetString()
                
                $verifyElement = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("verify")
                $providerReturned = $verifyElement.GetProperty("provider").GetString()
                $matchOidcIdentity = $verifyElement.GetProperty("matchOidcIdentity")[0]
                $issuerReturned = $matchOidcIdentity.GetProperty("issuer").GetString()
                $subjectReturned = $matchOidcIdentity.GetProperty("subject").GetString()
                $verificationConfigReturned = $verifyElement.GetProperty("verificationConfig").GetProperty($verificationConfigKey).GetString()
                
                Write-Host "[POLL $n] State: $provisioningState | URL: $urlReturned | Tag: $tagReturned"
                Write-Host "         Provider: $providerReturned | Issuer: $issuerReturned"
                Write-Host "         Subject: $subjectReturned | VerifyKey: $verificationConfigReturned"
                
                if ($provisioningState -eq $SUCCEEDED) {
                    if (!$firstSucceededTime) {
                        $firstSucceededTime = Get-Date
                        Write-Host "[MILESTONE] First Succeeded at: $firstSucceededTime" -ForegroundColor Cyan
                    }
                    
                    if ($urlReturned -eq $url -and 
                        $tagReturned -eq $tag -and
                        $providerReturned -eq $provider -and
                        $issuerReturned -eq $issuer -and
                        $subjectReturned -eq $subject -and
                        $verificationConfigReturned -eq "<redacted>") {
                        Write-Host "[SUCCESS] All properties match!" -ForegroundColor Green
                        break
                    }
                }
            } else {
                Write-Host "[POLL $n] Show command failed, retrying..."
            }

            $n++
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Updates verification settings for the flux configuration on the cluster" {
        # Update with new verification settings
        $newTag = "1.2.0"
        $newUrl = "oci://ghcr.io/stefanprodan/manifests/podinfo2"
        $newProvider = "cosign"
        $newIssuer = "https://accounts.google.com"
        $newSubject = "https://github.com/example/repo/.github/workflows/build.yml@refs/heads/main"
        $newVerificationConfigKey = "verifyKeys"
        $newVerificationConfigValue = "Y2FDZXJ0aWZpY2F0ZU5ldw=="

        $newOidcIdentityJsonSafe = '{"issuer":"' + $newIssuer + '","subject":"' + $newSubject + '"}'
        Write-Host "Safe OIDC Identity JSON: $newOidcIdentityJsonSafe"

        $output = az k8s-configuration flux update `
            -c $ENVCONFIG.arcClusterName `
            -g $ENVCONFIG.resourceGroup `
            --cluster-type "connectedClusters" `
            -n $configurationName `
            --kind oci `
            -u $newUrl `
            --tag $newTag `
            --verification-provider $newProvider `
            --match-oidc-identity $newOidcIdentityJsonSafe `
            --verification-config "$newVerificationConfigKey=$newVerificationConfigValue" `
            --no-wait 2>&1

        Write-Host ""
        Write-Host "Update command output:" -ForegroundColor Cyan
        Write-Host $output

        $n = 0
        do 
        {
            Start-Sleep -Seconds 10
            $output = az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
            $jsonOutput = [System.Text.Json.JsonDocument]::Parse($output)
            $provisioningState = ($output | ConvertFrom-Json).provisioningState
            $urlReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("url").GetString()
            $tagReturned = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("repositoryRef").GetProperty("tag").GetString()
            
            # Check updated verification properties
            $verifyElement = $jsonOutput.RootElement.GetProperty("ociRepository").GetProperty("verify")
            $providerReturned = $verifyElement.GetProperty("provider").GetString()
            $matchOidcIdentity = $verifyElement.GetProperty("matchOidcIdentity")[0]
            $issuerReturned = $matchOidcIdentity.GetProperty("issuer").GetString()
            $subjectReturned = $matchOidcIdentity.GetProperty("subject").GetString()
            $verificationConfigReturned = $verifyElement.GetProperty("verificationConfig").GetProperty($newVerificationConfigKey).GetString()
            
            Write-Host "Provisioning State: $provisioningState"
            Write-Host "OCI Repository URL: $urlReturned"
            Write-Host "OCI Repository Tag: $tagReturned"
            Write-Host "Verification Provider: $providerReturned"
            Write-Host "OIDC Issuer: $issuerReturned"
            Write-Host "OIDC Subject: $subjectReturned"
            Write-Host "Verification Config Key: $verificationConfigReturned"
            
            if ($provisioningState -eq $SUCCEEDED -and 
                $urlReturned -eq $newUrl -and 
                $tagReturned -eq $newTag -and
                $providerReturned -eq $newProvider -and
                $issuerReturned -eq $newIssuer -and
                $subjectReturned -eq $newSubject -and
                $verificationConfigReturned -eq "<redacted>") {
                break
            }
            Start-Sleep -Seconds 10
            $n += 1
        } while ($n -le $MAX_RETRY_ATTEMPTS)
        $n | Should -BeLessOrEqual $MAX_RETRY_ATTEMPTS
    }

    It "Deletes the configuration from the cluster" {
        az k8s-configuration flux delete -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName --force
        $? | Should -BeTrue

        # Configuration should be removed from the resource model
        az k8s-configuration flux show -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters" -n $configurationName
        $? | Should -BeFalse
    }

    It "Performs another list after the delete" {
        $output = az k8s-configuration flux list -c $ENVCONFIG.arcClusterName -g $ENVCONFIG.resourceGroup --cluster-type "connectedClusters"
        $configExists = $output | ConvertFrom-Json | Where-Object { $_.id -Match $configurationName }
        $configExists | Should -BeNullOrEmpty
    }
}