# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):

    with self.argument_context('cli-translator arm translate') as c:
        c.argument('template_path', options_list=['--template'], help='The path of template.json file')
        c.argument('parameters_path', options_list=['--parameters'], help='The path of parameters.json file')
