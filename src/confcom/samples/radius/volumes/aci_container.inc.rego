{
  "id": "alpine:3.19",
  "name": "alpine:3.19",
  "layers": [
    "6f937bc4d3707c87d1207acd64290d97ec90c8b87a7785cb307808afa49ff892"
  ],
  "platform": "linux/amd64",
  "mounts": [
    {
      "destination": "/etc/resolv.conf",
      "source": "sandbox:///tmp/atlas/resolvconf/.+",
      "type": "bind",
      "options": [
        "rbind",
        "rshared",
        "rw"
      ]
    },
    {
      "destination": "/tmp/scratch",
      "options": [
        "rbind",
        "rshared",
        "rw"
      ],
      "source": "sandbox:///tmp/atlas/emptydir/.+",
      "type": "bind"
    },
    {
      "destination": "/data",
      "options": [
        "rbind",
        "rshared",
        "rw"
      ],
      "source": "sandbox:///tmp/atlas/azureFileVolume/.+",
      "type": "bind"
    },
    {
      "destination": "/config",
      "options": [
        "rbind",
        "rshared",
        "ro"
      ],
      "source": "sandbox:///tmp/atlas/(azureFileVolume|secretsVolume)/.+",
      "type": "bind"
    }
  ],
  "command": [
    "/bin/sh"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "TERM=xterm",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "(?i)(FABRIC)_.+=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "HOSTNAME=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "T(E)?MP=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "FabricPackageFileName=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "HostedServiceName=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "IDENTITY_API_VERSION=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "IDENTITY_HEADER=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
      "strategy": "re2",
      "required": false
    },
    {
      "pattern": "azurecontainerinstance_restarted_by=.+",
      "strategy": "re2",
      "required": false
    }
  ],
  "working_dir": "/"
}
