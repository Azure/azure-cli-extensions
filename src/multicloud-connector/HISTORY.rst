.. :changelog:

Release History
===============
1.1.0
++++++
* Target the ``2027-01-01`` GA version of the Microsoft.HybridConnectivity API
* Add GCP support to ``public-cloud-connector create`` and ``public-cloud-connector update`` via ``--gcp-cloud-profile``
* Support ``GCP`` as a value of ``--host-type``
* Add ``generate-gcp-template`` command to retrieve the GCP access control template
* Surface the read-only ``kind`` property on public cloud connectors and ``hostTypes`` on solution types

1.0.1
++++++
* Update help message for better readability

1.0.0
++++++
* GA release
* Register all required RPs before running each command
* Reflect API swagger changes
* Store the output of ``generate-aws-template`` to json file on disk
* Update help guide with more examples

1.0.0b1
++++++
* Initial release.