# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,too-many-lines

def load_command_table(self, _):  # pylint: disable=unused-argument
    with self.command_group('nginx deployment configuration'):
        from .custom import ConfigurationUpdate
        self.command_table["nginx deployment configuration update"] = ConfigurationUpdate(loader=self)

    with self.command_group('nginx deployment waf-policy') as g:
        g.command('create', 'create_waf_policy', examples=[
            {'name': 'Create a WAF policy', 
            'text': 'az nginx deployment waf-policy create --name mypolicyname --deployment-name mydeploymentname --resource-group myresourcegroupname --filepath /path/to/my/policy.json --content mycontentfileinbase64encoding'}
        ])

    with self.command_group('nginx deployment waf-policy') as g:
        g.command('update', 'update_waf_policy', examples=[
            {'name': 'Update a WAF policy', 
            'text': 'az nginx deployment waf-policy update --name mypolicyname --deployment-name mydeploymentname --resource-group myresourcegroupname --filepath /path/to/my/policy.json --content mycontentfileinbase64encoding'}
        ])
