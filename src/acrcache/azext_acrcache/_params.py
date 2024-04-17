# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):
    from azure.cli.core.commands.parameters import get_three_state_flag

    with self.argument_context('acr cache') as c:
        c.argument('registry_name', options_list=['--registry', '-r'])
        c.argument('name', options_list=['--name', '-n'], help='The name of the cache rule.')
        c.argument('cred_set', options_list=['--cred-set', '-c'], help='The name of the credential set.')
        c.argument('source_repo', options_list=['--source-repo', '-s'], help="The full source repository path such as 'docker.io/library/ubuntu'.")
        c.argument('target_repo', options_list=['--target-repo', '-t'], help="The target repository namespace such as 'ubuntu'.")
        c.argument('remove_cred_set', action="store_true", help='Optional boolean indicating whether to remove the credential set from the cache rule. False by default.')
        c.argument('sync', arg_type=get_three_state_flag(), help='Optional boolean indicating whether to enable artifact sync on the cache rule. False by default.')
