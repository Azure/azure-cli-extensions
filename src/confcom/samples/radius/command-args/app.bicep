extension radius

// Feature: command + args override
// Template fields: container.command, container.args
// Policy field:    command

param application string

resource container 'Applications.Core/containers@2023-10-01-preview' = {
  name: 'command-args'
  properties: {
    application: application
    container: {
      image: 'alpine:3.19'
      command: ['/bin/sh']
      args: ['-c', 'echo hello && sleep infinity']
    }
  }
}
