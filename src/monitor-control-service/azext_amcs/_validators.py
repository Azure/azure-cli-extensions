# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
from azure.cli.core.azclierror import InvalidArgumentValueError


def validate_association_name_with_endpoint(namespace):
    if namespace.endpoint_id:
        if namespace.association_name != "configurationAccessEndpoint":
            raise InvalidArgumentValueError("Association name for resource to endpoint "
                                            "must be configurationAccessEndpoint")
