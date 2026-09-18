# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):

    with self.argument_context('monitor health-models arrange') as c:
        c.argument('resource_group', options_list=['--resource-group', '-g'], required=True,
                   help='Name of resource group. You can configure the default group using '
                        '`az configure --defaults group=<name>`.')
        c.argument('health_model_name', options_list=['--health-model-name', '--name', '-n'], required=True,
                   help='Name of the health model resource to arrange.')
        c.argument('entity_name', options_list=['--entity-name'],
                   help='Name of an entity to scope the arrange to that entity\'s subtree - itself plus '
                        'every descendant reachable via parent-to-child relationships - instead of the '
                        'whole model. Cross-boundary relationships to entities outside the subtree are '
                        'ignored, the arranged subtree is anchored so this entity keeps its own existing '
                        'canvas position, and every entity outside the subtree is left completely '
                        'unchanged. Omit to arrange every entity in the health model (default).')
        c.argument('priority', options_list=['--priority'], nargs='+',
                   help='Space-separated entity names to place left to right in this order. '
                        'Best effort, not a guarantee: the layout applies it at each level below '
                        'the listed entities\' closest shared parent, along each entity\'s '
                        'shortest path down from it, and leaves the rest to its own layout rules. '
                        'Only the relative order is set, so entities you did not list keep their '
                        'place and may still sit between the listed ones. Quote names that '
                        'contain spaces. Omit to let the layout choose the order (default).')
        c.argument('yes', options_list=['--yes', '-y'], action='store_true',
                   help='Do not prompt for confirmation.')
        c.argument('node_width', type=float,
                   help='Assumed entity node width (in canvas units) used for layout spacing. '
                        'Defaults to the Azure Portal Health Model Designer\'s exact, fixed '
                        'entity-card width (200 canvas units), verified from its '
                        '`.react-flow__node` CSS rule and independently matched by its initial '
                        'measured seed; override for a different rendered width.')
        c.argument('node_height', type=float,
                   help='Assumed entity node height (in canvas units) used for layout spacing. '
                        'Defaults to the Azure Portal Health Model Designer\'s initial measured '
                        'seed for every V2/V3 entity card (81 canvas units, from '
                        '`ModelActionsSlice.ts`\'s `measured: { width: 200, height: 81 }`). '
                        'Unlike width, no CSS rule pins entity-card height: this is a '
                        'Portal-sourced seed, and ReactFlow may later replace it with a '
                        'runtime-measured value once the card\'s actual content is rendered, '
                        'which the headless CLI cannot obtain - override it if you know your '
                        'model\'s actual rendered height.')
        c.argument('node_sep', type=float,
                   help='Horizontal space between entities in the same rank, in canvas units '
                        '(matches the portal Arrange default of 50).')
        c.argument('rank_sep', type=float,
                   help='Vertical space between ranks, in canvas units (matches the portal '
                        'Arrange default of 100).')
