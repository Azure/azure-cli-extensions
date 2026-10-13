# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

from azure.cli.core.aaz import AAZAnyTypeArg, register_command
from azext_cloudservice.aaz.latest.cloud_service._create import Create as _Create
from azext_cloudservice.aaz.latest.cloud_service._list import List as _List


@register_command(
    "cloud-service list",
    is_experimental=True,
)
class CloudServiceList(_List):
    """List all cloud services in a resource group.

    :example: List cloud services in a resource group.
        az cloud-service list --resource-group MyResourceGroup
    """

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.resource_group._required = True
        return args_schema


@register_command(
    "cloud-service list-all",
    is_experimental=True,
)
class CloudServiceListAll(_List):
    """List all cloud services in the subscription.

    :example: List all cloud services in the current subscription.
        az cloud-service list-all
    """

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.resource_group._registered = False
        return args_schema


class CloudServiceCreate(_Create):
    """Library-only backend of the custom `cloud-service create` command.

    Extension `settings` and `protectedSettings` may be plain strings (for example the XML of the RDP
    extension), which the generated dictionary schema cannot carry. They are passed through the hidden
    `extension_raw_properties` argument and merged into the request body.
    """

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.extension_raw_properties = AAZAnyTypeArg()
        args_schema.extension_raw_properties._registered = False
        return args_schema

    class CloudServicesCreateOrUpdate(_Create.CloudServicesCreateOrUpdate):

        @property
        def content(self):
            body = super().content
            raw = self.ctx.args.extension_raw_properties.to_serialized_data()
            if raw:
                extensions = body['properties']['extensionProfile']['extensions']
                for extension, extra in zip(extensions, raw):
                    props = extension.setdefault('properties', {})
                    if 'settings' in extra:
                        props['settings'] = extra['settings']
                    if 'protected_settings' in extra:
                        props['protectedSettings'] = extra['protected_settings']
            return body
