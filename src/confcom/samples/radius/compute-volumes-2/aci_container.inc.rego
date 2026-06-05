{
  "id": "mcr.microsoft.com/azuredocs/aci-helloworld",
  "name": "mcr.microsoft.com/azuredocs/aci-helloworld",
  "layers": [
    "c870621d92a05fa5231b803218bc333b27a3fe5d4a194a50b8a93c91e8ae2526",
    "40966b81fe978b1337681321a0edcb96ef6fc4981b11f58f4352a8a3c07a750b",
    "e10bce5e2275167a28bd408f51acf19c13a922e9e20520dd80909436d330c51d",
    "f45344b9dc081a4d618986f4aa34f2210ee1e12157d69653994ddf66492d8550",
    "94f44f275b9e392b7984c3561d2d36dbedc9796d87c648a0ec54c8436bcfe225",
    "6ebbf71611dc211dc5f2212413210ca54a10d44e55720df50fb6c91f7394342a",
    "8b4842f06982817534a75bcf71865213b09dfa8313229c384e5201dadbd75e25",
    "89a85c545a97f322b528f4bf9a119a29107a18e3e444597db53845c88642b82e"
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
      "destination": "/app/data",
      "options": [
        "rbind",
        "rshared",
        "rw"
      ],
      "source": "sandbox:///tmp/atlas/azureFileVolume/.+",
      "type": "bind"
    },
    {
      "destination": "/tmp/cache",
      "options": [
        "rbind",
        "rshared",
        "rw"
      ],
      "source": "sandbox:///tmp/atlas/emptydir/.+",
      "type": "bind"
    }
  ],
  "command": [
    "/bin/sh",
    "-c",
    "node /usr/src/app/index.js"
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
    },
    {
      "pattern": "CONNECTION_DATA_.+=.*",
      "strategy": "re2",
      "required": true
    }
  ],
  "working_dir": "/usr/src/app"
}
