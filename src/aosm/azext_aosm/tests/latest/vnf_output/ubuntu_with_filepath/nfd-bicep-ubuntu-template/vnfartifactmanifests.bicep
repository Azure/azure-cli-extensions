// Copyright (c) Microsoft Corporation.

// This file creates an NF definition for a VNF
param location string
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of an existing Storage Account-backed Artifact Store, deployed under the publisher.')
param saArtifactStoreName string
@description('Name of the manifest to deploy for the ACR-backed Artifact Store')
param acrManifestName string
@description('Name of the manifest to deploy for the Storage Account-backed Artifact Store')
param saManifestName string
@description('Name of Network Function. Used predominantly as a prefix for other variable names')
param nfName string
@description('The version that you want to name the NFM VHD artifact, in format A-B-C. e.g. 6-13-0')
param vhdVersion string
@description('The name under which to store the ARM template')
param armTemplateVersion string

// Created by the az aosm definition publish command before the template is deployed
resource publisher 'Microsoft.HybridNetwork/publishers@2023-09-01' existing = {
  name: publisherName
  scope: resourceGroup()
}

// Created by the az aosm definition publish command before the template is deployed
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

// Created by the az aosm definition publish command before the template is deployed
resource saArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-09-01' existing = {
  parent: publisher
  name: saArtifactStoreName
}

resource saArtifactManifest 'Microsoft.Hybridnetwork/publishers/artifactStores/artifactManifests@2023-09-01' = {
  parent: saArtifactStore
  name: saManifestName
  location: location
  properties: {
    artifacts: [
      {
        artifactName: '${nfName}-vhd'
        artifactType: 'VhdImageFile'
        artifactVersion: vhdVersion
      }
    ]
  }
}

resource acrArtifactManifest 'Microsoft.Hybridnetwork/publishers/artifactStores/artifactManifests@2023-09-01' = {
  parent: acrArtifactStore
  name: acrManifestName
  location: location
  properties: {
    artifacts: [
      {
        artifactName: '${nfName}-arm-template'
        artifactType: 'ArmTemplate'
        artifactVersion: armTemplateVersion
      }
    ]
  }
}
