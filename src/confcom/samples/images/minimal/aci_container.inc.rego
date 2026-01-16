{
  "id": "confcom_test_minimal",
  "name": "confcom_test_minimal",
  "layers": [
    "8b4664979ffe3c5188efbbbb30e31716c03bfe880f15f455be0fc3beb4741de9"
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
    "/hello"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    }
  ],
  "working_dir": "/"
}
