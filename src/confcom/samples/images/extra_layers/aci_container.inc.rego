{
  "id": "confcom_test_extra_layers",
  "name": "confcom_test_extra_layers",
  "layers": [
    "13f6c367267457d9516d57c493e76b0324979e94cee9de3b310f913708b3667a",
    "ae7e9183858927a54e0ae33a479948abd16a6f38712b84324191b900270cde8c"
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
  "command": [
    "sh"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    }
  ]
}
