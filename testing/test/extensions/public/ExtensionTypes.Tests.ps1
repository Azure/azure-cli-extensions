Describe 'Extension Types Testing' {
    BeforeAll {
        $extensionType = "cassandradatacentersoperator"
        $location = "eastus2euap"
        
        . $PSScriptRoot/../../helper/Constants.ps1
        . $PSScriptRoot/../../helper/Helper.ps1
    }

    It 'Performs a show extension types call' {
        $output = az $Env:K8sExtensionName extension-types show -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a cluster-scoped list extension types call" {
        $output = az $Env:K8sExtensionName extension-types list -c $($ENVCONFIG.arcClusterName) -g $($ENVCONFIG.resourceGroup) --cluster-type connectedClusters
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a location-scoped list extension types call" {
        $output = az $Env:K8sExtensionName extension-types list-by-location --location $location
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }

    It "Performs a location-scoped list extension type versions call" {
        $output = az $Env:K8sExtensionName extension-types list-versions --location $location --extension-type $extensionType
        $? | Should -BeTrue
        $output | Should -Not -BeNullOrEmpty
    }
}
