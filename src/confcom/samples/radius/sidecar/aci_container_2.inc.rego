{
  "id": "prom/node-exporter:v1.6.0",
  "name": "prom/node-exporter:v1.6.0",
  "layers": [
    "7a580d3787151687569bf746ee21f3efff8a44c25a05516422f081b0b37ede8a",
    "99078a17fc9f1f4e964f4f07056b14ace4f15cf6cce47534f94ce79b90190d5f",
    "2d01b6595212164df2bb77813c093e4a5b7541ec7eb78bdd01c6a88d79a1bfc2"
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
    "/bin/node_exporter"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    }
  ]
}
