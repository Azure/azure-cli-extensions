# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion


class ScenarioAutoSuggest(AutoSuggest):
    """Auto Suggest used in Scenario execution mode"""
    def __init__(self):
        self.cur_sample = ''
        self.cur_command = ''
        self.param_value_map = {}

    def update(self, sample: str):
        """Change command sample that would be suggested to the user"""
        self.cur_sample = sample.split('az ')[-1]
        self.param_value_map = {}
        self.cur_command = self.cur_sample.split('-')[0].strip()
        cur_param = ''
        for part in self.cur_sample.split():
            if part.startswith('-'):
                cur_param = part
                self.param_value_map[cur_param] = ''
            elif cur_param:
                self.param_value_map[cur_param] += ' ' + part
                self.param_value_map[cur_param] = self.param_value_map[cur_param].strip()

    def get_suggestion(self, cli, buffer, document):
        user_input = document.text.rsplit('\n', 1)[-1]
        user_input = re.sub(r'\s+', ' ', user_input)
        # If the user has input the command part of sample, suggest the parameters
        if user_input.startswith(self.cur_command):
            # find user unfinished part of input command
            unfinished = user_input.rsplit(' ', 1)[-1]
            # list of unused parameters in current sample
            unused_param = list(self.param_value_map.keys())
            completed_parts = user_input[-len(unfinished):].strip().split()
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
                suggest = []
                for param in unused_param:
                    if param.startswith(unfinished):
                        suggest.append(param[len(unfinished):])
                        if self.param_value_map[param]:
                            suggest.append(self.param_value_map[param])
                        unused_param.remove(param)
                        break
                if suggest:
                    for param in unused_param:
                        suggest.append(param)
                        if self.param_value_map[param]:
                            suggest.append(self.param_value_map[param])
                    return Suggestion(' '.join(suggest))
            elif unfinished == '':
                if not last_part.startswith('-'):
                    suggest = []
                    for param in unused_param:
                        suggest.append(param)
                        if self.param_value_map[param]:
                            suggest.append(self.param_value_map[param])
                    return Suggestion(' '.join(suggest))
        # If the user hasn't finished the command part, suggest the whole sample
        elif self.cur_command.startswith(user_input):
            return Suggestion(self.cur_sample[len(user_input):])
