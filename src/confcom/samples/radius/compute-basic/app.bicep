// Radius.Compute/containers: properties.containers.<name>.image → policy id, name, layers
extension radius
extension radiusResources

@description('The Radius Application ID. Injected automatically by the rad CLI.')
param application string
@description('The ID of your Radius Environment. Set automatically by the rad CLI.')
param environment string


resource myapplication 'Applications.Core/applications@2023-10-01-preview' = {
  name: 'radius-app-2'
  properties: {
    environment: environment
  }
}

resource demo 'Radius.Compute/containers@2025-08-01-preview' = {
  name: 'demo'
  properties: {
    environment: environment
    application: myapplication.id
    containers: {
      demo: {
        image: 'ghcr.io/radius-project/samples/demo:latest'
        ports: {
          web: {
            containerPort: 3000
          }
        }
      }
    }
  }
}
