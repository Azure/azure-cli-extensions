# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Run CDN scenarios with separate per-case processes and bounded execution."""

import argparse
import contextlib
from datetime import datetime, timezone
import faulthandler
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

from .config import timeout_settings


TEST_DIR = Path(__file__).parent


def collect_tests(names):
    suite = unittest.defaultTestLoader.discover(
        str(TEST_DIR), pattern='test_*scenarios.py', top_level_dir=str(TEST_DIR.parents[2]))
    cases = []

    def collect(items):
        for item in items:
            if isinstance(item, unittest.TestSuite):
                collect(item)
            else:
                if isinstance(item, unittest.loader._FailedTest):  # pylint: disable=protected-access
                    raise RuntimeError(f'Cannot collect {item.id()}') from item._exception  # pylint: disable=protected-access
                cases.append(item.id())

    collect(suite)
    if names:
        missing = set(names) - {case.rsplit('.', 1)[-1] for case in cases}
        if missing:
            raise ValueError('Unknown scenario names: ' + ', '.join(sorted(missing)))
        cases = [case for case in cases if case.rsplit('.', 1)[-1] in names]
    return cases


def run_with_timeout(command, log_path, timeout):
    env = None
    base_executable = sys._base_executable  # pylint: disable=protected-access
    if sys.platform == 'win32' and command[0] == sys.executable and base_executable != sys.executable:
        # Match multiprocessing: wait on Python itself, not the Windows venv redirector.
        command = [base_executable, *command[1:]]
        env = os.environ.copy()
        env['__PYVENV_LAUNCHER__'] = sys.executable
    with log_path.open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
        try:
            deadline = time.time() + timeout
            while True:
                remaining = deadline - time.time()
                if remaining <= 0:
                    process.kill()
                    process.wait(timeout=10)
                    return 124
                try:
                    return process.wait(timeout=min(remaining, 1))
                except subprocess.TimeoutExpired:
                    pass
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)


def preserve_failed_recording(recording, original, output_dir):
    failed_dir = output_dir / 'failed-recordings'
    failed_dir.mkdir(exist_ok=True)
    for path in (recording, recording.with_suffix('.temp.yaml')):
        if path.exists():
            shutil.copy2(path, failed_dir / path.name)
            if path != recording:
                path.unlink()
    if original is None:
        recording.unlink(missing_ok=True)
    else:
        recording.write_bytes(original)


def _worker(case, output_dir, timeout):
    import pytest

    module, class_name, method = case.rsplit('.', 2)
    node = str(TEST_DIR / (module.rsplit('.', 1)[-1] + '.py')) + '::' + class_name + '::' + method
    faulthandler.enable()
    faulthandler.dump_traceback_later(max(1, timeout * 0.8))
    try:
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch('azure.cli.core.util.handle_version_update'))
            stack.enter_context(patch('azure.cli.core.util.show_updates_available'))
            if os.environ.get('AZURE_TEST_RUN_LIVE') != 'true':
                for target in ('socket.socket.connect', 'socket.getaddrinfo'):
                    stack.enter_context(patch(target, side_effect=AssertionError('Playback must not access the network')))
            return pytest.main([
                node, '-q', '-p', 'no:cacheprovider', '--disable-warnings', '--log-cli-level=INFO',
                '--junitxml=' + str(output_dir / (method + '.xml')),
            ])
    finally:
        faulthandler.cancel_dump_traceback_later()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('record', 'replay'))
    parser.add_argument('tests', nargs='*', help='Optional scenario method names')
    parser.add_argument('--config', help='JSON overrides for the committed CDN test environment')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--list', action='store_true', help='List selected scenarios without running them')
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    parser.add_argument('--worker-timeout', type=float, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.config:
        os.environ['AZURE_CDN_TEST_CONFIG'] = str(Path(args.config).resolve())
    if args.mode == 'record':
        os.environ['AZURE_TEST_RUN_LIVE'] = 'true'
    else:
        os.environ.pop('AZURE_TEST_RUN_LIVE', None)
    os.environ['AZURE_CORE_COLLECT_TELEMETRY'] = 'false'
    os.environ['AZURE_EXTENSION_USE_DYNAMIC_INSTALL'] = 'no'
    limits = timeout_settings(args.mode)
    if args.worker:
        return _worker(args.worker, args.output_dir, args.worker_timeout)

    cases = collect_tests(args.tests)
    if args.list:
        print('\n'.join(cases))
        return 0
    output_dir = (args.output_dir or TEST_DIR.parents[2] / '.test-results' /
                  datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    deadline = time.time() + limits['suite_seconds']
    for case in cases:
        name = case.rsplit('.', 1)[-1]
        remaining = deadline - time.time()
        if remaining <= 0:
            results.append({'case': case, 'status': 'not_run', 'reason': 'Suite timeout'})
            continue
        recording = TEST_DIR / 'recordings' / (name + '.yaml')
        original = recording.read_bytes() if recording.exists() else None
        if args.mode == 'replay' and original is None:
            results.append({'case': case, 'status': 'failed', 'reason': 'Recording is missing'})
            continue
        timeout = min(limits['case_seconds'], remaining)
        command = [
            sys.executable, '-m', __spec__.name, args.mode, '--worker', case,
            '--output-dir', str(output_dir), '--worker-timeout', str(timeout),
        ]
        print(f'Running {name} (deadline {timeout:.1f}s)', flush=True)
        code = run_with_timeout(command, output_dir / (name + '.log'), timeout)
        if code != 0 and args.mode == 'record':
            preserve_failed_recording(recording, original, output_dir)
        status = 'passed' if code == 0 else 'timeout' if code == 124 else 'failed'
        results.append({'case': case, 'status': status, 'exit_code': code})
        (output_dir / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(f'{name}: {status}', flush=True)
    (output_dir / 'results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'Results: {output_dir}', flush=True)
    return 0 if all(case['status'] == 'passed' for case in results) else 1


if __name__ == '__main__':
    sys.exit(main())
