# Azure CLI GalleryServiceArtifact Extension #
This is an extension to Azure CLI to manage Gallery Service Artifact resources.

## How to use ##
Remove existing extension (if previously installed) 

    ```az extension remove --name gallery-service-artifact```

Add Gallery Service Artifact extension using the wheel file

    ```az extension add --name gallery-service-artifact```

## Sample Commands
### List Service Artifacts
Lists all Service Artifacts under a Gallery.

```az gallery service-artifact list --gallery-name <gallery-name> --resource-group <resource-group-name> --subscription <subscription-id>```      
 
### Create Service Artifacts
Creates a new Service Artifact

```az gallery service-artifact create --gallery-name <gallery-name> --resource-group <resource-group-name> --subscription <subscription-id> --service-artifact-name <service-artifact-name> --location <location>  --target-locations '@<path-to-target-location-json-file>' --vm-artifacts-profiles '@<path-to-vm-artifact-json-file>' --description "<service-artifact-description>"```
 
### Get Service Artifact
Retrieves an existing Service Artifact

```az gallery service-artifact get --gallery-name <gallery-name> --resource-group <resource-group-name> --subscription <subscription-id> --service-artifact-name <service-artifact-name>```
 
### Update Service Artifact
Updates an existing Service Artifact.

```az gallery service-artifact update --gallery-name <gallery-name> --resource-group <resource-group-name> --subscription <subscription-id> --service-artifact-name <service-artifact-name> --location <location> --target-locations '@<path-to-target-location-json-file>' --vm-artifacts-profiles '@<path-to-vm-artifact-json-file>' --description "<service-artifact-description>"```
