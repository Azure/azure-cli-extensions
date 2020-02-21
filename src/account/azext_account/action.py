import argparse
from knack.util import CLIError


# pylint: disable=protected-access


class AddOwners(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        action = self.get_action(values, option_string)

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        try:
            properties = dict(x.split('=', 1) for x in values)
        except ValueError:
            raise CLIError('usage error: {} [KEY=VALUE ...]'.format(option_string))
        d = {}
        return d
