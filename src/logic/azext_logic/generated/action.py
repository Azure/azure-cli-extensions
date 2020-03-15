# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from knack.util import CLIError


# pylint: disable=protected-access


class AddWorkflow(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddWorkflow, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'provisioning_state':
                d['provisioning_state'] = v
            elif kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'state':
                d['state'] = v
            elif kl == 'version':
                d['version'] = v
            elif kl == 'access_endpoint':
                d['access_endpoint'] = v
            elif kl == 'endpoints_configuration':
                d['endpoints_configuration'] = v
            elif kl == 'sku':
                d['sku'] = v
            elif kl == 'integration_account':
                d['integration_account'] = v
            elif kl == 'integration_service_environment':
                d['integration_service_environment'] = v
            elif kl == 'definition':
                d['definition'] = v
            elif kl == 'parameters':
                d['parameters'] = v
        return d


class AddParameters(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddParameters, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'target_schema_version':
                d['target_schema_version'] = v
        return d


class AddListCallbackUrl(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddListCallbackUrl, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'not_after':
                d['not_after'] = v
            elif kl == 'key_type':
                d['key_type'] = v
        return d


class AddMove(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddMove, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'provisioning_state':
                d['provisioning_state'] = v
            elif kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'state':
                d['state'] = v
            elif kl == 'version':
                d['version'] = v
            elif kl == 'access_endpoint':
                d['access_endpoint'] = v
            elif kl == 'endpoints_configuration':
                d['endpoints_configuration'] = v
            elif kl == 'sku':
                d['sku'] = v
            elif kl == 'integration_account':
                d['integration_account'] = v
            elif kl == 'integration_service_environment':
                d['integration_service_environment'] = v
            elif kl == 'definition':
                d['definition'] = v
            elif kl == 'parameters':
                d['parameters'] = v
        return d


class AddKeyType(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddKeyType, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'key_type':
                d['key_type'] = v
        return d


class AddValidate(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddValidate, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'provisioning_state':
                d['provisioning_state'] = v
            elif kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'state':
                d['state'] = v
            elif kl == 'version':
                d['version'] = v
            elif kl == 'access_endpoint':
                d['access_endpoint'] = v
            elif kl == 'endpoints_configuration':
                d['endpoints_configuration'] = v
            elif kl == 'sku':
                d['sku'] = v
            elif kl == 'integration_account':
                d['integration_account'] = v
            elif kl == 'integration_service_environment':
                d['integration_service_environment'] = v
            elif kl == 'definition':
                d['definition'] = v
            elif kl == 'parameters':
                d['parameters'] = v
        return d


class AddSetState(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddSetState, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'source':
                d['source'] = v
        return d


class AddIntegrationAccount(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddIntegrationAccount, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'sku':
                d['sku'] = v
            elif kl == 'integration_service_environment':
                d['integration_service_environment'] = v
            elif kl == 'state':
                d['state'] = v
        return d


class AddListKeyVaultKeys(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddListKeyVaultKeys, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'key_vault':
                d['key_vault'] = v
            elif kl == 'skip_token':
                d['skip_token'] = v
        return d


class AddLogTrackingEvents(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddLogTrackingEvents, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'source_type':
                d['source_type'] = v
            elif kl == 'track_events_options':
                d['track_events_options'] = v
            elif kl == 'events':
                d['events'] = v
        return d


class AddRegenerateAccessKey(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddRegenerateAccessKey, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'key_type':
                d['key_type'] = v
        return d


class AddAssemblyArtifact(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddAssemblyArtifact, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'properties':
                d['properties'] = v
        return d


class AddBatchConfiguration(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddBatchConfiguration, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'properties':
                d['properties'] = v
        return d


class AddSchema(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddSchema, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'schema_type':
                d['schema_type'] = v
            elif kl == 'target_namespace':
                d['target_namespace'] = v
            elif kl == 'document_name':
                d['document_name'] = v
            elif kl == 'file_name':
                d['file_name'] = v
            elif kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'metadata':
                d['metadata'] = v
            elif kl == 'content':
                d['content'] = v
            elif kl == 'content_type':
                d['content_type'] = v
            elif kl == 'content_link':
                d['content_link'] = v
        return d


class AddListContentCallbackUrl(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddListContentCallbackUrl, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'not_after':
                d['not_after'] = v
            elif kl == 'key_type':
                d['key_type'] = v
        return d


class AddMap(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddMap, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'map_type':
                d['map_type'] = v
            elif kl == 'parameters_schema':
                d['parameters_schema'] = v
            elif kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'content':
                d['content'] = v
            elif kl == 'content_type':
                d['content_type'] = v
            elif kl == 'content_link':
                d['content_link'] = v
            elif kl == 'metadata':
                d['metadata'] = v
        return d


class AddPartner(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddPartner, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'partner_type':
                d['partner_type'] = v
            elif kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'metadata':
                d['metadata'] = v
            elif kl == 'content':
                d['content'] = v
        return d


class AddAgreement(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddAgreement, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'metadata':
                d['metadata'] = v
            elif kl == 'agreement_type':
                d['agreement_type'] = v
            elif kl == 'host_partner':
                d['host_partner'] = v
            elif kl == 'guest_partner':
                d['guest_partner'] = v
            elif kl == 'host_identity':
                d['host_identity'] = v
            elif kl == 'guest_identity':
                d['guest_identity'] = v
            elif kl == 'content':
                d['content'] = v
        return d


class AddCertificate(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddCertificate, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'metadata':
                d['metadata'] = v
            elif kl == 'key':
                d['key'] = v
            elif kl == 'public_certificate':
                d['public_certificate'] = v
        return d


class AddSession(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddSession, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'created_time':
                d['created_time'] = v
            elif kl == 'changed_time':
                d['changed_time'] = v
            elif kl == 'content':
                d['content'] = v
        return d


class AddIntegrationServiceEnvironment(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)
        super(AddIntegrationServiceEnvironment, self).__call__(parser, namespace, action, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        for k in properties:
            kl = k.lower()
            v = properties[k]
            if kl == 'properties':
                d['properties'] = v
            elif kl == 'sku':
                d['sku'] = v
        return d
