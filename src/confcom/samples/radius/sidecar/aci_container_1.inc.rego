{
  "id": "fluent/fluent-bit:2.1",
  "name": "fluent/fluent-bit:2.1",
  "layers": [
    "c9ece343c622c4ec9c420cefb552e74ecf9cd6d695ceec0a507e29f2a94469b5",
    "82fb7fc0439dda36d1d3145378a8b1f5e5eb6f3c3053876b331c0e7839b5a8aa",
    "2d5007a19e4369e60a149d3fc10342275e186448c0d355e04414f74a4c1cabfa",
    "6c23cf620e0f8fd2f630bad98814040e89768652d62ed40dbb73aaf2ebed028c",
    "2c6f540907e3fd5b6182cded7492b68f8ce9332f30e89436afab59271c8592d8",
    "ac3801059d83cfb321d565fb31653ae6e1a8741bc29c54fe6b1229b097e469e5",
    "7b4fbef988c8f7e20a7e469cf1109e74018bebac8221a5e27b0fdaac3b6f1772",
    "1e9c60962369a61fca177bf0421e6b11f1758cb3f1630cfe6a8693dba1a48910",
    "305b68459e325133b30c7846567a7ba0ca291d8d6d5091205aa5f6ccf2b2982e",
    "b0b8d88bc0fa3e6b9ad462ad384793b3aa6278822d5a6c1ea29e2f23f0c66992",
    "f9d43418841515426a14c08a998d1e680b76cf578ab8515af97401cb12e8dbaa",
    "b9051e32eeec3446b227c38d01d76f2a57d1a972517256f7f4ac8bb791ae5ac0",
    "06a5da170bb9bec3146fa1652b4b0823d52b00bdfb60abb2a9ba5a2cbaec92d9",
    "bdc57a4217ffbd60a494f10b29c63c85ab729fa95f8d406343cfcbedd73f535a",
    "e2a7e7f6f652f64fd74dd3d39ffe3ca1e67e74e4322c417590a934d3554ece7b",
    "2d5054f1223c542eec390a27f5ad159f9bbeebfcd454597471c0d4ec95a803a9",
    "de09ba99efa50232090cb64f96a2e8e9216b24ac5316c0978fafd86c51916aa6",
    "06da377ea013ef94f430ee264721162741e4c3cd60b0a2b84943241938432d3f"
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
    "/fluent-bit/bin/fluent-bit"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "FLUENT_BIT_VERSION=2.1.10",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "FLUENT_OUTPUT=stdout",
      "strategy": "string",
      "required": false
    }
  ],
  "working_dir": "/"
}
