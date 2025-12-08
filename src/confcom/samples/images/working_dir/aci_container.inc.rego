{
  "id": "confcom_test_working_dir",
  "name": "confcom_test_working_dir",
  "layers": [
    "8b4664979ffe3c5188efbbbb30e31716c03bfe880f15f455be0fc3beb4741de9",
    "1c4128b7270b18b052aff3f68a5611873057aa0b9ce3acfbf273494e67c63254"
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
  "working_dir": "/home"
}
