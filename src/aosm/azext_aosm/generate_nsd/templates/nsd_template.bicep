// Copyright (c) Microsoft Corporation. All rights reserved.
// Highly Confidential Material
//
// Bicep template to create an Artifact Manifest, Config Group Schema and NSDV.
//
// Requires an existing NFDV from which the values will be populated.

param location string
@description('Name of an existing publisher, expected to be in the resource group where you deploy the template')
param publisherName string
@description('Name of an existing ACR-backed Artifact Store, deployed under the publisher.')
param acrArtifactStoreName string
@description('Name of an existing Network Service Design Group')
param nsDesignGroup string
@description('The version of the NSDV you want to create, in format A-B-C')
param nsDesignVersion string
@description('Name of the nfvi site')
param nfviSiteName string = '{{nfvi_site_name}}'
@description('The version that you want to name the NF template artifact, in format A-B-C. e.g. 6-13-0. Suggestion that this matches as best possible the SIMPL released version. If testing for development, you can use any numbers you like.')
param armTemplateVersion string = '{{armTemplateVersion}}'
@description('Name of the NF template artifact')
var armTemplateName = '{{armTemplateName}}'

// The publisher resource is the top level AOSM resource under which all other designer resources
// are created. 
resource publisher 'Microsoft.HybridNetwork/publishers@2023-04-01-preview' existing = {
  name: publisherName
  scope: resourceGroup()
}

// The artifact store is the resource in which all the artifacts required to deploy the NF are stored. 
// You can either create one especially for SIMPL or share a manifest with other NSDs. In this example
// the artifact store is expected to be shared and should be created upfront.
resource acrArtifactStore 'Microsoft.HybridNetwork/publishers/artifactStores@2023-04-01-preview' existing = {
  parent: publisher
  name: acrArtifactStoreName
}

// Created up-front, the NSD Group is the parent resource under which all NSD versions will be created.
resource nsdGroup 'Microsoft.Hybridnetwork/publishers/networkservicedesigngroups@2023-04-01-preview' existing = {
  parent: publisher
  name: nsDesignGroup
}

// The configuration group schema defines the configuration required to deploy the NSD. The NSD references this object in the
// `configurationgroupsSchemaReferences` and references the values in the schema in the `parameterValues`.
// The operator will create a config group values object that will satisfy this schema.
resource cgSchema 'Microsoft.Hybridnetwork/publishers/configurationGroupSchemas@2023-04-01-preview' = {
  parent: publisher
  name: '{{cg_schema_name}}'
  location: location
  properties: {
    schemaDefinition: string(loadJsonContent('schemas/{{cg_schema_name}}.json'))
  }
}

// The NSD version
resource nsdVersion 'Microsoft.Hybridnetwork/publishers/networkservicedesigngroups/networkservicedesignversions@2023-04-01-preview' = {
  parent: nsdGroup
  name: nsDesignVersion
  location: location
  properties: {
    description: '{{nsdv_description}}'
    // The version state can be Preview, Active or Deprecated.
    // Once in an Active state, the NSDV becomes immutable.
    versionState: 'Preview'
    // The `configurationgroupsSchemaReferences` field contains references to the schemas required to
    // be filled out to configure this NSD.
    configurationGroupSchemaReferences: {
      {{cg_schema_name}}: {
        id: cgSchema.id
      }
    }
    // This details the NFVIs that should be available in the Site object created by the operator.
    nfvisFromSite: {
      nfvi1: {
        name: nfviSiteName
        type: 'AzureCore'
      }
    }
    // This field lists the templates that will be deployed by AOSM and the config mappings
    // to the values in the CG schemas.
    resourceElementTemplates: [
      {
        name: '{{ResourceElementName}}'
        // The type of resource element can be ArmResourceDefinition, ConfigurationDefinition or NetworkFunctionDefinition.
        type: 'NetworkFunctionDefinition'
        // The configuration object may be different for different types of resource element.
        configuration: {
          // This field points AOSM at the artifact in the artifact store.
          artifactProfile: {
            artifactStoreReference: {
              id: acrArtifactStore.id
            }
            artifactName:  armTemplateName
            artifactVersion: armTemplateVersion
          }
          templateType: 'ArmTemplate'
          // The parameter values map values from the CG schema, to values required by the template
          // deployed by this resource element.
          // outputParameters from the disk RET are used in these parameterValues
          // This NSD does not support the NF-Agent as it has no Configuration Resource Elements.
          // If Configuration resource elements (SDFs, Perimeta config) are added, the simplNfConfigMapping
          // must be edited to have these lines (instead of blank values. SNSSelf is null if there are no Configuration elements)
          // "nfAgentServiceBusNamespace": "{configurationparameters('SNSSelf').nfAgentConfiguration.resourceNamespace}",
          // "nfAgentUserAssignedIdentityResourceId": "{configurationparameters('SNSSelf').nfAgentConfiguration.userAssignedIdentityResourceId}",
          parameterValues: string(loadJsonContent('configMappings/configMappings.json'))
        }
        dependsOnProfile: {
          installDependsOn: []
          uninstallDependsOn: []
          updateDependsOn: []
        }
      }      
    ]
  }
}
