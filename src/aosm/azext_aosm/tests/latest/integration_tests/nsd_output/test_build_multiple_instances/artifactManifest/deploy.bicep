// Copyright (c) Microsoft Corporation.

// This file creates an Artifact Manifest for a NSD
param location string
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of the Artifact Manifest to create')
param acrManifestName string

// The publisher resource is the top level AOSM resource under which all other designer resources
// are created.
// If using publish command, this is created from deploying the nsdbase.bicep
resource publisher 'Microsoft.HybridNetwork/publishers@2024-04-15' existing =  {
  name: publisherName
}

// The artifact store is the resource in which all the artifacts required to deploy the NF are stored.
// If using publish command, this is created from deploying the nsdbase.bicep
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2024-04-15' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

// Artifact manifest from ARMTemplate and NF RET artifacts
resource acrArtifactManifest 'Microsoft.Hybridnetwork/publishers/artifactStores/artifactManifests@2024-04-15' = {
  parent: acrArtifactStore
  name: acrManifestName
  location: location
  properties: {
    artifacts: [
      {
        artifactName: 'ubuntu-vm'
        artifactType: 'OCIArtifact'
        artifactVersion: '1.0.0'
      }
    ]
  }
}