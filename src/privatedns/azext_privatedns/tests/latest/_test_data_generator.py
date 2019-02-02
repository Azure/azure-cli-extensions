# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

# pylint: disable=line-too-long
def GeneratePrivateZoneName(self):
    self.kwargs['zone'] = self.create_random_name("clitest.privatedns.com", length=35)


def GeneratePrivateZoneArmId(self):
    regexSubscription = '[0-9a-f]{{8}}-[0-9a-f]{{4}}-[1-5][0-9a-f]{{3}}-[89ab][0-9a-f]{{3}}-[0-9a-f]{{12}}'
    return "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/privateDnsZones/{2}".format(regexSubscription, self.kwargs['rg'], self.kwargs['zone'])


def GenerateTags(self):
    tagKey = self.create_random_name("tagKey", length=15)
    tagVal = self.create_random_name("tagVal", length=15)
    self.kwargs['tags'] = "{0}={1}".format(tagKey, tagVal)
    return tagKey, tagVal
