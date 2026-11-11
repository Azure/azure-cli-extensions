.. :changelog:

Release History
===============

1.0.0b7
+++++++
* Resolve Windows ssh-keygen from supported system installation paths.
* Support native OpenSSH installation discovery from 32-bit Azure CLI on 64-bit Windows.
* Stop processing when SSH key generation fails.

1.0.0b6
+++++++
* Resolves installation issue caused by Graphs Python SDK package where a long path error occured. To fix this - SDK support was removed and replaced with httpclient.

1.0.0b5
+++++++
* Adding support for older algorithm ssh keys

1.0.0b4
+++++++
* Adding support for Linux platform

1.0.0b3
++++++
* Adding print statements to o/p creation & update of extensions.

1.0.0b2
++++++
* Pinning the dependency azure-identity version to 1.17.1
* Adding error handling to support file not found error

1.0.0b1
++++++
* Initial release.