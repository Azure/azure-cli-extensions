# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):
    from azure.cli.core.commands.parameters import get_three_state_flag

    with self.argument_context('acr cache') as c:
        c.argument('registry_name', options_list=['--registry', '-r'], help='The name of the container registry. It should be specified in lower case. You can configure the default registry name using `az configure --defaults acr=<registry name>`')
        c.argument('name', options_list=['--name', '-n'], help='The name of the cache rule.')
        c.argument('cred_set', options_list=['--cred-set', '-c'], help='The name of the credential set.')
        c.argument('source_repo', options_list=['--source-repo', '-s'], help="The full source repository path such as 'docker.io/library/ubuntu'.")
        c.argument('target_repo', options_list=['--target-repo', '-t'], help="The target repository namespace such as 'ubuntu'.")
        c.argument('remove_cred_set', action="store_true", help='Optional boolean indicating whether to remove the credential set from the cache rule. False by default.')
        c.argument('sync', arg_type=get_three_state_flag(), help='Optional boolean indicating whether to enable artifact sync on the cache rule. False by default.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')
        c.argument('dry_run', help='Do not create the cache rule but instead return the tags that will be synced. Can only be used if \'sync\' is true.', action='store_true')
        c.argument('starts_with', help='Only sync the tags that start with the specified string.')
        c.argument('ends_with', help='Only sync the tags that end with the specified string.')
        c.argument('contains', help='Only sync the tags that contain the specified string.')
        c.argument('image', help='The name of the tag you want to sync immediately. Can only be used if artifact sync is enabled and the tag is within any specified tag filter.')
