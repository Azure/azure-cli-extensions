// Copyright (c) Microsoft Corporation.

// This file creates the base AOSM resources for an NSD
param location string
@description('Name of a publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of an Network Service Design Group')
param nsDesignGroup string

// The publisher resource is the top level AOSM resource under which all other designer resources
// are created.
resource publisher 'Microsoft.HybridNetwork/publishers@2023-09-01' = {
  name: publisherName
  location: location
  properties: { scope: 'Private'}
}

// The artifact store is the resource in which all the artifacts required to deploy the NF are stored.
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' = {
  parent: publisher
  name: acrArtifactStoreName
  location: location
  properties: {
    storeType: 'AzureContainerRegistry'
  }
}

// The NSD Group is the parent resource under which all NSD versions will be created.
resource nsdGroup 'Microsoft.Hybridnetwork/publishers/networkservicedesigngroups@2023-09-01' = {
  parent: publisher
  name: nsDesignGroup
  location: location
}
