# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk.preparers import ResourceGroupPreparer

class AKSCustomResourceGroupPreparer(ResourceGroupPreparer):
    """Custom resource group preparer that defaults the length of the resource group to 14.
    This avoids hitting validation issues due to the length of the resource id
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        kwargs['random_name_length'] = 14
        super(AKSCustomResourceGroupPreparer, self).__init__(*args, **kwargs)
