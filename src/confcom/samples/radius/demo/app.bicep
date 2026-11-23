extension radius

param application string
param environment string

param image string = 'ghcr.io/radius-project/samples/demo:latest'

resource demo 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'demo'
  properties: {
    application: application
    container: {
      image: image
      ports: {
        web: {
          containerPort: 3000
        }
      }
      livenessProbe: {
        kind: 'httpGet'
        containerPort: 3000
        path: '/healthz'
        initialDelaySeconds: 10
      }
    }
    connections: {
      redis: {
        source: db.id
      }
    }
  }
}

resource db 'Applications.Datastores/redisCaches@2023-10-01-preview' = {
  name: 'db'
  properties: {
    application: application
    environment: environment
  }
}
