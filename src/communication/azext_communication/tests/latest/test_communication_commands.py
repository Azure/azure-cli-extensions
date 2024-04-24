# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json
from .recording_processors import BodyReplacerProcessor, URIIdentityReplacer

from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest,
    live_only
)


class CommunicationClientTest(ScenarioTest):
    
    def __init__(self, *args, **kwargs):
        super(CommunicationClientTest, self).__init__(recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["createdBy", "lastModifiedBy", "identity", "dataLocation"])
        ], *args, **kwargs)
        
    @live_only()
    @ResourceGroupPreparer(name_prefix='cli_test_communication', location='eastus')
    def test_communication_identity(self):
        self.kwargs.update({
            'resource_name': self.create_random_name('resource', 15),
            'managed_identity_name': self.create_random_name('identity', 15)
        })

        self.kwargs['managed_identity_id'] = self.cmd('identity create -n managedIdentity -g {rg}').get_output_in_json()['id']

        self.cmd('communication create -n {resource_name} -g {rg} --location global --data-location unitedstates --mi-system-assigned', checks=[
            self.check('identity.type', 'SystemAssigned')
        ])

        self.cmd('communication create -n {resource_name} -g {rg} --location global --data-location unitedstates')
        self.cmd('communication identity assign -n {resource_name} -g {rg} --system-assigned', checks=[
            self.check('type', 'SystemAssigned')
        ])

        self.cmd('communication identity assign -n {resource_name} -g {rg} --system-assigned --user-assigned {managed_identity_id}', checks={
            self.check('type', "SystemAssigned,UserAssigned")
        })

        self.cmd('communication identity remove -n {resource_name} -g {rg} --system-assigned', checks={
            self.check('type', "UserAssigned")
        })
