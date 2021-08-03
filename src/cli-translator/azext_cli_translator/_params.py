# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):

    with self.argument_context('cli-translator arm translate') as c:
        c.argument('template_path', options_list=['--template'], help='The local path or url of template.json file')
        c.argument('parameters_path', options_list=['--parameters'], help='The local path or url of parameters.json file')
        c.argument('target_subscription', options_list=['--target-subscription'], help='The target subscription id. If omit, the current subscription id will be used')
