# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long


def load_arguments(self, _):
    import platform
    from azure.cli.core.commands.parameters import tags_type, get_enum_type, get_location_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group
    from ._validators import validate_codespace_name_or_id, validate_plan_name_or_id, validate_secret_filter_list

    with self.argument_context('codespace') as c:
        c.argument('tags', tags_type)
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('plan_name', options_list=['--plan', '-p'], help="Name or ID of the Codespace plan",
                   validator=validate_plan_name_or_id)
        c.argument('codespace_name', options_list=['--name', '-n'], help='Name of the Codespace.')
        c.argument('codespace_id', options_list=['--id'], help='Id of the Codespace.',
                   validator=validate_codespace_name_or_id)
        c.argument('sku_name', options_list=['--instance-type'], help='Instance Type')
        c.argument('autoshutdown_delay', options_list=['--suspend-after'],
                   arg_type=get_enum_type(['5', '30', '120']),
                   help="Automatically suspend the inactive Codespace after this many minutes.")

    with self.argument_context('codespace plan') as c:
        c.argument('plan_name', options_list=['--name', '-n'], help="Name of the Codespace plan", id_part='name')
        c.argument('subnet_id', arg_group="Network", options_list=['--subnet'],
                   help="Resource ID of an existing subnet. If specified, all Codespaces in this plan will be created in this subnet. The subnet must be in the same region as the plan.")
        c.argument('default_autoshutdown_delay', arg_group="Plan Default", options_list=['--default-suspend-after'],
                   arg_type=get_enum_type(['5', '30', '120']),
                   help="Default minutes Codespaces in this plan should suspend after.")
        c.argument('default_sku_name', arg_group="Plan Default", options_list=['--default-instance-type'], help="Default Instance Type for Codespaces in this plan.")

    with self.argument_context('codespace create') as c:
        c.argument('friendly_name', options_list=['--name', '-n'], help='Name of the Codespace.')
        c.argument('git_repo', arg_group="Git", help="Url of the git repository we'll clone into the Codespace")
        c.argument('git_user_name', arg_group="Git", help="Git username. For example, the output of `git config user.name`")
        c.argument('git_user_email', arg_group="Git", help="Git user email. For example, the output of `git config user.email`")
        c.argument('dotfiles_repo', arg_group="Dotfiles", help="Url of dotfiles git repository. More info: https://aka.ms/vso-docs/reference/personalizing")
        c.argument('dotfiles_path', arg_group="Dotfiles", help="Path where you expect your dotfiles repository to be cloned into the Codespace.")
        c.argument('dotfiles_command', arg_group="Dotfiles", help="The command we'll run after cloning your dotfiles repository.")

    with self.argument_context('codespace list') as c:
        c.argument('list_all', options_list=['--all'], action='store_true',
                   help="Include the Codespaces of other users. You may not have access to connect or modify these other Codespaces.")

    with self.argument_context('codespace open') as c:
        c.argument('do_not_prompt', options_list=['--yes', '-y'], action='store_true',
                   help='Do not prompt for confirmation.')

    with self.argument_context('codespace location show') as c:
        c.argument('location_name', options_list=['--name', '-n'], help='Name of the region.')

    # Hidden arguments that should largely be used by the dev team
    with self.argument_context('codespace') as c:
        c.argument('config_rp_api_version', options_list=['--rp'], help="Resource Provider API version to use.")
        c.argument('config_service_domain', options_list=['--domain'], help="Service domain to use.")
        c.argument('config_clear', options_list=['--clear'], action='store_true',
                   help='Clear current configuration to return to defaults.')

    with self.argument_context('codespace secret') as c:
        quotes = '""' if platform.system() == 'Windows' else "''"
        quote_text = 'Use {} to clear existing filters.'.format(quotes)
        c.argument('secret_filters', arg_group="Secret", options_list=['--filters'],
                   validator=validate_secret_filter_list,
                   help=f"space-separated filters: type=value [type=value ...]. {quote_text} Allowed types: GitRepo, CodespaceName.",
                   nargs='*')
        c.argument('secret_name', arg_group="Secret", options_list=['--name', '-n'], help="Name of the secret.")
        c.argument('secret_value', arg_group="Secret", options_list=['--value'], help="Value of the secret.")
        c.argument('secret_note', arg_group="Secret", options_list=['--note'], help="Note for the secret.")
        c.argument('secret_id', options_list=['--id'], help="Id of the secret.")
