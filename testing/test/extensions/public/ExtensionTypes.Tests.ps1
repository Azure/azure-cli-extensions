Describe 'Extension Types Testing' {
    BeforeAll {
        $extensionType = "microsoft.contoso.samples"
        $location = "eastus2euap"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Performs a show-by-cluster extension types call' {
        Start-Sleep -Seconds 240
        $output = az $Env:K8sExtensionName extension-types show-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It 'Performs a show-by-location extension types call' {
        $output = az $Env:K8sExtensionName extension-types show-by-location --location $location --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a list-by-cluster extension types call" {
        $output = az $Env:K8sExtensionName extension-types list-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a list-by-location extension types call" {
        $output = az $Env:K8sExtensionName extension-types list-by-location --location $location
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a show-version-by-cluster  extension type version call" {
        $output = az $Env:K8sExtensionName extension-types show-version-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType --version 1.1.0
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a show-version-by-location extension type version call" {
        $output = az $Env:K8sExtensionName extension-types show-version-by-location --location $location --extension-type $extensionType --version 1.1.0
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a list-versions-by-cluster extension type versions call" {
        $output = az $Env:K8sExtensionName extension-types list-versions-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a list-versions-by-location extension type versions call" {
        $output = az $Env:K8sExtensionName extension-types list-versions-by-location --location $location --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }
}
