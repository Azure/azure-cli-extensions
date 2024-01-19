// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
//
// The template that the NSD invokes to create the Network Function from a published NFDV.

@secure()
param configObject object

var resourceGroupId = resourceGroup().id

var identityObject = (configObject.managedIdentityId == '')  ? {
  type: 'SystemAssigned'
} : {
  type: 'UserAssigned'
  userAssignedIdentities: {
    '${configObject.managedIdentityId}': {}
  }
}

var nfdvSymbolicName = '${configObject.publisherName}/${configObject.nfdgName}/${configObject.nfdvName}'

resource nfdv 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups/networkfunctiondefinitionversions@2023-09-01' existing = {
  name: nfdvSymbolicName
  scope: resourceGroup(configObject.publisherResourceGroup)
}

resource nfResource 'Microsoft.HybridNetwork/networkFunctions@2023-09-01' = [for (values, i) in configObject.deploymentParameters: {
  name: '${configObject.nfdgName}${i}'
  location: configObject.location
  identity: identityObject
  properties: {
    networkFunctionDefinitionVersionResourceReference: {
      id: nfdv.id
      idType: 'Open'
    }
    nfviType: (configObject.customLocationId == '') ? 'AzureCore' : 'AzureArcKubernetes'
    nfviId: (configObject.customLocationId == '') ? resourceGroupId : configObject.customLocationId
    allowSoftwareUpdate: true
    configurationType: 'Secret'
    secretDeploymentValues: string(values)
  }
}]
