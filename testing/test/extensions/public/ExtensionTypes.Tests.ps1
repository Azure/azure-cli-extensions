Describe 'Extension Types Testing' {
    BeforeAll {
        $extensionType = "cassandradatacentersoperator"
        $location = "eastus2euap"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Performs a show-by-cluster extension types call' {
        $output = az $Env:K8sExtensionName extension-types show-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It 'Performs a show-by-location extension types call' {
        $output = az $Env:K8sExtensionName extension-types show-by-location --location $location --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a cluster-scoped list extension types call" {
        $output = az $Env:K8sExtensionName extension-types list-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a location-scoped list extension types call" {
        $output = az $Env:K8sExtensionName extension-types list-by-location --location $location
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a location-scoped show extension type version call" {
        $output = az $Env:K8sExtensionName extension-types show-version-by-cluster -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType --version 1.0.0
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a cluster-scoped show extension type version call" {
        $output = az $Env:K8sExtensionName extension-types list-versions-by-cluster --location $location --extension-type $extensionType --version 1.0.0
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a cluster-scoped list extension type versions call" {
        $output = az $Env:K8sExtensionName extension-types list-versions-by-cluster --location $location --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a location-scoped list extension type versions call" {
        $output = az $Env:K8sExtensionName extension-types list-versions-by-location --location $location --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }
}
