from azext_arcdata.sqlarc.common.help_formats import (
    help_format_example,
    help_format_examples_2,
    help_format_examples_3,
    help_format_examples_4,
    help_format_short
)

HELP_HOST = help_format_short.format(
    type="group",
    short="Manage extension level properties",
)
HELP_HOST_FEATURE_FLAG = help_format_short.format(
    type="group",
    short="Manage extension level feature flags",
)
HELP_HOST_FEATURE_FLAG_SET = help_format_examples_4.format(
    type="command",
    short="Set feature flag",
    exName="Ex 1 - Enabling a feature flag",
    example=(
        "az sql server-arc extension feature-flag set --name FeatureName "
        "--enable true --resource-group MyResourceGroup "
        "--machine-name MyArcServerName"
    ),
    exName2="Ex 2 - Enabling a feature flag using arc sql instance resource name",
    example2=(
        "az sql server-arc extension feature-flag set --name FeatureName "
        "--enable true --resource-group MyResourceGroup "
        "--sql-server-arc-name MyArcSqlInstanceName"
    ),
    exName3="Ex 3 - Disabling a feature flag",
    example3=(
        "az sql server-arc extension feature-flag set --name FeatureName "
        "--enable false --resource-group MyResourceGroup "
        "--machine-name MyArcServerName"
    ),
    exName4="Ex 4 - Disabling a feature flag using arc sql instance resource name",
    example4=(
        "az sql server-arc extension feature-flag set --name FeatureName "
        "--enable false --resource-group MyResourceGroup "
        "--sql-server-arc-name MyArcSqlInstanceName"
    ),
)
HELP_HOST_FEATURE_FLAG_DELETE = help_format_examples_2.format(
    type="command",
    short="Delete feature flag",
    exName="Ex 1 - Deleting a feature flag",
    example=(
        "az sql server-arc extension feature-flag delete --name FeatureName "
        "--resource-group MyResourceGroup --machine-name MyArcServerName"
    ),
    exName2="Ex 2 - Deleting a feature flag using arc sql instance resource name",
    example2=(
        "az sql server-arc extension feature-flag delete --name FeatureName "
        "--resource-group MyResourceGroup "
        "--sql-server-arc-name MyArcSqlInstanceName"
    ),
)
HELP_HOST_FEATURE_FLAG_SHOW = help_format_examples_4.format(
    type="command",
    short="Show feature flag",
    exName="Ex 1 - Displaying feature flag for a feature",
    example=(
        "az sql server-arc extension feature-flag show --name FeatureName "
        "--resource-group MyResourceGroup --machine-name MyArcServerName"
    ),
    exName2="Ex 2 - Displaying feature flag for a feature using arc sql instance resource name",
    example2=(
        "az sql server-arc extension feature-flag show --name FeatureName "
        "--resource-group MyResourceGroup "
        "--sql-server-arc-name MyArcSqlInstanceName"
    ),
    exName3="Ex 3 - Displaying all feature flags",
    example3=(
        "az sql server-arc extension feature-flag show "
        "--resource-group MyResourceGroup --machine-name MyArcServerName"
    ),
    exName4="Ex 4 - Displaying all feature flags using arc sql instance resource name",
    example4=(
        "az sql server-arc extension feature-flag show "
        "--resource-group MyResourceGroup "
        "--sql-server-arc-name MyArcSqlInstanceName"
    ),
)
HELP_HOST_SHOW = help_format_examples_2.format(
    type="command",
    short="Show host properties",
    exName="Ex 1 - Displaying host level properties",
    example=(
        "az sql server-arc extension show --resource-group MyResourceGroup "
        "--machine-name MyArcServerName"
    ),
    exName2="Ex 2 - Displaying host level properties using Arc Sql instance resource name",
    example2=(
        "az sql server-arc extension show --resource-group MyResourceGroup "
        "--sql-server-arc-name MyArcSqlInstanceName"
    ),
)
HELP_HOST_SET = help_format_examples_3.format(
    type="command",
    short="Update common host properties",
    exName="Ex 1 - Updating LicenseType value",
    example=(
        "az sql server-arc extension set --resource-group MyResourceGroup "
        "--machine-name MyArcServerName --license-type LicenseTypeValue"
    ),
    exName2="Ex 2 - Updating status of extended security updates",
    example2=(
        "az sql server-arc extension set --resource-group MyResourceGroup "
        "--machine-name MyArcServerName --esu-enabled True"
    ),
    exName3="Ex 2 - Updating list of excluded sql instances",
    example3=(
        'az sql server-arc extension set --resource-group MyResourceGroup '
        '--machine-name MyArcServerName '
        '--skip-instances "InstanceName1, InstanceName2"'
    ),
)
HELP_AVAILABILITY_GROUP = help_format_short.format(
    type="group",
    short="Manage availability groups",
)
HELP_AVAILABILITY_GROUP_FAILOVER = help_format_example.format(
    type="command",
    short="Request manual failover of an availability group",
    exName="Ex 1 - Request manual failover of an availability group",
    example="{example}",
)
HELP_AVAILABILITY_GROUP_CREATE = help_format_example.format(
    type="command",
    short="Create an availability group",
    exName="Ex 1 - Create an availability group",
    example="{example}",
)

HELP_NAME_ARC_SERVER = "Name of the connected machine"

HELP_RG_ARC_SERVER = (
    "Name of the resource group where the connected machine is located"
)
