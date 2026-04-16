{
  "id": "ghcr.io/radius-project/samples/demo:latest",
  "name": "ghcr.io/radius-project/samples/demo:latest",
  "layers": [
    "75f76b2620207ef52a83803bb27b3243a51b13304950ee97fd4a2540cd2f465f",
    "59c31a97dcce2c0ad99f2cf17259d8219e6c4cd124bc1394ab095d06c4ef7f5b",
    "0f3d7530222006ed59264af03b28095e595766c0b30a93d91468a717dc7616aa",
    "0d4f8d1e29f9e79bba609429da3cef21f17e57a1be70a03f3831865ee6893897",
    "7bc9bcba198443ecd416542322e965fdae2217058deba096d1489a309d24e2cf",
    "a21d4aba807cccaae033de52089054b0cf8c68ad96205205c5a5c631e308173f",
    "ed09faca596368d6fc491376f8313170615ee85ae8367c339830753f7d284189"
  ],
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
      "pattern": "NODE_VERSION=22.22.0",
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
      "pattern": "CONNECTIONS_REDIS_.+=.+",
      "strategy": "re2",
      "required": true
    }
  ],
  "working_dir": "/usr/src/app"
}
