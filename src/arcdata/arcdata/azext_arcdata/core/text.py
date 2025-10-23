# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------


class Text(object):
    @staticmethod
    def clear():
        import sys
        import colorama

        try:
            colorama.init()
            sys.stderr.write("\x1b[2J\x1b[H")
        finally:
            print(colorama.Style.RESET_ALL)

    @staticmethod
    def green(message):
        from colorama import Fore, Style, init

        try:
            init()
            print("{}{}{}".format(Fore.GREEN, message, Style.RESET_ALL))
        finally:
            print(Style.RESET_ALL)

    @staticmethod
    def yellow(message):
        from colorama import Fore, Style, init

        try:
            init()
            print("{}{}{}".format(Fore.YELLOW, message, Style.RESET_ALL))
        finally:
            print(Style.RESET_ALL)

    @staticmethod
    def red(message):
        from colorama import Fore, Style, init

        try:
            init()
            print("{}{}{}".format(Fore.RED, message, Style.RESET_ALL))
        finally:
            print(Style.RESET_ALL)

    @staticmethod
    def warning(message):
        Text.yellow(message)

    # NOTE: Add more colors when needed
