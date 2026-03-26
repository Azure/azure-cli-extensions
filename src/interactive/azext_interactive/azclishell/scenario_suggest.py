# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from collections import defaultdict

from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion


class ScenarioAutoSuggest(AutoSuggest):
    """Auto Suggest used in Scenario execution mode"""

    def __init__(self):
        self.cur_sample = ''
        self.cur_command = ''
        # param_sample_value_map is the dictionary that has `key` with command params and `value` with <sample_value>
        self.param_sample_value_map = {}
        # when user input a value of a parameter,value will be stored in this map. Will be suggested in the scenario
        # customized_cached_param_map is the dictionary that has `key` with <sample_value> of scenario commands or some `special global params` and `value` with the value that customer has entered
        self.customized_cached_param_map = {}
        # Define some special global parameters which matches the param instead of sample value.
        # Tend to improve the suggestion rate when scenario is not strictly stylized
        self.special_global_param_map = {'-g': ['-g', '--resource-group'],
                                         '--resource-group': ['-g', '--resource-group'],
                                         '-s': ['-s', '--subscription'], '--subscription': ['-s', '--subscription'],
                                         '-l': ['-l', '--location'], '--location': ['-l', '--location']}

    def update(self, sample: str):
        """Change command sample that would be suggested to the user"""
        # The sample should not start with 'az '
        self.cur_sample = sample.split('az ')[-1]
        # Find parameters used in sample and its value
        self.param_sample_value_map = defaultdict(lambda: None)
        # Find the command part of sample
        self.cur_command = self.cur_sample.split('-')[0].strip()
        cur_param = ''
        for part in self.cur_sample.split():
            if part.startswith('-'):
                cur_param = part
                self.param_sample_value_map[cur_param] = ''
            elif cur_param:
                self.param_sample_value_map[cur_param] += ' ' + part
                self.param_sample_value_map[cur_param] = self.param_sample_value_map[cur_param].strip()

    def update_customized_cached_param_map(self, command_text: str):
        """Update the value of a parameter in the customized parameter value map"""
        # remove the 'az ' part of command
        command_text = command_text.split('az ')[-1]
        cached_sample_value = ''
        special_global_param_list = None
        for part in command_text.split():
            if part.startswith('-'):
                # if the parameter is a special global parameter, use the parameter itself as the key
                if part in self.special_global_param_map.keys():
                    # Because '--g' and '--resource-group' are the same parameter, we need to both support in the customized map
                    special_global_param_list = self.special_global_param_map[part]
                    for param in special_global_param_list:
                        self.customized_cached_param_map[param] = ''
                    cached_sample_value = ''
                else:
                    cached_sample_value = self.param_sample_value_map[part]
                    self.customized_cached_param_map[cached_sample_value] = ''
                    special_global_param_list = None
            elif cached_sample_value:
                self.customized_cached_param_map[cached_sample_value] += ' ' + part
                self.customized_cached_param_map[cached_sample_value] = self.customized_cached_param_map[
                    cached_sample_value].strip()
            # Because '--g' and '--resource-group' are the same parameter, we need to both support in the customized map
            elif special_global_param_list:
                for param in special_global_param_list:
                    self.customized_cached_param_map[param] += ' ' + part
                    self.customized_cached_param_map[param] = self.customized_cached_param_map[param].strip()

    def get_suggestion(self, cli, buffer, document):
        user_input = document.text.rsplit('\n', 1)[-1]
        # format all the space in user's input to ' '
        user_input = re.sub(r'\s+', ' ', user_input)
        # If the user has input the command part of sample, suggest the parameters
        if user_input.startswith(self.cur_command):
            # find user unfinished part of input command
            # rsplit(' ', 1) will split the string from right to left with max split 1
            unfinished = user_input.rsplit(' ', 1)[-1]
            # list of unused parameters in current sample
            unused_param = list(self.param_sample_value_map.keys())
            # same as unfinished
            completed_parts = user_input.rsplit(' ', 1)[0].strip().split()
            # last completed part of user's input
            last_part = completed_parts[-1]

            def try_remove(container, item):
                if item in container:
                    container.remove(item)

            # Remove all used parameter from unused_param
            for part in completed_parts:
                if part.startswith('-'):
                    try_remove(unused_param, part)
                    if part in ['-g', '--resource-group']:
                        try_remove(unused_param, '--resource-group')
                        try_remove(unused_param, '-g')
                    if part in ['-n', '--name']:
                        try_remove(unused_param, '--name')
                        try_remove(unused_param, '-n')

            # If user is inputting a parameter, suggest the parameter and the rest part
            if unfinished.startswith('-'):
                # Find the parameter user is inputting and suggest the unfinished part
                for param in unused_param:
                    if param.startswith(unfinished):
                        unused_param.remove(param)
                        return Suggestion(param[len(unfinished):])
            elif unfinished == '':
                # if last part is a not a parameter or the last part is a bool parameter and the value is empty, suggest the first unused parameter
                if (not last_part.startswith('-')) or self.param_sample_value_map[last_part] == '':
                    for param in unused_param:
                        # the param is a special global parameter, such as '--location' and not given a customized value
                        if param in self.special_global_param_map.keys() and self.param_sample_value_map[param].startswith('<'):
                            cached_param = param
                        else:
                            # cached_param is either the sample values in scenarios, such as <RESOURCEGROUPNAME> or some special global params, such as '--location'
                            cached_param = self.param_sample_value_map[param]
                        if cached_param:
                            if cached_param in self.customized_cached_param_map.keys():
                                value = self.customized_cached_param_map[cached_param]
                            elif cached_param.startswith('<') or cached_param.startswith('-'):
                                value = ''
                            else:
                                value = cached_param
                            return Suggestion(' '.join([param, value]))
                        else:
                            return Suggestion(param)

        # If the user hasn't finished the command part, suggest the whole command
        elif self.cur_command.startswith(user_input):
            return Suggestion(self.cur_sample[len(user_input):])
