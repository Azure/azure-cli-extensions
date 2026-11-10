# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._show import Show as _PrivateLinkResourceShow


class PrivateLinkResourceShow(_PrivateLinkResourceShow):
    AZ_HELP = {
        **_PrivateLinkResourceShow.AZ_HELP,
        'examples': [{
            'name': 'Get a HorizonDB private link resource',
            'text': 'az horizondb cluster private-link-resource show --resource-group example-resource-group '
                    '--cluster-name example-cluster --resource-name example-resource',
        }],
    }

    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        options = ['-n', '--name', '--resource-name']
        args_schema.group_name._options = options  # pylint: disable=protected-access
        args_schema.group_name._help['name'] = ' '.join(options)  # pylint: disable=protected-access
        return args_schema
