// Copyright (c) Microsoft Corporation.

// This file creates an Artifact Manifest for a NSD
param location string
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of the manifest to deploy for the ACR-backed Artifact Store')
param acrManifestNames array
@description('The name under which to store the ARM template')
param armTemplateNames array
@description('The version that you want to name the NFM template artifact, in format A.B.C. e.g. 6.13.0. If testing for development, you can use any numbers you like.')
param armTemplateVersion string

resource publisher 'Microsoft.HybridNetwork/publishers@2023-09-01' existing = {
  name: publisherName
  scope: resourceGroup()
}

resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

resource acrArtifactManifests 'Microsoft.Hybridnetwork/publishers/artifactStores/artifactManifests@2023-09-01' = [for (values, i) in armTemplateNames: {
  parent: acrArtifactStore
  name: acrManifestNames[i]
  location: location
  properties: {
    artifacts: [
      {
        artifactName: armTemplateNames[i]
        artifactType: 'ArmTemplate'
        artifactVersion: armTemplateVersion
      }
    ]
  }
}]
