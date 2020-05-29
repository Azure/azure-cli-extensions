# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from msrestazure.tools import is_valid_resource_id
from azure.cli.core.commands.parameters import get_resources_in_subscription  # pylint: disable=unused-import


def validate_storage_account(namespace):
    from msrestazure.tools import parse_resource_id
    if is_valid_resource_id(namespace.storage_account):
        parsed_storage = parse_resource_id(namespace.storage_account)
        storage_name = parsed_storage['resource_name']
        namespace.storage_account = storage_name


def validate_statement_language(namespace):
    statement_language = {
        'spark': 'spark',
        'scala': 'spark',
        'pypark': 'pyspark',
        'python': 'pyspark',
        'sparkdotnet': 'sparkdotnet',
        'csharp': 'sparkdotnet',
        'sql': 'sql'
    }
    namespace.language = statement_language.get(namespace.language.lower())
