# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

from azext_cloudservice.aaz.latest.cloud_service.update_domain._walk_update_domain import \
    WalkUpdateDomain as _WalkUpdateDomain


class UpdateDomainWalkUpdateDomain(_WalkUpdateDomain):
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.no_wait._registered = False
        return args_schema
