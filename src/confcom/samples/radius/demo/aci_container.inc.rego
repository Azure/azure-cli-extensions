{
  "TODO": "use a stable tag",
  "id": "ghcr.io/radius-project/samples/demo:latest",
  "name": "ghcr.io/radius-project/samples/demo:latest",
  "layers": [
    "0b5d60458546072c2bbdd10e4f7945269804ad8b9f38681a453c7095bc5e1f16",
    "dbb256e70a8fb2cdd20474f2c1e8a5eff0c818cc17e795bc1645cda49cb3d7db",
    "a6da557c1af67b877134b37ce68e0a3c1ea0e90c531b9f009191a51c56eb8511",
    "101c4d258cab057dd7e23c4315781ec2c36d56074d823f8c2f33021a81877640",
    "0513f0dc5688c9c527b9faee572f2ece3f115b9ab9691204a8d16fc0fbacac4a",
    "2a61e3e42c8497e414a574a8f839dab99b258cb215e5edb72344716170577217",
    "9649c2fcda1caf460e2c6cc82573e493a08964a3891aa00e21360f7997dc9bc2"
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
    }
  ],
  "command": [
    "docker-entrypoint.sh"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "NODE_VERSION=22.22.3",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "YARN_VERSION=1.22.22",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "PORT=3000",
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
      "pattern": "CONNECTION_REDIS_.+=.*",
      "strategy": "re2",
      "required": true
    }
  ],
  "working_dir": "/usr/src/app"
}
