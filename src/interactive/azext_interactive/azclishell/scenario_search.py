# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
import threading
import json
from ._azclierror import ScenarioSearchError
from azure.cli.core.style import Style, print_styled_text


class SearchScope(int, Enum):
    All = 1
    Scenario = 2
    Command = 3

    @staticmethod
    def get(scope):
        if not scope:
            return SearchScope.All
        if scope.lower() == "scenario":
            return SearchScope.Scenario
        if scope.lower() == "command":
            return SearchScope.Command
        return SearchScope.All


class MatchRule(int, Enum):
    All = 1
    And = 2
    Or = 3

    @staticmethod
    def get(rule):
        if not rule:
            return MatchRule.All
        if rule.lower() == "and":
            return MatchRule.And
        if rule.lower() == "or":
            return MatchRule.Or
        return MatchRule.All


class SearchThread(threading.Thread):
    def __init__(self, cli_ctx, keywords, search_path, executing_command, on_prepared_callback):
        super().__init__()
        self.cli_ctx = cli_ctx
        self.keywords = keywords
        self.on_prepared_callback = on_prepared_callback
        # maintain a copy of the command history to insert commands executed in the searched scenario
        self.command_history = search_path.get_cmd_history(25)
        if executing_command:
            self.command_history.append(executing_command)
        self.processed_exception = search_path.get_result_summary() if not executing_command else None
        self.result = None
        self.api_version = None

    def run(self, scope=SearchScope.Scenario, match_rule=MatchRule.All) -> None:
        try:
            self.result, self.api_version = online_search(keyword=self.keywords, scope=scope,
                                                          match_rule=match_rule,
                                                          top=self.cli_ctx.config.getint('next', 'num_limit',
                                                                                         fallback=5))
            self.result = search_result_to_scenario_list(self.result)
        except ScenarioSearchError:
            self.result = "Connection Error. Please check your network connection."


# copied from azext_scenario_guide.requests.search_online: https://github.com/Azure/azure-cli-extensions/blob/7365e1ba3cc858b075cbc98aeb4e5ce5c91db745/src/scenario-guide/azext_scenario_guide/requests.py#L13
def online_search(keyword, scope=SearchScope.All, match_rule=MatchRule.All, top=5):
    """Search related e2e scenarios"""
    import requests
    url = "https://cli-recommendation.azurewebsites.net/api/SearchService"
    payload = {
        "keyword": keyword,
        "scope": scope,
        "match_rule": match_rule,
        "top_num": top,
    }
    try:
        response = requests.post(url, json.dumps(payload))
        response.raise_for_status()
    except requests.ConnectionError as e:
        raise ScenarioSearchError(f'Network Error: {e}') from e
    except requests.exceptions.HTTPError as e:
        raise ScenarioSearchError(f'{e}') from e
    except requests.RequestException as e:
        raise ScenarioSearchError(f'Request Error: {e}') from e

    results = []
    if 'data' in response.json():
        results = response.json()['data']
    api_version = None
    if 'api_version' in response.json():
        api_version = response.json()['api_version']
    return results, api_version


# # copied from scenario_guide/azext_scenario_guide.custom._show_search_item: https://github.com/Azure/azure-cli-extensions/blob/7365e1ba3cc858b075cbc98aeb4e5ce5c91db745/src/scenario-guide/azext_scenario_guide/custom.py#L52
def show_search_item(results):
    """
    Display searched scenarios in following format.

    e.g.
    [1] Monitor an App Service app with web server logs (4 Commands)
    Include command: az webapp create
    """

    # To learn the structure of result,
    # visit https://github.com/hackathon-cli-recommendation/cli-recommendation/blob/master/Docs/API_design_doc.md
    for idx, result in enumerate(results):

        print()
        # display idx as "[ 1]" if max index is larger than 9
        idx_str = f"[{idx + 1:2}] " if len(results) >= 10 else f"[{idx + 1:1}] "
        num_notice = f" ({len(result['nextCommandSet'])} Commands)"
        print_styled_text([(Style.ACTION, idx_str), (Style.PRIMARY, result['scenario']), (Style.SECONDARY, num_notice)])

        # Display the command description or related command in the secondary information
        # The specific display strategy are as follows:
        # 1. It will display the description if a matched keyword in description
        # 2. If there's no matched keyword in description, it will display the command with matched keyword instead
        # 3. If there's no matched keyword in commands, it will display the scenario name with matched keyword
        # 4. If there's no matched keyword in scenario name, it will display scenario description anyway
        highlight_desc = next(iter(result.get('highlights', {}).get('description', [])), None)
        if highlight_desc:
            print_styled_text(_match_result_highlight(highlight_desc))
            continue

        # Show the command with the most matching keywords
        highlight_commands = result.get('highlights', {}).get('nextCommandSet/command', [])
        # display the command with most matched keywords
        highlight_command = max(highlight_commands, key=lambda cmd: len(cmd.split("<em>")), default=None)
        if highlight_command:
            include_command_style = [(Style.SECONDARY, "Include command: ")]
            include_command_style.extend(_match_result_highlight(highlight_command))
            print_styled_text(include_command_style)
            continue

        highlight_name = next(iter(result.get('highlights', {}).get('scenario', [])), None)
        if highlight_name:
            print_styled_text(_match_result_highlight(highlight_name))
            continue

        print_styled_text((Style.SECONDARY, result.get('description', "")))

    print()


# copied from scenario_guide/azext_scenario_guide.custom._match_result_highlight: https://github.com/Azure/azure-cli-extensions/blob/7365e1ba3cc858b075cbc98aeb4e5ce5c91db745/src/scenario-guide/azext_scenario_guide/custom.py#L129
def _match_result_highlight(highlight_content: str) -> list:
    """Build `styled_text` from content with `<em></em>` as highlight mark"""
    styled_description = []
    remain = highlight_content
    in_highlight = False
    while remain:
        split_result = remain.split("<em>" if not in_highlight else "</em>", 1)
        content = split_result[0]
        try:
            remain = split_result[1]
        except IndexError:
            remain = None
        styled_description.append((Style.SECONDARY if not in_highlight else Style.WARNING, content))
        in_highlight = not in_highlight
    return styled_description


def search_result_to_scenario_list(search_results):
    """Convert search result to scenario"""
    scenario_list = []
    for raw_scenario in search_results:
        # type 5 means the scenario is from online search
        scenario = {'scenario': raw_scenario['description'], 'nextCommandSet': raw_scenario['commandSet'],
                    'source': raw_scenario['source'], 'type': 5, 'executeIndex': range(len(raw_scenario['commandSet'])),
                    'score': raw_scenario['score'], 'reason': raw_scenario['description'],
                    'highlights': raw_scenario['highlights'], 'description': raw_scenario['description']}
        # update command list: az group list => group list
        commands = []
        for command in scenario['nextCommandSet']:
            command['command'] = command['command'].split(' ', 1)[1]
            commands.append(command)
        scenario['nextCommandSet'] = commands
        scenario_list.append(scenario)
    return scenario_list
