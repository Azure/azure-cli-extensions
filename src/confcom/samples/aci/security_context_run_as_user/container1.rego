{
    "env_rules": [
        {
            "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "required": false,
            "strategy": "string"
        },
        {
            "pattern": "TERM=xterm",
            "required": false,
            "strategy": "string"
        },
        {
            "pattern": "(?i)(FABRIC)_.+=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "HOSTNAME=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "T(E)?MP=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "FabricPackageFileName=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "HostedServiceName=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "IDENTITY_API_VERSION=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "IDENTITY_HEADER=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "IDENTITY_SERVER_THUMBPRINT=.+",
            "required": false,
            "strategy": "re2"
        },
        {
            "pattern": "azurecontainerinstance_restarted_by=.+",
            "required": false,
            "strategy": "re2"
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
            "source": "sandbox:///tmp/atlas/resolvconf/.+",
            "type": "bind"
        }
    ],
    "name": "container1",
    "user": {
        "user_idname": {
            "pattern": "1234",
            "strategy": "id"
        }
    }
}