# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.aaz import register_command

from .aaz.latest.interconnect.block import (Create as _InterconnectBlockCreate, Delete as _InterconnectBlockDelete,
                                            List as _InterconnectBlockList, Show as _InterconnectBlockShow,
                                            Update as _InterconnectBlockUpdate)


@register_command(
    'interconnect-block create',
)
class InterconnectBlockCreate(_InterconnectBlockCreate):
    """Create an Interconnect Block. When updating an Interconnect Block, only tags and sku-capacity may be modified.

    :example: Creates a new Interconnect Block resource.
        az interconnect-block create --name training-icb-001 --resource-group ai-training-rg --location eastus --zones 1 --sku-name Standard_ND128isr_GB300_v6 --sku-capacity 36 --interconnect-group-id "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/network-rg/providers/Microsoft.Network/interconnectGroups/training-ig" --tags Environment=Production Workload=AI-Training CostCenter=ML-Engineering
    """


@register_command(
    'interconnect-block delete',
    confirmation='Are you sure you want to perform this operation?',
)
class InterconnectBlockDelete(_InterconnectBlockDelete):
    """Delete an Interconnect Block.

    :example: Delete an Interconnect Block with confirmation.
        az interconnect-block delete --name training-icb-001 --resource-group ai-training-rg

    :example: Delete an Interconnect Block without confirmation.
        az interconnect-block delete --name training-icb-001 --resource-group ai-training-rg --yes
    """


@register_command(
    'interconnect-block list',
)
class InterconnectBlockList(_InterconnectBlockList):
    """List Interconnect Blocks.

    :example: List Interconnect Blocks all in subscription.
        az interconnect-block list

    :example: List Interconnect Blocks in a resource group.
        az interconnect-block list --resource-group ai-training-rg

    :example: List Interconnect Blocks and filter by capacity.
        az interconnect-block list --resource-group ai-training-rg --query "[?sku.capacity>=36]"
    """


@register_command(
    'interconnect-block show',
)
class InterconnectBlockShow(_InterconnectBlockShow):
    """Get information about an Interconnect Block.

    :example: Get an Interconnect Block.
        az interconnect-block show --name training-icb-001 --resource-group ai-training-rg

    :example: Get an Interconnect Block with instance view (includes runtime details).
        az interconnect-block show --name training-icb-001 --resource-group ai-training-rg --expand instanceView
    """


@register_command(
    'interconnect-block update',
)
class InterconnectBlockUpdate(_InterconnectBlockUpdate):
    """Update an Interconnect Block. Only tags and sku-capacity may be modified.

    :example: Update the capacity of an Interconnect Block.
        az interconnect-block update --name training-icb-001 --resource-group ai-training-rg --sku-capacity 54

    :example: Update the tags of an Interconnect Block.
        az interconnect-block update --name training-icb-001 --resource-group ai-training-rg --tags Environment=Production Capacity=54-nodes LastScaled=$(date +%Y-%m-%d)

    :example: Update the scale of an Interconnect Block with no-wait.
        az interconnect-block update --name training-icb-001 --resource-group ai-training-rg --sku-capacity 72 --no-wait
    """
