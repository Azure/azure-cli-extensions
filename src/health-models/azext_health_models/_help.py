# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['monitor health-models arrange'] = """
    type: command
    short-summary: Automatically arrange a health model's entities on the canvas.
    long-summary: |
        Experimental. Recomputes each entity's `canvasPosition` using a layered,
        top-to-bottom graph layout based on the Azure Portal Health Model Designer, then
        persists the new positions immediately. Results may differ from the portal's Arrange
        feature, and the CLI has no undo or revert command.
    examples:
        - name: Arrange all entities in a health model using the portal's default spacing.
          text: |
            az monitor health-models arrange --resource-group MyResourceGroup --health-model-name MyHealthModel
        - name: Arrange with custom horizontal/vertical spacing between entities and ranks.
          text: |
            az monitor health-models arrange -g MyResourceGroup -n MyHealthModel --node-sep 80 --rank-sep 150
        - name: Arrange only an entity's subtree (itself plus its descendants), keeping its own position.
          text: |
            az monitor health-models arrange -g MyResourceGroup -n MyHealthModel --entity-name MyRootEntity
"""
