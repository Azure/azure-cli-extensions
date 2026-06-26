{
  "id": "confcom_test_environment_variables",
  "name": "confcom_test_environment_variables",
  "layers": [
    "f1ba3e38cc8c3755648e05aa57ea155496e9a2e42fd2454932b6647bc93575b2"
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
    "/hello"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "TEST_ENV_VAR=Test Env Value",
      "strategy": "string",
      "required": false
    }
  ],
  "working_dir": "/"
}
