# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import subprocess
import logging
import traceback
from knack.util import CommandResultItem

logger = logging.getLogger(__name__)

def display(txt):
    """ Output to stderr """
    print(txt, file=sys.stderr)

class ProfileContext:
    def __init__(self, profile_name=None):
        self.target_profile = profile_name

        self.origin_profile = current_profile()

    def __enter__(self):
        if self.target_profile is None or self.target_profile == self.origin_profile:
            display('The tests are set to run against current profile "{}"'.format(self.origin_profile))
        else:
            result = cmd('az cloud update --profile {}'.format(self.target_profile),
                         'Switching to target profile "{}"...'.format(self.target_profile))
            if result.exit_code != 0:
                raise Exception(result.error.output.decode('utf-8'))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.target_profile is not None and self.target_profile != self.origin_profile:
            display('Switching back to origin profile "{}"...'.format(self.origin_profile))
            call('az cloud update --profile {}'.format(self.origin_profile))

        if exc_tb:
            display('')
            traceback.print_exception(exc_type, exc_val, exc_tb)


def current_profile():
    return cmd('az cloud show --query profile -otsv', show_stderr=False).result


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
    from azdev.utilities import IS_WINDOWS, display

    # use default message if custom not provided
    if message is True:
        message = 'Running: {}\n'.format(command)

    if message:
        display(message)

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
            arguments = ['-x', '-v', '--boxed', '-p no:warnings', '--log-level=WARN', '--junit-xml', log_path]
        else:
            arguments = ['-x', '-v', '-p no:warnings', '--log-level=WARN', '--junit-xml', log_path]

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


# pylint: disable=too-many-statements,too-many-locals
# def run_tests(tests, xml_path=None, discover=False, in_series=False,
#               run_live=False, profile=None, last_failed=False, pytest_args=None,
#               no_exit_first=False, mark=None,
#               git_source=None, git_target=None, git_repo=None,
#               cli_ci=False):




#     path_table = get_path_table()

#     test_index = _get_test_index(profile or current_profile(), discover)

#     if not tests:
#         tests = list(path_table['mod'].keys()) + list(path_table['core'].keys()) + list(path_table['ext'].keys())
#     if tests == ['CLI']:
#         tests = list(path_table['mod'].keys()) + list(path_table['core'].keys())
#     elif tests == ['EXT']:
#         tests = list(path_table['ext'].keys())

#     # filter out tests whose modules haven't changed
#     modified_mods = _filter_by_git_diff(tests, test_index, git_source, git_target, git_repo)
#     if modified_mods:
#         display('\nTest on modules: {}\n'.format(', '.join(modified_mods)))

#     if cli_ci is True:
#         ctx = CLIAzureDevOpsContext(git_repo, git_source, git_target)
#         modified_mods = ctx.filter(test_index)


#     # process environment variables
#     if run_live:
#         logger.warning('RUNNING TESTS LIVE')
#         os.environ[ENV_VAR_TEST_LIVE] = 'True'

#     def _find_test(index, name):
#         name_comps = name.split('.')
#         num_comps = len(name_comps)
#         key_error = KeyError()

#         for i in range(num_comps):
#             check_name = '.'.join(name_comps[(-1 - i):])
#             try:
#                 match = index[check_name]
#                 if check_name != name:
#                     logger.info("Test found using just '%s'. The rest of the name was ignored.\n", check_name)
#                 return match
#             except KeyError as ex:
#                 key_error = ex
#                 continue
#         raise key_error

#     # lookup test paths from index
#     test_paths = []
#     for t in modified_mods:
#         try:
#             test_path = os.path.normpath(_find_test(test_index, t))
#             test_paths.append(test_path)
#         except KeyError:
#             logger.warning("'%s' not found. If newly added, re-run with --discover", t)
#             continue

#     exit_code = 0

#     # Tests have been collected. Now run them.
#     if not test_paths:
#         logger.warning('No tests selected to run.')
#         sys.exit(exit_code)

#     exit_code = 0
#     with ProfileContext(profile):
#         runner = get_test_runner(parallel=not in_series,
#                                  log_path=xml_path,
#                                  last_failed=last_failed,
#                                  no_exit_first=no_exit_first,
#                                  mark=mark)
#         exit_code = runner(test_paths=test_paths, pytest_args=pytest_args)

#     sys.exit(0 if not exit_code else 1)
