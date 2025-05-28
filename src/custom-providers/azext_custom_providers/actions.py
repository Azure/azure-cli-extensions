# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
import argparse
from knack.util import CLIError


class ActionAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        from azext_custom_providers.vendored_sdks.customproviders.models import CustomRPActionRouteDefinition as model
        action = get_object(values, option_string, model)
        super(ActionAddAction, self).__call__(parser, namespace, action, option_string)


class ResourceTypeAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        from azext_custom_providers.vendored_sdks.customproviders.models import CustomRPResourceTypeRouteDefinition as model
        resource_type = get_object(values, option_string, model)
        super(ResourceTypeAddAction, self).__call__(parser, namespace, resource_type, option_string)


class ValidationAddAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        from azext_custom_providers.vendored_sdks.customproviders.models import CustomRPValidations as model
        validation = get_object(values, option_string, model)
        super(ValidationAddAction, self).__call__(parser, namespace, validation, option_string)


def get_object(values, option_string, model):
    kwargs = {}
    for item in values:
        try:
            key, value = item.split('=', 1)
            kwargs[key] = value
        except ValueError:
            raise CLIError('usage error: {} KEY=VALUE [KEY=VALUE ...]'.format(option_string))
    return model(**kwargs)
