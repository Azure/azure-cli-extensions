# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from knack.util import CLIError


# pylint: disable=protected-access
class PeeringAddDirectConnections(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(PeeringAddDirectConnections, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'bandwidthinmbps':
                d['bandwidthInMbps'] = v
            elif kl == 'sessionaddressprovider':
                d['sessionAddressProvider'] = v
            elif kl == 'useforpeeringservice':
                d['useForPeeringService'] = v
            elif kl == 'peeringdbfacilityid':
                d['peeringDBFacilityId'] = v
            elif kl == 'sessionprefixv4':
                d.setdefault('bgpSession', {})['sessionPrefixV4'] = v
            elif kl == 'sessionprefixv6':
                d.setdefault('bgpSession', {})['sessionPrefixV6'] = v
            elif kl == 'maxprefixesadvertisedv4':
                d.setdefault('bgpSession', {})['maxPrefixesAdvertisedV4'] = v
            elif kl == 'maxprefixesadvertisedv6':
                d.setdefault('bgpSession', {})['maxPrefixesAdvertisedV6'] = v
            elif kl == 'md5authenticationkey':
                d.setdefault('bgpSession', {})['md5AuthenticationKey'] = v
            elif kl == 'connectionidentifier':
                d['connectionIdentifier'] = v
            else:
                raise CLIError('usage error: {} is invalid'.format(k))
        return d


# pylint: disable=protected-access
class PeeringAddExchangeConnections(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(PeeringAddExchangeConnections, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'bandwidthinmbps':
                d['bandwidthInMbps'] = v
            elif kl == 'sessionaddressprovider':
                d['sessionAddressProvider'] = v
            elif kl == 'useforpeeringservice':
                d['useForPeeringService'] = v
            elif kl == 'peeringdbfacilityid':
                d['peeringDBFacilityId'] = v
            elif kl == 'sessionprefixv4':
                d.setdefault('bgpSession', {})['sessionPrefixV4'] = v
            elif kl == 'sessionprefixv6':
                d.setdefault('bgpSession', {})['sessionPrefixV6'] = v
            elif kl == 'maxprefixesadvertisedv4':
                d.setdefault('bgpSession', {})['maxPrefixesAdvertisedV4'] = v
            elif kl == 'maxprefixesadvertisedv6':
                d.setdefault('bgpSession', {})['maxPrefixesAdvertisedV6'] = v
            elif kl == 'md5authenticationkey':
                d.setdefault('bgpSession', {})['md5AuthenticationKey'] = v
            elif kl == 'connectionidentifier':
                d['connectionIdentifier'] = v
            else:
                raise CLIError('usage error: {} is invalid'.format(k))
        return d
