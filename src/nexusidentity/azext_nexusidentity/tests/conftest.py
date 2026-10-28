# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Adapt NexusIdentity reports for upstream Azure CLI Extensions PR validation.

The GitHub PR's Azure Pipelines validation invokes ``azdev test``, which adds
``--forked``. Current pipeline runs have installed pytest 9.2.0 with pytest-forked 1.7.5:
https://dev.azure.com/azclitools/public/_build/results?buildId=367334

These runner versions are incompatible: pytest 9.2 stores a NodeId object in
the report's private ``_id`` field, while pytest-forked copies the report's
``__dict__`` and serializes it with marshal. NodeId is not marshal-serializable.
The runner hides ``ValueError: unmarshallable object`` and exits with status 3,
attributing the process failure to test_nexusidentity_key_publication even
when the scenario itself passes.

This adapter replaces only that serialized field with the public string
``nodeid`` accepted by pytest's TestReport constructor. It loads automatically
in upstream CI without an installation patch, preserves process isolation,
test outcomes and failure details, and leaves older string-based reports
unchanged. The original serializer is restored at configuration cleanup.

Alternatives and why this adapter is used:

* Upgrading Azure CLI alone does not fix pytest-forked's report serializer.
  The failure was also reproduced locally with Azure CLI 2.92.
* Fixing pytest-forked upstream and having CI install a corrected release is
  the preferred long-term solution. Version 1.7.5 still has this defect.
* Pinning pytest to 9.1.1 restores compatibility, but must be done in upstream
  CI's environment; a local pin does not affect that pipeline.
* Patching the installed runner during setup would work only if upstream CI
  also ran that patch. This adapter instead travels with the extension tests.
* Running pytest directly without --forked avoids the defect but changes
  process isolation and requires changing the upstream test command.
  azdev's --series option disables parallel workers, not forking.

Changing the scenario body cannot repair report serialization. Keeping pytest
9.2 and the existing upstream CI command without this adapter requires a
corrected pytest-forked installation.
"""

from functools import wraps


def pytest_configure(config):
    forked = config.pluginmanager.getplugin("pytest_forked")
    if forked is None:
        return

    original = forked.serialize_report

    @wraps(original)
    def serialize_report(report):
        data = original(report)
        # pytest 9.2 stores NodeId internally; TestReport accepts its public string.
        if "_id" in data:
            del data["_id"]
            data["nodeid"] = report.nodeid
        return data

    forked.serialize_report = serialize_report
    config.add_cleanup(lambda: setattr(forked, "serialize_report", original))
