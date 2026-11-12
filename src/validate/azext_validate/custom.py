# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

_POWERSHELL_SUFFIXES = ('.ps1', '.psm1')


def validate_commands(cmd, command_texts=None, script_text=None,  # pylint: disable=too-many-arguments,unused-argument
                      script_file=None, shell=None, offline=False, output_file=None):
    from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, RequiredArgumentMissingError
    from azext_validate._validator import Validator
    given = [name for name, value in (('--command', command_texts), ('--script', script_text),
                                      ('--file', script_file)) if value is not None]
    if len(given) > 1:
        raise MutuallyExclusiveArgumentError('Use only one of --command, --script and --file.')
    if not given:
        raise RequiredArgumentMissingError('Provide --command, --script or --file.')
    if script_file is not None:
        script_text = _read_script(script_file)
        if shell is None and os.path.splitext(script_file)[1].lower() in _POWERSHELL_SUFFIXES:
            shell = 'powershell'
    shell = shell or 'bash'
    validator = Validator(offline=offline)
    if command_texts is not None:
        doc = validator.check_commands(command_texts, shell)
    else:
        doc = validator.check_script(script_text, shell)
    if output_file:
        _write_json(output_file, doc)
    return doc


def _read_script(path):
    from azure.cli.core.azclierror import FileOperationError
    import codecs
    try:
        with open(os.path.expanduser(path), 'rb') as f:
            raw = f.read()
        # Windows PowerShell 5.1 writes UTF-16 with a byte-order mark; everything else is read as UTF-8.
        if raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            return raw.decode('utf-16')
        return raw.decode('utf-8-sig')
    except (OSError, UnicodeDecodeError) as ex:
        raise FileOperationError('Could not read the --file script: {}.'.format(
            getattr(ex, 'strerror', None) or type(ex).__name__))


def _write_json(path, doc):
    import json
    from azure.cli.core.azclierror import FileOperationError
    try:
        with open(os.path.expanduser(path), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, indent=2)
            f.write('\n')
    except OSError as ex:
        raise FileOperationError('Could not write the --output-file: {}.'.format(ex.strerror or type(ex).__name__))
