# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import platform
import subprocess


class AzCopy(object):
    system_executable_path = {
        'Darwin': ['azcopy_darwin_amd64_10.0.4', 'azcopy'],
        'Linux': ['azcopy_linux_amd64_10.0.4', 'azcopy'],
        'Windows': ['azcopy_windows_amd64_10.0.4', 'azcopy.exe']
    }

    def __init__(self):
        self.system = platform.system()
        curr_path = os.path.dirname(os.path.realpath(__file__))
        self.executable = os.path.join(curr_path, *AzCopy.system_executable_path[self.system])

    def run_command(self, args):
        args = [self.executable] + args
        subprocess.call(args)
