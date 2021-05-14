# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os
import subprocess
import sys
import traceback
from knack.util import CommandResultItem

from az_aks_tool.const import IS_WINDOWS, ENV_VAR_TEST_LIVE
from az_aks_tool.utils import heading
logger = logging.getLogger(__name__)


class ProfileContext:
    def __init__(self, profile_name=None):
        self.target_profile = profile_name

        self.origin_profile = current_profile()

    def __enter__(self):
        if self.target_profile is None or self.target_profile == self.origin_profile:
            logger.info('The tests are set to run against current profile "{}"'.format(
                self.origin_profile))
        else:
            result = cmd('az cloud update --profile {}'.format(self.target_profile),
                         'Switching to target profile "{}"...'.format(self.target_profile))
            if result.exit_code != 0:
                raise Exception(result.error.output.decode('utf-8'))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.target_profile is not None and self.target_profile != self.origin_profile:
            logger.info('Switching back to origin profile "{}"...'.format(
                self.origin_profile))
            call('az cloud update --profile {}'.format(self.origin_profile))

        if exc_tb:
            traceback.print_exception(exc_type, exc_val, exc_tb)


def current_profile():
    return cmd('az cloud show --query profile -otsv', show_stderr=False).result


class CommandError(Exception):

    def __init__(self, output, exit_code, command):
        message = "Command `{}` failed with exit code {}:\n{}".format(
            command, exit_code, output)
        self.exit_code = exit_code
        self.output = output
        self.command = command
        super().__init__(message)


def call(command, **kwargs):
    """ Run an arbitrary command but don't buffer the output.

    :param command: The entire command line to run.
    :param kwargs: Any kwargs supported by subprocess.Popen
    :returns: (int) process exit code.
    """
    return subprocess.call(
        command,
        shell=True,
        **kwargs)


def cmd(command, message=False, show_stderr=True, raise_error=False, **kwargs):
    """ Run an arbitrary command.

    :param command: The entire command line to run.
    :param message: A custom message to display, or True (bool) to use a default.
    :param show_stderr: On error, display the contents of STDERR.
    :param raise_error: On error, raise CommandError.
    :param kwargs: Any kwargs supported by subprocess.Popen
    :returns: CommandResultItem object.
    """

    # use default message if custom not provided
    if message is True:
        message = 'Running: {}\n'.format(command)

    if message:
        logger.info(message)

    logger.info("Running: %s", command)
    try:
        output = subprocess.check_output(
            command.split(),
            stderr=subprocess.STDOUT if show_stderr else None,
            shell=IS_WINDOWS,
            **kwargs).decode('utf-8').strip()
        logger.debug(output)
        return CommandResultItem(output, exit_code=0, error=None)
    except subprocess.CalledProcessError as err:
        if raise_error:
            raise CommandError(err.output.decode(), err.returncode, command)
        return CommandResultItem(err.output, exit_code=err.returncode, error=err)


def get_test_runner(parallel, log_path, last_failed, no_exit_first, mark):
    """Create a pytest execution method"""
    def _run(test_paths, pytest_args):

        if os.name == 'posix':
            arguments = ['-x', '-v', '--boxed', '-p no:warnings',
                         '--log-level=WARN', '--junit-xml', log_path]
        else:
            arguments = ['-x', '-v', '-p no:warnings',
                         '--log-level=WARN', '--junit-xml', log_path]

        if no_exit_first:
            arguments.remove('-x')

        if mark:
            arguments.append('-m "{}"'.format(mark))

        arguments.extend(test_paths)
        if parallel:
            arguments += ['-n', 'auto']
        if last_failed:
            arguments.append('--lf')
        if pytest_args:
            arguments += pytest_args
        cmd = 'python -m pytest {}'.format(' '.join(arguments))
        logger.info('Running: %s', cmd)
        return call(cmd)

    return _run


def run_tests(tests, test_index, mode, base_path, xml_file, json_file, in_series=False,
              run_live=False, profile=None, last_failed=False, no_exit_first=False, mark=None, pytest_args=None):

    heading('Run Tests')

    # process file path
    if not xml_file.startswith(mode):
        xml_file = "{}_{}".format(mode, xml_file)
    if not json_file.startswith(mode):
        json_file = "{}_{}".format(mode, json_file)
    xml_path = os.path.realpath(os.path.join(base_path, xml_file))
    json_path = os.path.realpath(os.path.join(base_path, json_file))
    pytest_args.append("--json-report-file {}".format(json_path))
    logger.info("junit/xml report file full path: {}".format(xml_path))
    logger.info("json report file full path: {}".format(json_path))

    # process environment variables
    if run_live:
        logger.warning('RUNNING TESTS LIVE')
        os.environ[ENV_VAR_TEST_LIVE] = 'True'

    def _find_test(index, name):
        name_comps = name.split('.')
        num_comps = len(name_comps)
        key_error = KeyError()

        for i in range(num_comps):
            check_name = '.'.join(name_comps[(-1 - i):])
            try:
                match = index[check_name]
                if check_name != name:
                    logger.info(
                        "Test found using just '%s'. The rest of the name was ignored.", check_name)
                return match
            except KeyError as ex:
                key_error = ex
                continue
        raise key_error

    # lookup test paths from index
    test_paths = []
    for t in tests:
        try:
            test_path = os.path.normpath(_find_test(test_index, t))
            test_paths.append(test_path)
        except KeyError:
            logger.warning("'%s' not found.", t)
            continue

    # Tests have been collected. Now run them.
    exit_code = 0
    if not test_paths:
        logger.warning('No tests selected to run.')
        return exit_code

    with ProfileContext(profile):
        runner = get_test_runner(parallel=not in_series,
                                 log_path=xml_path,
                                 last_failed=last_failed,
                                 no_exit_first=no_exit_first,
                                 mark=mark)
        exit_code = runner(test_paths=test_paths, pytest_args=pytest_args)

    return 0 if not exit_code else 1
