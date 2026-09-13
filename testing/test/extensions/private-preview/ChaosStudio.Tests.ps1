Describe 'Chaos Studio Testing' {
    BeforeAll {
        $extensionType = "Microsoft.ChaosStudio"
        $extensionName = "chaos-studio-cli-test"

        . $PSScriptRoot\..\..\helper\Constants.ps1
        . $PSScriptRoot\..\..\helper\Helper.ps1

        foreach ($key in @("chaosWorkspaceId", "chaosExtensionVersion", "chaosStressToolsImage")) {
            if (-not $ENVCONFIG.$key) {
                throw "Set '$key' in testing/settings.json before running Chaos Studio integration tests."
            }
        }
        $clusterArgs = @("-c", $ENVCONFIG.aksClusterName, "-g", $ENVCONFIG.resourceGroup,
            "--cluster-type", "managedClusters")
        $settings = @("chaos-workspace-id=$($ENVCONFIG.chaosWorkspaceId)",
            "experiments.stressToolsImage=$($ENVCONFIG.chaosStressToolsImage)")
        if ($ENVCONFIG.chaosExistingRoleDefinitionId) {
            $settings += "chaos-existing-role-definition-id=$($ENVCONFIG.chaosExistingRoleDefinitionId)"
        }
    }

    It 'Creates, shows, lists, updates and deletes the managed workspace extension' {
        $output = az $Env:K8sExtensionName list @clusterArgs -o json
        $LASTEXITCODE | Should -Be 0
        $existing = @($output | ConvertFrom-Json | Where-Object { $_.extensionType -eq $extensionType })
        $existing.Count | Should -Be 0 -Because "this test requires a dedicated cluster without Chaos Studio"

        try {
            $output = az $Env:K8sExtensionName create @clusterArgs -n $extensionName --extension-type $extensionType --release-train dev --version $ENVCONFIG.chaosExtensionVersion --configuration-settings @settings -o json
            $LASTEXITCODE | Should -Be 0
            $created = $output | ConvertFrom-Json
            $created.provisioningState | Should -Be "Succeeded"
            $created.autoUpgradeMinorVersion | Should -BeFalse
            $created.configurationSettings.'subscriber.workspaceId' | Should -Be $ENVCONFIG.chaosWorkspaceId
            $created.configurationSettings.'subscriber.serverEndpoint' | Should -Not -BeNullOrEmpty

            $output = az $Env:K8sExtensionName show @clusterArgs -n $extensionName -o json
            $LASTEXITCODE | Should -Be 0
            ($output | ConvertFrom-Json).extensionType | Should -Be $extensionType

            $output = az $Env:K8sExtensionName list @clusterArgs -o json
            $LASTEXITCODE | Should -Be 0
            @($output | ConvertFrom-Json | Where-Object { $_.name -eq $extensionName }).Count | Should -Be 1

            $output = az $Env:K8sExtensionName update @clusterArgs -n $extensionName --version $ENVCONFIG.chaosExtensionVersion --yes -o json
            $LASTEXITCODE | Should -Be 0
            $updated = $output | ConvertFrom-Json
            $updated.provisioningState | Should -Be "Succeeded"
            $updated.configurationSettings.'workloadIdentity.clientId' | Should -Be $created.configurationSettings.'workloadIdentity.clientId'
            $updated.configurationSettings.'subscriber.serverEndpoint' | Should -Be $created.configurationSettings.'subscriber.serverEndpoint'
            $updated.configurationSettings.'experiments.stressToolsImage' | Should -Be $ENVCONFIG.chaosStressToolsImage
        }
        finally {
            az $Env:K8sExtensionName delete @clusterArgs -n $extensionName --yes
            $LASTEXITCODE | Should -Be 0
        }

        $output = az $Env:K8sExtensionName list @clusterArgs -o json
        $LASTEXITCODE | Should -Be 0
        @($output | ConvertFrom-Json | Where-Object { $_.name -eq $extensionName }).Count | Should -Be 0
    }
}
