extension radius

// Sample covering: sidecar containers via runtimes.kubernetes.pod.containers

param environment string

resource app 'Applications.Core/applications@2023-10-01-preview' = {
  name: 'sidecarapp'
  properties: {
    environment: environment
  }
}

resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'main'
  properties: {
    application: app.id
    container: {
      image: 'nginx:1.25-alpine'
      ports: {
        http: {
          containerPort: 80
        }
      }
    }
    runtimes: {
      kubernetes: {
        pod: {
          containers: [
            {
              name: 'log-collector'
              image: 'fluent/fluent-bit:2.1'
              env: [
                {
                  name: 'FLUENT_OUTPUT'
                  value: 'stdout'
                }
              ]
            }
            {
              name: 'metrics-exporter'
              image: 'prom/node-exporter:v1.6.0'
            }
          ]
        }
      }
    }
  }
}
