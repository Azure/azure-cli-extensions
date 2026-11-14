from azext_arcdata.sqlarc.common.help_formats import (
    help_format_example,
    help_format_examples_3,
    help_format_short
)

HELP_BACKUPS_POLICY = help_format_short.format(
    type="group",
    short="Manage backups policy",
)

HELP_BACKUPS_POLICY_SET = help_format_examples_3.format(
    type="command",
    short="Set your backups policy",
    exName="Ex 1 - Enabling a backups policy with a custom backups policy",
    example="{example}",
    exName2="Ex 2 - Enabling a backups policy with the default backups policy",
    example2="{example2}",
    exName3="Ex 3 - Disabling a backups policy",
    example3="{example3}",
)
HELP_BACKUPS_POLICY_SHOW = help_format_example.format(
    type="command",
    short="See your current backups policy",
    exName="Ex 1 - Displaying a backups policy",
    example="{example}",
)
HELP_BACKUPS_POLICY_DELETE = help_format_example.format(
    type="command",
    short="Delete your current backups policy",
    exName="Ex 1 - Deleting a backups policy",
    example="{example}",
)
