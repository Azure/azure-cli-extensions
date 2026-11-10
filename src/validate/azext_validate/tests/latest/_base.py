# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
"""Shared test helpers: no network for the whole test run, a private metadata cache, and a runner
that goes through the real CLI entry point."""

import io
import json
import os
import shutil
import socket
import tempfile
import time
import unittest
from unittest import mock

from azure.cli.core import get_default_cli, telemetry

from azext_validate import _engine, _extmeta, _validator

NETWORK_ATTEMPTS = []


def _blocked_network(*args, **_kwargs):
    NETWORK_ATTEMPTS.append(args[:2])
    raise OSError('network disabled in tests')


_PATCHES = [
    mock.patch.object(socket, 'getaddrinfo', _blocked_network),
    mock.patch.object(socket, 'create_connection', _blocked_network),
    mock.patch.object(socket.socket, 'connect', lambda self, *a: _blocked_network(*a)),
    mock.patch.object(socket.socket, 'connect_ex', lambda self, *a: _blocked_network(*a)),
]


_started = []


def block_network():  # S3: no network for the whole test module
    if not _started:
        for p in _PATCHES:
            p.start()
        _started.append(True)


def unblock_network():
    if _started:
        for p in _PATCHES:
            p.stop()
        _started.clear()


class TempStore(_extmeta.MetadataStore):
    """Metadata store with an empty, private cache directory."""
    root = None
    fake_session = None

    def __init__(self, config_dir, offline=False, session=None, now=time.time):
        super().__init__(config_dir, offline=offline, session=session or self.fake_session, now=now)
        self.cache_dir = os.path.join(self.root, 'cache')
        self.core_index_path = os.path.join(self.root, 'no-core-index.json')


def run_validate(*args, shell=None):
    cli = get_default_cli()
    out = io.StringIO()
    argv = ['validate'] + list(args) + (['--shell', shell] if shell else []) + ['-o', 'json']
    code = cli.invoke(argv, out_file=out)
    text = out.getvalue()
    return code, (json.loads(text) if text.strip() else None), text


class ValidateTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='azvalidate-test-')
        TempStore.root = self.tmp
        self.store_patch = mock.patch.object(_validator, 'MetadataStore', TempStore)
        self.store_patch.start()
        telemetry._session = telemetry.TelemetrySession()
        _engine.BLOCKED_CALLS.clear()
        NETWORK_ATTEMPTS.clear()

    def tearDown(self):
        self.store_patch.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)
