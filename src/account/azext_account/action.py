import argparse
from knack.util import CLIError


# pylint: disable=protected-access


class AddOwners(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
       return

    def get_action(self, values, option_string):  # pylint: disable=no-self-use
        d = {}
        return d
