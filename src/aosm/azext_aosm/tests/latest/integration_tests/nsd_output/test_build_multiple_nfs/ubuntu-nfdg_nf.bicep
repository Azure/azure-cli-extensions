// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
//
// The template that the NSD invokes to create the Network Function from a published NFDV.

@description('Publisher where the NFD is published')
param publisherName string = 'reference-publisher'

@description('Resource group where the NFD publisher exists')
param publisherResourceGroup string = 'Reference-publisher'

@description('NFD Group name for the Network Function')
param networkFunctionDefinitionGroupName string = 'ubuntu-nfdg'

@description('NFD version')
param ubuntu_nfdg_nfd_version string

@description('The managed identity that should be used to create the NF.')
param managedIdentity string

param location string = 'eastus'

param nfviType string = 'AzureCore'

param resourceGroupId string = resourceGroup().id

@secure()
param deploymentParametersObject object

var deploymentParameters = deploymentParametersObject.deploymentParameters

var identityObject = (managedIdentity == '')  ? {
  type: 'SystemAssigned'
} : {
  type: 'UserAssigned'
  userAssignedIdentities: {
    '${managedIdentity}': {}
  }
}

resource publisher 'Microsoft.HybridNetwork/publishers@2023-09-01' existing = {
  name: publisherName
  scope: resourceGroup(publisherResourceGroup)
}

resource nfdg 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups@2023-09-01' existing = {
  parent: publisher
  name: networkFunctionDefinitionGroupName
}

resource nfdv 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups/networkfunctiondefinitionversions@2023-09-01' existing = {
  parent: nfdg
  name: ubuntu_nfdg_nfd_version

}

resource nf_resource 'Microsoft.HybridNetwork/networkFunctions@2023-09-01' = [for (values, i) in deploymentParameters: {
  name: 'ubuntu-nfdg${i}'
  location: location
  identity: identityObject
  properties: {
    networkFunctionDefinitionVersionResourceReference: {
      id: nfdv.id
      idType: 'Open'
    }
    nfviType: nfviType
    nfviId: resourceGroupId
    allowSoftwareUpdate: true
    configurationType: 'Secret'
    secretDeploymentValues: string(values)
  }
}]