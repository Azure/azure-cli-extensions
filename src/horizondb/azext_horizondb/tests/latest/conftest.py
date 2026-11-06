# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest


def pytest_configure(config):
    forked = config.pluginmanager.get_plugin('pytest_forked')
    if forked is None:
        return

    original_serializer = forked.serialize_report

    def serialize_report(report):
        data = original_serializer(report)
        # Match pytest's wire format; pytest-forked 1.7.5 cannot marshal pytest 9.2 NodeIds.
        if '_id' in data:
            data['nodeid'] = str(data.pop('_id'))
        return data

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(forked, 'serialize_report', serialize_report)
    config.add_cleanup(monkeypatch.undo)
