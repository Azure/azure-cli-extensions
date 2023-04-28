// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
// Bicep template to create a Publisher
param location string = resourceGroup().location
@description('Name you want to give the new Publisher object')
param publisherName string 

resource publisher 'Microsoft.HybridNetwork/publishers@2022-09-01-preview' = {
  name: publisherName
  scope: resourceGroup()
  location: location
  properties: {
    scope: 'Private'
  }
}
