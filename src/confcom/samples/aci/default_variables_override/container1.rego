{
    "command": [
        "python3",
        "main.py"
    ],
    "env_rules": [
        {
            "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "required": false,
            "strategy": "string"
        },
        {
            "pattern": "PYTHONUNBUFFERED=1",
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
    "id": "mcr.microsoft.com/acc/samples/aci/helloworld@sha256:86da7a2c5e55b72bf6bc7cf465b860e49c075395d854877124de63a9342ac777",
    "layers": [
        "4e74440c7b0e6e6c1cc9e6eb9b779e1ffde807122ed8a16bb0422a1d64fd5aa8",
        "4cf856bcde8e1fa71f57d2218e21dd7c1a6a12c6d930d2bdb4bdb13a46fed9e4",
        "41a52f45506177737caec5d57fe6160b6c8942dcac1bc7834fc0e94e62ff6b4d",
        "b8ea8eae7795453b5e3dcfafe3f11fb2d68efb1062308e4d2411d44dd19fa97c",
        "a0df1939f552483286c45204e7f583c9a6146963a79556fe22578d7b7e63e7a1",
        "3ccbd6b119e951f3f2586339e9d10168b064a5852fd87cfae94af47a89f4d6c6",
        "8348c9d4357db6a600aa4c5116ed9755a230d274096706a7d214c02105d0b256"
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
    "working_dir": "/app"
}