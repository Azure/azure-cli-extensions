[
  {
    "command": [],
    "env_rules": [
      {
        "pattern": "FROM_CONFIG=value-one",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "FROM_BINARY_CONFIG=value-binary",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "FROM_SECRET=value-secret",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "FROM_STRINGDATA=value-plain",
        "required": false,
        "strategy": "string"
      },
      {
        "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "required": false,
        "strategy": "string"
      }
    ],
    "id": "mcr.microsoft.com/azurelinux/distroless/base@sha256:1e77d97e1e39f22ed9c52f49b3508b4c1044cec23743df9098ac44e025f654f2",
    "layers": [
      "243e1b3ce08093f2f0d9cd6a9eafde8737f64fec105ed59c346d309fbe760b58"
    ],
    "mounts": [
      {
        "destination": "/etc/resolv.conf",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/var/run/secrets/kubernetes.io/serviceaccount",
        "options": [
          "rbind",
          "rshared",
          "ro"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/etc/hosts",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/dev/termination-log",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      },
      {
        "destination": "/etc/hostname",
        "options": [
          "rbind",
          "rshared",
          "rw"
        ],
        "source": "sandbox:///tmp/atlas/emptydir/.+",
        "type": "bind"
      }
    ],
    "name": "app",
    "working_dir": "/"
  }
]
