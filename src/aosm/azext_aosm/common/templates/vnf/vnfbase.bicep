// Copyright (c) Microsoft Corporation.

// This file creates the base AOSM resources for a VNF
param location string
@description('Name of a publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of a Storage Account-backed Artifact Store, deployed under the publisher.')
param saArtifactStoreName string
@description('Name of a Network Function Definition Group')
param nfDefinitionGroup string

// The publisher resource is the top level AOSM resource under which all other designer resources
// are created.
resource publisher 'Microsoft.HybridNetwork/publishers@2024-04-15' = {
  name: publisherName
  location: location
  properties: { scope: 'Private'}
}

// The artifact store is the resource in which all the artifacts (except VHD images) required to deploy the NF are stored.
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2024-04-15' = {
  parent: publisher
  name: acrArtifactStoreName
  location: location
  properties: {
    storeType: 'AzureContainerRegistry'
  }
}

// The storage account is the resource in which the VHD images are stored.
resource saArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2024-04-15' = {
  parent: publisher
  name: saArtifactStoreName
  location: location
  properties: {
    storeType: 'AzureStorageAccount'
  }
}

// The NFD Group is the parent resource under which all NFD versions will be created.
resource nfdg 'Microsoft.Hybridnetwork/publishers/networkfunctiondefinitiongroups@2024-04-15' = {
  parent: publisher
  name: nfDefinitionGroup
  location: location
}
