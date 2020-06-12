# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):
    workspace_name_type = CLIArgumentType(options_list=['--workspace-name', '-w'], help='Name of the Quantum Workspace. You can configure the default workspace using `az quantum workspace set`.', id_part=None, required=False)
    program_args = CLIArgumentType(nargs='*', help='List of arguments expected by the Q# operation specified as --name=value after `--`.')
    target_id = CLIArgumentType(options_list=['--target-id', '-t'], help='Target id.')
    project = CLIArgumentType(help='The location of the Q# project to submit. Defaults to current folder.')
    job_name = CLIArgumentType(help='A friendly name to give to this execution of the program.')
    shots = CLIArgumentType(help='The number of times to execute the Q# program on the given target.')
    no_build = CLIArgumentType(help='If specified, the Q# program is not built before submitting.')

    with self.argument_context('quantum workspace') as c:
        c.argument('workspace_name', workspace_name_type)

    with self.argument_context('quantum target') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('target_id', options_list=['--target-id', '-t'], help='Target id.')

    with self.argument_context('quantum job') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('job_id', options_list=['--job-id', '-id'], help='Job id.')
        c.argument('target_id', target_id)
        c.argument('project', project)
        c.argument('job_name', job_name)
        c.argument('shots', shots)
        c.argument('no_build', no_build)

    with self.argument_context('quantum job submit') as c:
        c.positional('program_args', program_args)

    with self.argument_context('quantum execute') as c:
        c.argument('workspace_name', workspace_name_type)
        c.argument('target_id', target_id)
        c.argument('project', project)
        c.argument('job_name', job_name)
        c.argument('shots', shots)
        c.argument('no_build', no_build)
        c.positional('program_args', program_args)
