# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access

import argparse
from knack.util import CLIError


class AddReturnAddress(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.return_address = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'recipient-name':
                d['recipient_name'] = v
            elif kl == 'street-address1':
                d['street_address1'] = v
            elif kl == 'street-address2':
                d['street_address2'] = v
            elif kl == 'city':
                d['city'] = v
            elif kl == 'state-or-province':
                d['state_or_province'] = v
            elif kl == 'postal-code':
                d['postal_code'] = v
            elif kl == 'country-or-region':
                d['country_or_region'] = v
            elif kl == 'phone':
                d['phone'] = v
            elif kl == 'email':
                d['email'] = v
        return d


class AddReturnShipping(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.return_shipping = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'carrier-name':
                d['carrier_name'] = v
            elif kl == 'carrier-account-number':
                d['carrier_account_number'] = v
        return d


class AddShippingInformation(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.shipping_information = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'recipient-name':
                d['recipient_name'] = v
            elif kl == 'street-address1':
                d['street_address1'] = v
            elif kl == 'street-address2':
                d['street_address2'] = v
            elif kl == 'city':
                d['city'] = v
            elif kl == 'state-or-province':
                d['state_or_province'] = v
            elif kl == 'postal-code':
                d['postal_code'] = v
            elif kl == 'country-or-region':
                d['country_or_region'] = v
            elif kl == 'phone':
                d['phone'] = v
        return d


class AddDeliveryPackage(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.delivery_package = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'carrier-name':
                d['carrier_name'] = v
            elif kl == 'tracking-number':
                d['tracking_number'] = v
            elif kl == 'drive-count':
                d['drive_count'] = v
            elif kl == 'ship-date':
                d['ship_date'] = v
        return d


class AddReturnPackage(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.return_package = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'carrier-name':
                d['carrier_name'] = v
            elif kl == 'tracking-number':
                d['tracking_number'] = v
            elif kl == 'drive-count':
                d['drive_count'] = v
            elif kl == 'ship-date':
                d['ship_date'] = v
        return d


class AddDriveList(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddDriveList, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'drive-id':
                d['drive_id'] = v
            elif kl == 'bit-locker-key':
                d['bit_locker_key'] = v
            elif kl == 'manifest-file':
                d['manifest_file'] = v
            elif kl == 'manifest-hash':
                d['manifest_hash'] = v
            elif kl == 'drive-header-hash':
                d['drive_header_hash'] = v
            elif kl == 'state':
                d['state'] = v
            elif kl == 'copy-status':
                d['copy_status'] = v
            elif kl == 'percent-complete':
                d['percent_complete'] = v
            elif kl == 'verbose-log-uri':
                d['verbose_log_uri'] = v
            elif kl == 'error-log-uri':
                d['error_log_uri'] = v
            elif kl == 'manifest-uri':
                d['manifest_uri'] = v
            elif kl == 'bytes-succeeded':
                d['bytes_succeeded'] = v
        return d


class AddExport(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        namespace.export = action

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'blob-listblob-path':
                d['blob_listblob_path'] = v
            elif kl == 'blob-path':
                d['blob_path'] = v
            elif kl == 'blob-path-prefix':
                d['blob_path_prefix'] = v
        return d
