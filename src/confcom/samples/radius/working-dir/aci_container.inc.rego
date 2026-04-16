{
  "id": "alpine:3.19",
  "name": "alpine:3.19",
  "layers": [
    "6f937bc4d3707c87d1207acd64290d97ec90c8b87a7785cb307808afa49ff892"
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
    "/bin/sh"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    }
  ],
  "working_dir": "/app/src"
}
