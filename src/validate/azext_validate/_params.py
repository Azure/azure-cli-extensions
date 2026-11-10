# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def load_arguments(self, _):
    from azure.cli.core.commands.parameters import get_enum_type
    with self.argument_context('validate') as c:
        # Destinations must not be `command`: core sets namespace.command to the command name and
        # sends it to telemetry.
        c.argument('command_texts', options_list=['--command', '-c'], nargs='+',
                   help='One or more az commands to check, each as a single argument.')
        c.argument('script_text', options_list=['--script', '-s'],
                   help='The text of a Bash or PowerShell script; every az command in it is checked.')
        c.argument('script_file', options_list=['--file'],
                   help='Path of a Bash or PowerShell script file; every az command in it is checked. A file '
                        'ending in .ps1 or .psm1 is read as PowerShell, any other file as Bash, unless --shell '
                        'is given.')
        c.argument('shell', get_enum_type(['bash', 'powershell']),
                   help='Shell syntax of the input. Default: bash, or powershell for a --file ending in .ps1 or '
                        '.psm1.')
        c.argument('offline', action='store_true',
                   help='Never download published command metadata; use cached metadata only.')
        c.argument('output_file', options_list=['--output-file'],
                   help='Also write the result as JSON (UTF-8) to this file. The normal output is unchanged.')
