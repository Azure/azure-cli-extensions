# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
This script is used to run azdev scan on modified extensions in PR pipelines.

It reuses find_modified_files_against_master_branch() from util.py to get an
accurate list of files changed in the PR (via merge-base), then runs
azdev scan on each file.
"""
import json
import logging
import sys
from subprocess import CalledProcessError, check_output

from util import find_modified_files_against_master_branch

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def run_scan(modified_files, confidence_level=None):
    """Run azdev scan on each modified file and report secrets."""
    confidence_flag = []
    confidence_msg = ''
    if confidence_level:
        confidence_flag = ['--confidence-level', confidence_level]
        confidence_msg = ' --confidence-level {}'.format(confidence_level)

    secret_files = []
    failed_files = []
    for f in modified_files:
        cmd = ['azdev', 'scan', '-f', f, '--continue-on-failure'] + confidence_flag
        logger.info('Scanning: %s', f)
        try:
            output = check_output(cmd).decode('utf-8', errors='replace')
            result = json.loads(output)
            if result.get('secrets_detected') is True:
                logger.error(
                    '\033[0;31mSecrets detected from %s, Please remove or replace it. '
                    'You can run \'azdev scan%s\'/\'azdev mask%s\' locally to fix.\033[0m',
                    f, confidence_msg, confidence_msg
                )
                secret_files.append(f)
        except CalledProcessError as e:
            logger.error('azdev scan failed for %s: %s', f, e)
            failed_files.append(f)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error('Failed to parse azdev scan output for %s: %s', f, e)
            failed_files.append(f)

    has_errors = False
    if secret_files:
        logger.error('Secrets detected in %d file(s): %s', len(secret_files), secret_files)
        has_errors = True
    if failed_files:
        logger.error('Scan failed for %d file(s): %s', len(failed_files), failed_files)
        has_errors = True
    if has_errors:
        sys.exit(1)
    else:
        logger.info('-' * 100)
        logger.info('No secrets detected in any modified files.')
        logger.info('-' * 100)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='azdev scan on modified extensions')
    parser.add_argument('--confidence-level',
                        type=str,
                        default=None,
                        help='Confidence level for azdev scan (e.g., MEDIUM). '
                             'Default: HIGH (azdev scan default).')
    args = parser.parse_args()

    modified_files = find_modified_files_against_master_branch()
    if not modified_files:
        logger.info('No modified files found, skipping scan.')
        return

    run_scan(modified_files, confidence_level=args.confidence_level)


if __name__ == '__main__':
    main()
