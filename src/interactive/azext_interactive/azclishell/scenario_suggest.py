import re

from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion


class ScenarioAutoSuggest(AutoSuggest):
    def __init__(self):
        self.cur_sample = ''
        self.cur_command = ''
        self.param_value_map = {}

    def update(self, sample: str):
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
        text = document.text.rsplit('\n', 1)[-1]
        text = re.sub(r'\s+', ' ', text)
        if text.startswith(self.cur_command):
            unfinished = text.rsplit(' ', 1)[-1]
            used_param = []
            unused_param = list(self.param_value_map.keys())
            completed_parts = text[-len(unfinished):].strip().split()
            last_part = completed_parts[-1]

            def try_remove(container, item):
                if item in container:
                    container.remove(item)

            for part in completed_parts:
                if part.startswith('-'):
                    used_param.append(part)
                    try_remove(unused_param, part)
                    if part in ['-g', '--resource-group']:
                        try_remove(unused_param, '--resource-group')
                        try_remove(unused_param, '-g')
                    if part in ['-n', '--name']:
                        try_remove(unused_param, '--name')
                        try_remove(unused_param, '-n')

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
        elif self.cur_command.startswith(text):
            return Suggestion(self.cur_sample[len(text):])
