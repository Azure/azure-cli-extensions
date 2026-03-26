// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
//
// The template that the NSD invokes to create the Network Function from a published NFDV.

@description('Publisher where the NFD is published')
param publisherName string = 'reference-publisher'

@description('Resource group where the NFD publisher exists')
param publisherResourceGroup string = 'Reference-publisher'

@description('NFD Group name for the Network Function')
param networkFunctionDefinitionGroupName string = 'nginx-nfdg'

@description('NFD version')
param nginx_nfdg_nfd_version string

@description('The managed identity that should be used to create the NF.')
param managedIdentity string
@description('The custom location of the ARC-enabled AKS cluster to create the NF.')
param customLocationId string

param location string = 'eastus'

param nfviType string = 'AzureArcKubernetes'

param resourceGroupId string = resourceGroup().id

@secure()
param deployParametersObject object

var deployParameters = deployParametersObject.deployParameters

var identityObject = (managedIdentity == '')  ? {
  type: 'SystemAssigned'
} : {
  type: 'UserAssigned'
  userAssignedIdentities: {
    '${managedIdentity}': {}
  }
}

resource publisher 'Microsoft.HybridNetwork/publishers@2024-04-15' existing = {
  name: publisherName
  scope: resourceGroup(publisherResourceGroup)
}

resource nfdg 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups@2024-04-15' existing = {
  parent: publisher
  name: networkFunctionDefinitionGroupName
}

resource nfdv 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups/networkfunctiondefinitionversions@2024-04-15' existing = {
  parent: nfdg
  name: nginx_nfdg_nfd_version

}

resource nf_resource 'Microsoft.HybridNetwork/networkFunctions@2024-04-15' = [for (values, i) in deployParameters: {
  name: 'nginx-nfdg${i}'
  location: location
  identity: identityObject
  properties: {
    networkFunctionDefinitionVersionResourceReference: {
      id: nfdv.id
      idType: 'Open'
    }
    nfviType: nfviType
    nfviId: customLocationId
    allowSoftwareUpdate: true
    configurationType: 'Secret'
    secretDeploymentValues: string(values)
  }
}]
