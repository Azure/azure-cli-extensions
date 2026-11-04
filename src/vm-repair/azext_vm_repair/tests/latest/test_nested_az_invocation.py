# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Regression tests for validated nested Azure CLI invocation and error reporting.

import json
import os
import sys
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair import repair_utils
from azext_vm_repair.repair_utils import _call_az_command
from azure.cli.core.azclierror import InvalidArgumentValueError


class _FakeProcess:
    """Minimal stand-in for a subprocess.Popen object."""

    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr

    def communicate(self):
        return self._stdout, self._stderr


def _windows_command_line(mock_popen, command):
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'nt'):
        _call_az_command(command)
    return mock_popen.call_args[0][0]


# ---------------------------------------------------------------------------
# 1. Command construction
# ---------------------------------------------------------------------------

@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_uses_validated_batch_launcher_without_isolated_python(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az vm show -g rg -n vm')

    interpreter = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', 'cmd.exe')
    assert command_line == subprocess.list2cmdline([interpreter]) + \
        ' /d /v:off /s /c "az "vm" "show" "-g" "rg" "-n" "vm""'
    assert mock_popen.call_args.kwargs['shell'] is False


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_command_without_arguments(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    command_line = _windows_command_line(mock_popen, 'az')

    interpreter = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', 'cmd.exe')
    assert command_line == subprocess.list2cmdline([interpreter]) + ' /d /v:off /s /c "az "'


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_windows_metacharacters_in_arguments_are_still_neutralized(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    with pytest.raises(InvalidArgumentValueError):
        _windows_command_line(mock_popen, 'az vm create --tags "env=ok&echo pwned>file.txt&rem"')
    mock_popen.assert_not_called()


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_posix_still_uses_argument_list(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='ok')
    with mock.patch('azext_vm_repair.repair_utils.os.name', 'posix'):
        _call_az_command('az vm create --tags env=ok&echo')

    command_args = mock_popen.call_args[0][0]
    assert isinstance(command_args, list)
    assert command_args[0] == 'az'


# ---------------------------------------------------------------------------
# 2. Error surfacing
# ---------------------------------------------------------------------------

@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_failure_with_empty_stderr_reports_stdout(mock_popen):
    # Exact production signature: az.cmd reports on stdout and leaves stderr empty.
    mock_popen.return_value = _FakeProcess(
        returncode=1, stdout='Failed to load python executable.', stderr='')

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g rg -n vm')

    assert 'Failed to load python executable.' in str(raised.value)


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_failure_with_no_output_reports_exit_code(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=3, stdout='   ', stderr='  ')

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g rg -n vm')

    message = str(raised.value)
    assert message.strip(), 'AzCommandError must never be raised with an empty message'
    assert '3' in message


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_failure_prefers_stderr_when_present(mock_popen):
    mock_popen.return_value = _FakeProcess(
        returncode=1, stdout='noise on stdout', stderr='ERROR: (AuthorizationFailed) denied')

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm show -g rg -n vm')

    assert 'AuthorizationFailed' in str(raised.value)
    assert 'noise on stdout' not in str(raised.value)


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_secure_params_are_masked_in_error_message(mock_popen):
    # The error text is emitted to the user and to telemetry, so secure parameters must not leak.
    secure_value = 'unit-test-secure-parameter-value'
    mock_popen.return_value = _FakeProcess(
        returncode=1, stdout='', stderr='failed using {0}'.format(secure_value))

    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az vm create -g rg -n vm', secure_params=[secure_value])

    assert secure_value not in str(raised.value)
    assert '********' in str(raised.value)


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_successful_command_returns_stdout(mock_popen):
    mock_popen.return_value = _FakeProcess(returncode=0, stdout='{"id": "abc"}', stderr='')

    assert _call_az_command('az vm show -g rg -n vm') == '{"id": "abc"}'


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_non_az_command_is_still_rejected(mock_popen):
    with pytest.raises(AzCommandError):
        _call_az_command('notaz vm create')
    mock_popen.assert_not_called()


# ---------------------------------------------------------------------------
# 3. Real execution proofs (Windows only)
# ---------------------------------------------------------------------------

@pytest.fixture(params=['clean', 'cwd', 'pythonpath'])
def nested_cli_environment(request, tmp_path, monkeypatch):
    marker = tmp_path / 'shadow-cli-ran.txt'
    working_directory = tmp_path / 'working directory'
    working_directory.mkdir()
    monkeypatch.delenv('PYTHONPATH', raising=False)
    if request.param != 'clean':
        shadow_root = tmp_path / 'untrusted packages'
        package = shadow_root / 'azure' / 'cli'
        package.mkdir(parents=True)
        (package.parent / '__init__.py').write_text('', encoding='utf-8')
        (package / '__init__.py').write_text('', encoding='utf-8')
        (package / '__main__.py').write_text(
            'from pathlib import Path\n'
            'Path({!r}).write_text("shadow CLI executed", encoding="utf-8")\n'
            'print(\'{{"shadow-cli": true}}\')\n'.format(str(marker)),
            encoding='utf-8')
        if request.param == 'cwd':
            working_directory = shadow_root
            (working_directory / 'cmd.exe').write_bytes(b'Not a Windows executable')
        else:
            monkeypatch.setenv('PYTHONPATH', str(shadow_root))
    monkeypatch.chdir(working_directory)
    return marker


@pytest.mark.skipif(os.name != 'nt', reason='batch launch is Windows-specific')
def test_real_nested_az_call_succeeds(nested_cli_environment):
    output = _call_az_command('az version -o json')

    assert not nested_cli_environment.exists(), 'An untrusted package replaced Azure CLI'
    assert json.loads(output).get('azure-cli')


@pytest.mark.skipif(os.name != 'nt', reason='batch launch is Windows-specific')
def test_real_failing_az_call_reports_a_message(nested_cli_environment):
    # A genuinely failing az command must produce a non-empty, actionable error.
    with pytest.raises(AzCommandError) as raised:
        _call_az_command('az version --vm-repair-invalid-option')

    assert str(raised.value).strip()
    assert not nested_cli_environment.exists(), 'An untrusted package replaced Azure CLI'


@pytest.mark.skipif(os.name != 'nt', reason='batch launch is Windows-specific')
@pytest.mark.parametrize('installation_name', ["O'Brien", 'Program Files (x86)', "O'Brien (x86) & tools"])
@pytest.mark.parametrize('driver,is_linux,custom_scripts', [
    ('win-run-driver.ps1', False, True),
    ('linux-mount-encrypted-disk.sh', True, False),
    ('win-mount-encrypted-disk.ps1', False, False),
])
def test_real_script_paths_preserve_symbols_and_caller_directory(
        tmp_path, monkeypatch, installation_name, driver, is_linux, custom_scripts):
    caller_directory = tmp_path / "caller O'Brien (x86)"
    extension_directory = tmp_path / installation_name
    caller_directory.mkdir()
    extension_directory.mkdir()
    scripts_directory = extension_directory / 'scripts'
    scripts_directory.mkdir()
    driver_content = 'driver-script\n# \u4fee\u590d\n'
    (scripts_directory / driver).write_text(driver_content, encoding='utf-16')
    custom_names = ["custom O'Brien (x86) & ^ $ ` ;.ps1", 'second custom script.ps1']
    custom_contents = ['caller-script\n\n', '# \u4fee\u590d\nsecond-script\n']
    for name, content in zip(custom_names, custom_contents):
        (caller_directory / name).write_text(content, encoding='utf-8-sig')
        (extension_directory / name).write_text('decoy-script', encoding='utf-8')
    marker = caller_directory / 'untrusted-az-ran.txt'
    (caller_directory / 'az.cmd').write_text(
        '@echo off\necho untrusted>"{}"\nexit /b 1\n'.format(marker), encoding='utf-8')
    receiver = tmp_path / 'script receiver.py'
    receiver.write_text(
        'import json, os, sys\n'
        'from azure.cli.core.commands import _expand_file_prefixed_files\n'
        'arguments = sys.argv[1:]\n'
        'scripts = arguments[arguments.index("--scripts") + 1:arguments.index("-o")]\n'
        'result = json.dumps({"cwd": os.getcwd(), "scripts": scripts,\n'
        '                     "contents": _expand_file_prefixed_files(scripts)})\n'
        'if arguments[arguments.index("--command-id") + 1] == "RunShellScript":\n'
        '    result = "[stdout]\\n" + result + "\\n[stderr]\\n"\n'
        'print(json.dumps({"value": [{"message": result}, {"message": ""}]}))\n',
        encoding='utf-8')
    (tmp_path / 'az.cmd').write_text(
        '@echo off\n"{}" "{}" %*\n'.format(sys.executable, receiver), encoding='utf-8')
    monkeypatch.setenv('PATH', str(tmp_path) + os.pathsep + os.environ['PATH'])
    monkeypatch.setattr(repair_utils, '__file__', str(extension_directory / 'repair_utils.py'))
    monkeypatch.chdir(caller_directory)

    with mock.patch.object(repair_utils.importlib.util, 'find_spec',
                           return_value=SimpleNamespace(origin=str(extension_directory / '__init__.py'))):
        stdout, stderr = repair_utils._invoke_run_command(
            driver, 'source-vm', 'source-rg', is_linux,
            additional_custom_scripts=custom_names if custom_scripts else None)

    result = json.loads(stdout)
    assert result['cwd'] == str(extension_directory)
    expected_scripts = ['@' + str(scripts_directory / driver)]
    expected_contents = [driver_content.rstrip(os.linesep)]
    if custom_scripts:
        expected_scripts.extend('@' + str(caller_directory / name) for name in custom_names)
        expected_contents.extend(content.rstrip(os.linesep) for content in custom_contents)
    assert result['scripts'] == expected_scripts
    assert result['contents'] == expected_contents
    assert not marker.exists(), 'The caller directory replaced the trusted launcher'
    assert stderr == ''
    assert Path.cwd() == caller_directory


@mock.patch('azext_vm_repair.repair_utils.subprocess.Popen')
def test_async_command_does_not_wait(mock_popen):
    assert _call_az_command('az version', run_async=True) is None
    mock_popen.return_value.communicate.assert_not_called()


@pytest.mark.skipif(
    os.name != 'nt' or not os.environ.get('VM_REPAIR_TEST_USER_BASE'),
    reason='requires an isolated real pip --user Azure CLI installation')
def test_actual_helper_runs_user_site_only_cli(tmp_path, monkeypatch):
    user_base = Path(os.environ['VM_REPAIR_TEST_USER_BASE'])
    python = Path(sys._base_executable)  # pylint: disable=protected-access
    monkeypatch.setenv('PYTHONUSERBASE', str(user_base))
    monkeypatch.delenv('PYTHONPATH', raising=False)
    monkeypatch.setenv('AZURE_CONFIG_DIR', str(tmp_path / 'config'))
    monkeypatch.setenv('PATH', os.pathsep.join([
        str(user_base / 'Python{}{}'.format(*sys.version_info[:2]) / 'Scripts'), str(python.parent),
        str(Path(os.environ['SystemRoot']) / 'System32'), os.environ['SystemRoot'],
    ]))
    isolated = subprocess.run(
        [str(python), '-I', '-c', 'import azure.cli'], capture_output=True, check=False)
    assert isolated.returncode != 0, 'A global CLI would invalidate the user-site-only proof'
    probe = subprocess.run(
        [str(python), '-c',
         'import azure.cli.core, importlib.metadata, json; '
         'print(json.dumps([azure.cli.core.__file__, importlib.metadata.version("azure-cli")]))'],
        capture_output=True, text=True, check=True)
    location, version = json.loads(probe.stdout)
    assert Path(location).is_relative_to(user_base)
    assert json.loads(_call_az_command('az version -o json'))['azure-cli'] == version
