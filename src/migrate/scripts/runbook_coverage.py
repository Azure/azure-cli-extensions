#!/usr/bin/env python
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Measure unit-test coverage for the runbook package (``azext_migrate/runbook``).

Runs the runbook unit + scenario suites under ``coverage`` scoped to the
runbook source only, then prints a per-file report with missing lines and the
total percentage. Intended to be run locally and in CI on every PR.

Usage (from anywhere)::

    python src/migrate/scripts/runbook_coverage.py [--fail-under N] [-- <pytest args>]

``--fail-under N`` exits non-zero when total coverage is below ``N``
(defaults to 95). Pass ``--fail-under 0`` to report without gating.

Prerequisite: ``pip install coverage``.
"""

import argparse
import os
import subprocess
import sys

# src/migrate — coverage + pytest run with this as the working directory so the
# tests load the source package (not any build artifact).
_MIGRATE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SOURCE = os.path.join('azext_migrate', 'runbook')
_TESTS = [
    os.path.join('azext_migrate', 'tests', 'latest', 'runbook',
                 'test_runbook_unit.py'),
    os.path.join('azext_migrate', 'tests', 'latest', 'runbook',
                 'test_runbook_scenario.py'),
]


def _run(args):
    return subprocess.call([sys.executable, '-m'] + args, cwd=_MIGRATE_ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--fail-under', type=float, default=95.0,
        help='Exit non-zero if total coverage is below this percentage '
             '(default: 95).')
    parser.add_argument(
        'pytest_args', nargs='*',
        help='Extra arguments forwarded to pytest.')
    opts = parser.parse_args()

    try:
        import coverage  # noqa: F401  (presence check only)
    except ImportError:
        sys.exit('coverage is not installed. Run: pip install coverage')

    run_rc = _run([
        'coverage', 'run', '--source', _SOURCE, '-m', 'pytest',
        *_TESTS, '-q', '--import-mode=importlib', '-p', 'no:cacheprovider',
        *opts.pytest_args])
    if run_rc != 0:
        sys.exit(run_rc)  # tests failed; coverage is meaningless

    report = ['coverage', 'report', '-m']
    if opts.fail_under is not None:
        report += ['--fail-under', str(opts.fail_under)]
    sys.exit(_run(report))


if __name__ == '__main__':
    main()
