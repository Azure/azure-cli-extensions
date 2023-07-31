# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import unicode_literals, print_function

import datetime
import json
import math
import os
import re
import subprocess
import sys
import time

from threading import Thread
from six.moves import configparser
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core._profile import _SUBSCRIPTION_NAME, Profile
from azure.cli.core._session import ACCOUNT, CONFIG, SESSION
from azure.cli.core.api import get_config_dir
from azure.cli.core.util import handle_exception
# stylized output
from azure.cli.core.style import print_styled_text, Style
# progress bar
from azure.cli.core.commands.progress import IndeterminateProgressBar

# pylint: disable=import-error
import jmespath
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import Always
from prompt_toolkit.history import FileHistory
from prompt_toolkit.interface import Application, CommandLineInterface
from prompt_toolkit.shortcuts import create_eventloop
# pylint: enable=import-error

from . import VERSION
from .az_completer import AzCompleter
from .az_lexer import get_az_lexer, ExampleLexer, ToolbarLexer, ScenarioLexer
from .configuration import Configuration, SELECT_SYMBOL
from .frequency_heuristic import DISPLAY_TIME, frequency_heuristic
from .gather_commands import add_new_lines, GatherCommands
from .key_bindings import InteractiveKeyBindings
from .layout import LayoutManager
from .progress import progress_view
from . import telemetry
from .recommendation import Recommender, _show_details_for_e2e_scenario, gen_command_in_scenario
from .scenario_suggest import ScenarioAutoSuggest
from .threads import LoadCommandTableThread
from .util import get_window_dim, parse_quotes, get_os_clear_screen_word, get_yes_or_no_option, select_option
from .scenario_search import SearchThread, show_search_item

NOTIFICATIONS = ""
PART_SCREEN_EXAMPLE = .3
START_TIME = datetime.datetime.utcnow()
CLEAR_WORD = get_os_clear_screen_word()
_ENV_ADDITIONAL_USER_AGENT = 'AZURE_HTTP_USER_AGENT'

logger = get_logger(__name__)


def space_toolbar(settings_items, empty_space):
    """ formats the toolbar """
    counter = 0
    for part in settings_items:
        counter += len(part)

    if len(settings_items) == 1:
        spacing = ''
    else:
        # Calculate the length of space between items
        spacing_len = (len(empty_space) - len(NOTIFICATIONS) - counter) // (len(settings_items) - 1)
        if spacing_len < 0:
            # Not display the first item of settings if the space is not enough
            return space_toolbar(settings_items[1:], empty_space)
        # Sample spacing string from `empty_space`
        spacing = empty_space[:spacing_len]

    settings = spacing.join(settings_items)

    empty_space = empty_space[len(NOTIFICATIONS) + len(settings) + 1:]
    return settings, empty_space


def whether_continue_module_loading():
    """ whether continue loading the command table, return True/False """
    step_msg = [(Style.PRIMARY, "\nDo you want to continue loading?"), (Style.SECONDARY, "(y/n)\n"),
                (Style.PRIMARY,
                 "If you choose n, it will start the shell immediately,"
                 "but it may cause unknown errors due to incomplete module loading.\n")]
    continue_loading = get_yes_or_no_option(step_msg)
    return continue_loading


# pylint: disable=too-many-instance-attributes
class AzInteractiveShell(object):

    def __init__(self, cli_ctx, style=None, completer=None,
                 lexer=None, history=None,
                 input_custom=sys.stdin, output_custom=None,
                 user_feedback=False, intermediate_sleep=.25, final_sleep=4):

        from .color_styles import style_factory

        self.cli_ctx = cli_ctx
        self.config = Configuration(cli_ctx.config, style=style)
        self.config.set_style(style)
        self.style = style_factory(self.config.get_style())
        try:
            gathered_commands = GatherCommands(self.config)
            self.completer = completer or AzCompleter(self, gathered_commands)
            self.completer.initialize_command_table_attributes()
            self.lexer = lexer or get_az_lexer(gathered_commands)
        except IOError:  # if there is no cache
            self.completer = AzCompleter(self, None)
            self.lexer = None
        self.history = history or FileHistory(os.path.join(self.config.get_config_dir(), self.config.get_history()))
        if os.environ.get(_ENV_ADDITIONAL_USER_AGENT):
            os.environ[_ENV_ADDITIONAL_USER_AGENT] += ' AZURECLISHELL/' + VERSION
        else:
            os.environ[_ENV_ADDITIONAL_USER_AGENT] = 'AZURECLISHELL/' + VERSION

        # OH WHAT FUN TO FIGURE OUT WHAT THESE ARE!
        self._cli = None
        self.layout = None
        self.description_docs = u''
        self.param_docs = u''
        self.example_docs = u''
        self.last = None
        self.last_exit_code = 0
        self.user_feedback = user_feedback
        self.input = input_custom
        self.output = output_custom
        self.config_default = ""
        self.default_command = ""
        self.threads = []
        self.curr_thread = None
        self.spin_val = -1
        self.intermediate_sleep = intermediate_sleep
        self.final_sleep = final_sleep
        self.command_table_thread = None
        self.recommender = Recommender(
            self.cli_ctx, os.path.join(self.config.get_config_dir(), self.config.get_recommend_path()))
        self.recommender.set_on_prepared_callback(self.redraw_scenario_recommendation_info)

        # try to consolidate state information here...
        # Used by key bindings and layout
        self.example_page = 1
        self.is_prompting = False
        self.is_example_repl = False
        self.is_showing_default = False
        self.is_symbols = True

    def __call__(self):

        if self.cli_ctx.data["az_interactive_active"]:
            logger.warning("You're in the interactive shell already.")
            return

        if self.config.BOOLEAN_STATES[self.config.config.get('DEFAULT', 'firsttime')]:
            self.config.firsttime()

        if not self.config.has_feedback() and frequency_heuristic(self):
            print("\nAny comments or concerns? You can use the \'feedback\' command!" +
                  " We would greatly appreciate it.\n")
        if self.cli_ctx.config.getboolean("interactive", "enable_recommender", fallback=True):
            print(
                "\nA new Recommender is added which can make the completion ability more intelligent and provide the scenario completion!\n"
                "If you want to disable this feature, you can use 'az config set interactive.enable_recommender=False' to disable it.\n")

        self.cli_ctx.data["az_interactive_active"] = True
        self.run()
        self.cli_ctx.data["az_interactive_active"] = False

    @property
    def cli(self):
        """ Makes the interface or refreshes it """
        if self._cli is None:
            self._cli = self.create_interface()
        return self._cli

    def handle_cd(self, cmd):
        """changes dir """
        if len(cmd) != 2:
            print("Invalid syntax: cd path", file=self.output)
            return
        path = os.path.expandvars(os.path.expanduser(cmd[1]))
        try:
            os.chdir(path)
        except OSError as ex:
            print("cd: %s\n" % ex, file=self.output)

    def on_input_timeout(self, cli):
        """
        brings up the metadata for the command if there is a valid command already typed
        """
        document = cli.current_buffer.document
        text = document.text

        text = text.replace('az ', '')
        if self.default_command:
            text = self.default_command + ' ' + text

        param_info, example = self.generate_help_text()

        self.param_docs = u'{}'.format(param_info)
        self.example_docs = u'{}'.format(example)

        self._update_default_info()

        cli.buffers['description'].reset(
            initial_document=Document(self.description_docs, cursor_position=0))
        cli.buffers['parameter'].reset(
            initial_document=Document(self.param_docs))
        cli.buffers['examples'].reset(
            initial_document=Document(self.example_docs))
        cli.buffers['default_values'].reset(
            initial_document=Document(
                u'{}'.format(self.config_default if self.config_default else 'No Default Values')))
        self._update_toolbar()
        cli.request_redraw()

    def restart_completer(self):
        command_info = GatherCommands(self.config)
        if not self.completer:
            self.completer.start(command_info)
        self.completer.initialize_command_table_attributes()
        if not self.lexer:
            self.lexer = get_az_lexer(command_info)
        self._cli = None

    def redraw_scenario_recommendation_info(self):
        scenarios = self.recommender.get_scenarios() or []
        scenarios_rec_info = "Scenario Recommendation: "
        for idx, s in enumerate(scenarios):
            idx_display = f'[{idx + 1}]'
            scenario_desc = f'{s["scenario"]}'
            command_size = f'{len(s["nextCommandSet"])} Commands'
            scenarios_rec_info += f'\n {idx_display} {scenario_desc} ({command_size})'
        self.cli.buffers['scenarios'].reset(
            initial_document=Document(u'{}'.format(scenarios_rec_info)))
        self.cli.request_redraw()

    def _space_examples(self, list_examples, rows, section_value):
        """ makes the example text """
        examples_with_index = []

        for i, _ in list(enumerate(list_examples)):
            if len(list_examples[i]) > 1:
                examples_with_index.append("[" + str(i + 1) + "] " + list_examples[i][0] + "\n" +
                                           list_examples[i][1] + "\n")

        example = "".join(exam for exam in examples_with_index)
        num_newline = example.count('\n')

        page_number = ''
        if num_newline > rows * PART_SCREEN_EXAMPLE and rows > PART_SCREEN_EXAMPLE * 10:
            len_of_excerpt = math.floor(float(rows) * PART_SCREEN_EXAMPLE)

            group = example.split('\n')
            end = int(section_value * len_of_excerpt)
            begin = int((section_value - 1) * len_of_excerpt)

            if end < num_newline:
                example = '\n'.join(group[begin:end]) + "\n"
            else:
                # default chops top off
                example = '\n'.join(group[begin:]) + "\n"
                while ((section_value - 1) * len_of_excerpt) > num_newline:
                    self.example_page -= 1
            page_number = '\n' + str(section_value) + "/" + str(int(math.ceil(num_newline / len_of_excerpt)))

        return example + page_number + ' CTRL+Y (^) CTRL+N (v)'

    def _update_toolbar(self):
        cli = self.cli
        _, cols = get_window_dim()
        # The rightmost column in window doesn't seem to be used
        cols = int(cols) - 1

        empty_space = " " * cols

        delta = datetime.datetime.utcnow() - START_TIME
        if self.user_feedback and delta.seconds < DISPLAY_TIME:
            toolbar = [
                'Try out the \'feedback\' command',
                'If refreshed disappear in: {}'.format(str(DISPLAY_TIME - delta.seconds))]
        elif self.command_table_thread.is_alive():
            toolbar = [
                'Loading...',
                'Hit [enter] to refresh'
            ]
        else:
            toolbar = self._toolbar_info()

        toolbar, empty_space = space_toolbar(toolbar, empty_space)
        cli.buffers['bottom_toolbar'].reset(
            initial_document=Document(u'{}{}{}'.format(NOTIFICATIONS, toolbar, empty_space)))
        # Reset the cursor pos so that the bottom toolbar doesn't appear offset
        cli.buffers['bottom_toolbar'].cursor_position = 0

    def _toolbar_info(self):
        sub_name = ""
        try:
            profile = Profile(cli_ctx=self.cli_ctx)
            sub_name = profile.get_subscription()[_SUBSCRIPTION_NAME]
        except CLIError:
            pass

        curr_cloud = "Cloud: {}".format(self.cli_ctx.cloud.name)

        tool_val = 'Subscription: {}'.format(sub_name) if sub_name else curr_cloud

        settings_items = [
            "[F1]Layout",
            "[F2]Defaults",
            "[F3]Keys",
            "[Space]Predict",
            "[Ctrl+C]Clear Screen",
            "[Ctrl+D]Quit",
            tool_val
        ]
        return settings_items

    def generate_help_text(self):
        """ generates the help text based on commands typed """
        param_descrip = example = ""
        self.description_docs = u''

        rows, _ = get_window_dim()
        rows = int(rows)

        param_args = self.completer.leftover_args
        last_word = self.completer.unfinished_word
        command = self.completer.current_command
        new_command = ' '.join([command, last_word]).strip()

        if not self.completer.complete_command and new_command in self.completer.command_description:
            command = new_command

        if not command and self.recommender.enabled:
            # display hint to promote CLI recommendation when the user doesn't have any input
            self.description_docs = u'Try [Space] or `next` to get Command Recommendation'
        elif self.completer and command in self.completer.command_description:
            # Display the help message of the command when the user has input
            self.description_docs = u'{}'.format(self.completer.command_description[command])

        # get parameter help if full command
        if self.completer and command in self.completer.command_param_info:
            param = param_args[-1] if param_args else ''
            param = last_word if last_word.startswith('-') else param

            if param in self.completer.command_param_info[command] and self.completer.has_description(
                    command + " " + param):
                param_descrip = ''.join([
                    param, ":", '\n', self.completer.param_description.get(command + " " + param, '')])

            if command in self.completer.command_examples:
                string_example = []
                for example in self.completer.command_examples[command]:
                    for part in example:
                        string_example.append(part)
                ''.join(string_example)
                example = self._space_examples(
                    self.completer.command_examples[command], rows, self.example_page)

        return param_descrip, example

    def _update_default_info(self):
        try:
            defaults_section = self.cli_ctx.config.defaults_section_name
            self.config_default = ""
            if hasattr(self.cli_ctx.config, 'config_parser'):
                options = self.cli_ctx.config.config_parser.options(defaults_section)
            else:
                return
            for opt in options:
                self.config_default += opt + ": " + self.cli_ctx.config.get(defaults_section, opt) + "  "
        except configparser.NoSectionError:
            self.config_default = ""

    def create_application(self, full_layout=True, auto_suggest=AutoSuggestFromHistory(),
                           prompt_prefix='', toolbar_hint=''):
        """ makes the application object and the buffers """
        layout_manager = LayoutManager(self, prompt_prefix, toolbar_hint)
        if full_layout:
            layout = layout_manager.create_layout(ExampleLexer, ToolbarLexer, ScenarioLexer)
        else:
            layout = layout_manager.create_tutorial_layout()

        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            'description': Buffer(is_multiline=True, read_only=True),
            'parameter': Buffer(is_multiline=True, read_only=True),
            'examples': Buffer(is_multiline=True, read_only=True),
            'bottom_toolbar': Buffer(is_multiline=True),
            'example_line': Buffer(is_multiline=True),
            'default_values': Buffer(),
            'symbols': Buffer(),
            'progress': Buffer(is_multiline=False),
            'scenarios': Buffer(is_multiline=True, read_only=True),
        }

        writing_buffer = Buffer(
            history=self.history,
            auto_suggest=auto_suggest,
            enable_history_search=True,
            completer=self.completer,
            complete_while_typing=Always()
        )

        return Application(
            mouse_support=False,
            style=self.style,
            buffer=writing_buffer,
            on_input_timeout=self.on_input_timeout,
            key_bindings_registry=InteractiveKeyBindings(self).registry,
            layout=layout,
            buffers=buffers,
        )

    def create_interface(self):
        """ instantiates the interface """
        return CommandLineInterface(
            application=self.create_application(),
            eventloop=create_eventloop())

    def set_prompt(self, prompt_command="", position=0):
        """ writes the prompt line """
        self.description_docs = u'{}'.format(prompt_command)
        self.cli.current_buffer.reset(
            initial_document=Document(
                self.description_docs,
                cursor_position=position))
        self.cli.request_redraw()

    def set_scope(self, value):
        """ narrows the scopes the commands """
        if self.default_command:
            self.default_command += ' ' + value
        else:
            self.default_command += value
        return value

    def handle_example(self, text, continue_flag):
        """ parses for the tutorial """
        # Get the cmd part and index part from input
        # e.g. webapp create :: 1  => `cmd = 'webapp create'` `selected_option='1'`
        cmd = text.partition(SELECT_SYMBOL['example'])[0].rstrip()
        selected_option = text.partition(SELECT_SYMBOL['example'])[2].strip()
        example = ""
        try:
            selected_option = int(selected_option) - 1
        except ValueError:
            print("An Integer should follow the colon", file=self.output)
            return ""
        if cmd in self.completer.command_examples:
            if 0 <= selected_option < len(self.completer.command_examples[cmd]):
                example = self.completer.command_examples[cmd][selected_option][1]
                example = example.replace('\n', '')
            else:
                print('Invalid example number', file=self.output)
                return '', True

        example = example.replace('az', '')

        starting_index = None
        counter = 0
        example_no_fill = ""
        flag_fill = True
        for word in example.split():
            if flag_fill:
                example_no_fill += word + " "
            if word.startswith('-'):
                example_no_fill += word + " "
                if not starting_index:
                    starting_index = counter
                flag_fill = False
            counter += 1

        return self.example_repl(example_no_fill, example, starting_index, continue_flag)

    def example_repl(self, text, example, start_index, continue_flag):
        """ REPL(Read-Eval-Print Loop) for interactive tutorials """
        if start_index:
            start_index = start_index + 1
            cmd = ' '.join(text.split()[:start_index])
            example_cli = CommandLineInterface(
                application=self.create_application(
                    full_layout=False,
                    prompt_prefix='(tutorial) ',
                    toolbar_hint='In Tutorial Mode: Press [Enter] after typing each part'
                ),
                eventloop=create_eventloop())
            # Scenario recommendation cannot be enabled in tutorial mode
            self.completer.enable_scenario_recommender(False)
            example_cli.buffers['example_line'].reset(
                initial_document=Document(u'{}\n'.format(
                    add_new_lines(example)))
            )
            while start_index < len(text.split()):
                if self.default_command:
                    cmd = cmd.replace(self.default_command + ' ', '')
                example_cli.buffers[DEFAULT_BUFFER].reset(
                    initial_document=Document(
                        u'{}'.format(cmd),
                        cursor_position=len(cmd)))
                example_cli.request_redraw()
                answer = example_cli.run()
                if not answer:
                    return "", True
                answer = answer.text
                if answer.strip('\n') == cmd.strip('\n'):
                    continue
                else:
                    if len(answer.split()) > 1:
                        start_index += 1
                        cmd += " " + answer.split()[-1] + " " + \
                               u' '.join(text.split()[start_index:start_index + 1])
            self.completer.enable_scenario_recommender(True)
            example_cli.exit()
            del example_cli
        else:
            cmd = text

        return cmd, continue_flag

    def handle_scenario(self, text):
        """ parses for the scenario recommendation """
        # Get the index part from input
        # e.g. :: 1  => `selected_option='1'`
        selected_option = text.partition(SELECT_SYMBOL['example'])[2].strip()
        try:
            selected_option = int(selected_option) - 1
        except ValueError:
            print("An Integer should follow the colon", file=self.output)
            return
        if 0 <= selected_option < len(self.recommender.get_scenarios() or []):
            scenario = self.recommender.get_scenarios()[selected_option]
            self.recommender.feedback_scenario(selected_option, scenario)
        else:
            print('Invalid example number', file=self.output)
            return
        self.scenario_repl(scenario)

    def scenario_repl(self, scenario):
        """ REPL(Read-Eval-Print Loop) for interactive scenario execution """
        auto_suggest = ScenarioAutoSuggest()
        example_cli = CommandLineInterface(
            application=self.create_application(
                full_layout=False,
                auto_suggest=auto_suggest,
                prompt_prefix='(scenario) ',
                toolbar_hint='In Scenario Mode: Press [Enter] to execute commands   [Ctrl+C]Skip  [Ctrl+D]Quit'
            ),
            eventloop=create_eventloop())
        # When users execute the recommended command combination of scenario,
        # they no longer need the scenario recommendation
        self.completer.enable_scenario_recommender(False)

        _show_details_for_e2e_scenario(scenario, file=self.output)

        example_cli.buffers['example_line'].reset(
            initial_document=Document(scenario.get('reason') or scenario.get('scenario') or 'Running a E2E Scenario. ')
        )
        quit_scenario = False
        all_skipped = True
        # give notice to users that they can skip a command or quit the scenario
        print_styled_text([(Style.WARNING, '\nYou can use CTRL C to skip a command of the scenario, '
                                           'and CTRL D to exit the scenario.')])
        for nx_cmd, sample in gen_command_in_scenario(scenario, file=self.output):
            auto_suggest.update(sample)
            retry = True
            while retry:
                # reset and put the command in write buffer
                example_cli.buffers[DEFAULT_BUFFER].reset(
                    initial_document=Document(
                        u'{}'.format(nx_cmd['command']),
                        cursor_position=len(nx_cmd['command'])))
                example_cli.request_redraw()
                try:
                    # wait for user's input
                    document = example_cli.run()
                except (KeyboardInterrupt, ValueError):
                    # CTRL C
                    print_styled_text([(Style.WARNING, 'Skipped')])
                    break
                if not document:
                    # CTRL D
                    quit_scenario = True
                    break
                if not document.text:
                    continue
                cmd = document.text
                # Update customized parameter value map
                auto_suggest.update_customized_cached_param_map(cmd)
                self.history.append(cmd)
                # Prefetch the next recommendation using current executing command
                self.recommender.update_executing(cmd, feedback=False)
                telemetry.start()
                self.cli_execute(cmd)
                if self.last_exit_code:
                    telemetry.set_failure()
                else:
                    retry = False
                    all_skipped = False
                    telemetry.set_success()
                # Update execution result of previous command, fetch recommendation if command failed
                self.recommender.update_exec_result(self.last_exit_code, telemetry.get_error_info()['result_summary'])
                telemetry.flush()
            if quit_scenario:
                break
        if not quit_scenario:
            if all_skipped:
                print_styled_text([(Style.SUCCESS, '\n(✓)Done: '),
                                   (Style.WARNING, 'All commands Skipped! \n')])
            else:
                print_styled_text([(Style.SUCCESS, '\n(✓)Done: '),
                                   (Style.PRIMARY, 'All commands in this scenario have been executed! \n')])
        self.completer.enable_scenario_recommender(True)
        example_cli.exit()
        del example_cli

    def handle_search(self, text):
        """ parses for the scenario search """
        # If the user's input text is "/ connect a momgodb", we extract the keyword "connect a mongodb" from it
        keywords = text.partition(SELECT_SYMBOL['search'])[2].strip()
        if not keywords:
            print_styled_text([(Style.WARNING, 'Please input search keywords')])
            return
        self.recommender.cur_thread = SearchThread(self.recommender.cli_ctx, keywords,
                                                   self.recommender.recommendation_path,
                                                   self.recommender.executing_command,
                                                   self.recommender.on_prepared_callback)
        self.recommender.cur_thread.start()
        # Wait for the search thread to finish
        while self.recommender.cur_thread.is_alive():
            try:
                time.sleep(0.1)
                if self.recommender.cur_thread.result:
                    break
            except (KeyboardInterrupt, ValueError):
                # Catch CTRL + C to quit the search thread
                break
        if self.recommender.cur_thread.result is not None:
            results = self.recommender.cur_thread.result
            # If the result is a string, it means the search thread has encountered an error
            if type(results) is str:
                print_styled_text([(Style.WARNING, results)])
                self.recommender.cur_thread.result = []
                return
            if len(results) == 0:
                print_styled_text([(Style.WARNING, "We currently can't find the scenario you need. \n"
                                                   "You can try to change the search keywords or "
                                                   "submit an issue to ask for the scenario you need.")])
                # -1 means no result
                self.recommender.feedback_search("-1", keywords)
            else:
                show_search_item(results)

                option_msg = [(Style.ACTION, " ? "), (Style.PRIMARY, "Please select your option "),
                              (Style.SECONDARY, "(if none, enter 0)"), (Style.PRIMARY, ": ")]
                option = select_option(option_msg, min_option=0, max_option=len(results), default_option=-1)
                if option == 0:
                    # 0 means no selection
                    self.recommender.feedback_search("0", keywords)
                if option > 0:
                    scenario = results[option - 1]
                    self.recommender.feedback_search(option, keywords, scenario=scenario)
                    self.scenario_repl(scenario)

    def _special_cases(self, cmd, outside):
        break_flag = False
        continue_flag = False
        args = parse_quotes(cmd)
        cmd_stripped = cmd.strip()

        if not cmd_stripped and cmd:
            # add scope if there are only spaces
            cmd = self.default_command + " " + cmd
        elif cmd_stripped in ("quit", "exit"):
            break_flag = True
        elif cmd_stripped == "clear-history":
            continue_flag = True
            self.reset_history()
        elif cmd_stripped == CLEAR_WORD:
            outside = True
            cmd = CLEAR_WORD
        elif cmd_stripped[0] == SELECT_SYMBOL['outside']:
            cmd = cmd_stripped[1:]
            outside = True
            if cmd.strip() and cmd.split()[0] == 'cd':
                self.handle_cd(parse_quotes(cmd))
                continue_flag = True
            telemetry.track_outside_gesture()

        elif cmd_stripped[0] == SELECT_SYMBOL['exit_code']:
            meaning = "Success" if self.last_exit_code == 0 else "Failure"

            print(meaning + ": " + str(self.last_exit_code), file=self.output)
            continue_flag = True
            telemetry.track_exit_code_gesture()
        elif SELECT_SYMBOL['query'] in cmd_stripped and self.last and self.last.result:
            continue_flag = self.handle_jmespath_query(args)
            telemetry.track_query_gesture()
        elif not args:
            continue_flag = True
        elif args[0] == '--version' or args[0] == '-v':
            try:
                continue_flag = True
                self.cli_ctx.show_version()
            except SystemExit:
                pass
        elif cmd.startswith(SELECT_SYMBOL['example']):
            self.handle_scenario(cmd)
            continue_flag = True
        elif cmd.strip().startswith(SELECT_SYMBOL['search']):
            self.handle_search(cmd)
            continue_flag = True
        elif SELECT_SYMBOL['example'] in cmd:
            cmd, continue_flag = self.handle_example(cmd, continue_flag)
            telemetry.track_ran_tutorial()
        elif SELECT_SYMBOL['scope'] == cmd_stripped[0:2]:
            continue_flag, cmd = self.handle_scoping_input(continue_flag, cmd, cmd_stripped)
            telemetry.track_scope_changes()
        else:
            # not a special character; add scope and remove 'az'
            if self.default_command:
                cmd = self.default_command + " " + cmd
            elif cmd.split(' ', 1)[0].lower() == 'az':
                cmd = ' '.join(cmd.split()[1:])
            if "|" in cmd or ">" in cmd:
                # anything I don't parse, send off
                outside = True
                cmd = "az " + cmd
            telemetry.track_cli_commands_used()

        return break_flag, continue_flag, outside, cmd

    def handle_jmespath_query(self, args):
        """ handles the jmespath query for injection or printing """
        continue_flag = False
        query_symbol = SELECT_SYMBOL['query']
        symbol_len = len(query_symbol)
        try:
            if len(args) == 1:
                # if arguments start with query_symbol, just print query result
                if args[0] == query_symbol:
                    result = self.last.result
                elif args[0].startswith(query_symbol):
                    result = jmespath.search(args[0][symbol_len:], self.last.result)
                print(json.dumps(result, sort_keys=True, indent=2), file=self.output)
            elif args[0].startswith(query_symbol):
                # print error message, user unsure of query shortcut usage
                print(("Usage Error: " + os.linesep +
                       "1. Use {0} stand-alone to display previous result with optional filtering "
                       "(Ex: {0}[jmespath query])" +
                       os.linesep + "OR:" + os.linesep +
                       "2. Use {0} to query the previous result for argument values "
                       "(Ex: group show --name {0}[jmespath query])").format(query_symbol), file=self.output)
            else:
                # query, inject into cmd
                def jmespath_query(match):
                    if match.group(0) == query_symbol:
                        return str(self.last.result)
                    query_result = jmespath.search(match.group(0)[symbol_len:], self.last.result)
                    return str(query_result)

                def sub_result(arg):
                    escaped_symbol = re.escape(query_symbol)
                    # regex captures query symbol and all characters following it in the argument
                    return json.dumps(re.sub(r'%s.*' % escaped_symbol, jmespath_query, arg))

                cmd_base = ' '.join(map(sub_result, args))
                self.cli_execute(cmd_base)
            continue_flag = True
        except (jmespath.exceptions.ParseError, CLIError) as e:
            print("Invalid Query Input: " + str(e), file=self.output)
            continue_flag = True
        return continue_flag

    def handle_scoping_input(self, continue_flag, cmd, text):
        """ handles what to do with a scoping gesture """
        default_split = text.partition(SELECT_SYMBOL['scope'])[2].split()
        cmd = cmd.replace(SELECT_SYMBOL['scope'], '')

        continue_flag = True

        if not default_split:
            self.default_command = ""
            print('unscoping all', file=self.output)

            return continue_flag, cmd

        while default_split:
            if not text:
                value = ''
            else:
                value = default_split[0]

            tree_path = self.default_command.split()
            tree_path.append(value)

            if self.completer.command_tree.in_tree(tree_path):
                self.set_scope(value)
                print("defaulting: " + value, file=self.output)
                cmd = cmd.replace(SELECT_SYMBOL['scope'], '')
            elif SELECT_SYMBOL['unscope'] == default_split[0] and self.default_command.split():

                value = self.default_command.split()[-1]
                self.default_command = ' ' + ' '.join(self.default_command.split()[:-1])

                if not self.default_command.strip():
                    self.default_command = self.default_command.strip()
                print('unscoping: ' + value, file=self.output)

            elif SELECT_SYMBOL['unscope'] not in text:
                print("Scope must be a valid command", file=self.output)

            default_split = default_split[1:]
        return continue_flag, cmd

    def reset_history(self):
        history_file_path = os.path.join(self.config.get_config_dir(), self.config.get_history())
        os.remove(history_file_path)
        self.history = FileHistory(history_file_path)
        self.cli.buffers[DEFAULT_BUFFER].history = self.history

    def cli_execute(self, cmd):
        """ sends the command to the CLI to be executed """

        try:
            args = parse_quotes(cmd)

            if args and args[0] == 'feedback':
                self.config.set_feedback('yes')
                self.user_feedback = False

            azure_folder = get_config_dir()
            if not os.path.exists(azure_folder):
                os.makedirs(azure_folder)
            ACCOUNT.load(os.path.join(azure_folder, 'azureProfile.json'))
            CONFIG.load(os.path.join(azure_folder, 'az.json'))
            SESSION.load(os.path.join(azure_folder, 'az.sess'), max_age=3600)

            invocation = self.cli_ctx.invocation_cls(cli_ctx=self.cli_ctx,
                                                     parser_cls=self.cli_ctx.parser_cls,
                                                     commands_loader_cls=self.cli_ctx.commands_loader_cls,
                                                     help_cls=self.cli_ctx.help_cls)

            if '--progress' in args:
                args.remove('--progress')
                execute_args = [args]
                thread = Thread(target=invocation.execute, args=execute_args)
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
                self.curr_thread = thread

                progress_args = [self]
                thread = Thread(target=progress_view, args=progress_args)
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
                result = None
            else:
                try:
                    result = invocation.execute(args)
                    # Prevent users from exiting the entire az interactive by using Ctrl+C during command execution
                except KeyboardInterrupt:
                    result = None
                    self.last_exit_code = 1
                except SystemExit as ex:
                    # prevent errors caused by uncompleted command loading
                    if ex.code == 2 and self.command_table_thread.is_alive():
                        print_styled_text([(Style.ERROR, "Command loading is not complete, please wait...")])
                    result = None

            self.last_exit_code = 0
            if result and result.result is not None:
                if self.output:
                    self.output.write(result)
                    self.output.flush()
                else:
                    formatter = self.cli_ctx.output.get_formatter(self.cli_ctx.invocation.data['output'])
                    self.cli_ctx.output.out(result, formatter=formatter, out_file=sys.stdout)
                    self.last = result

        except Exception as ex:  # pylint: disable=broad-except
            self.last_exit_code = handle_exception(ex)
        except SystemExit as ex:
            self.last_exit_code = int(ex.code)

    def progress_patch(self, *args, **kwargs):
        """ forces to use the Shell Progress """
        from .progress import ShellProgressView
        self.cli_ctx.progress_controller.init_progress(ShellProgressView())
        return self.cli_ctx.progress_controller

    def load_command_table(self):
        """ loads the command table """
        # initialize some variables
        # whether the customer has been prompted to choose continue loading
        # unable to use continue_loading to check this because the customer may choose to continue loading
        if not self.cli_ctx.config.getboolean("interactive", "enable_preloading", fallback=True):
            self.command_table_thread = LoadCommandTableThread(self.restart_completer, self)
            self.command_table_thread.start()
            return
        print_styled_text([(Style.ACTION, "A command preload mechanism was added to prevent lagging and command run errors.\n"
                                          "You can skip preloading in a single pass by CTRL+C or turn it off by setting 'az config set interactive.enable_preloading=False'\n")])
        already_prompted = False
        continue_loading = True
        # load command table
        self.command_table_thread = LoadCommandTableThread(self.restart_completer, self)
        self.command_table_thread.start()
        self.command_table_thread.start_time = time.time()
        print_styled_text([(Style.ACTION, "Loading command table... Expected time around 1 minute.")])
        progress_bar = IndeterminateProgressBar(cli_ctx=self.cli_ctx, message="Loading command table")
        progress_bar.begin()

        # still loading commands, show the time of loading
        while self.command_table_thread.is_alive():
            try:
                time_spent_on_loading = time.time() - self.command_table_thread.start_time
                progress_bar = IndeterminateProgressBar(cli_ctx=self.cli_ctx,
                                                        message="Already spent {} seconds on loading.".format(
                                                            round(time_spent_on_loading, 1)))
                progress_bar.update_progress()
                time.sleep(0.1)
                # setup how long to wait before prompting the customer to continue loading
                # whether the loading time is too long(>150s)
                prompt_timeout_limit = 150
            except KeyboardInterrupt:
                # if the customer presses Ctrl+C, break the loading loop
                continue_loading = whether_continue_module_loading()
            if time_spent_on_loading > prompt_timeout_limit and not already_prompted:
                print_styled_text([(Style.WARNING,
                                    '\nLoading command table takes too long, please contact the Azure CLI team for help.')])
                continue_loading = whether_continue_module_loading()
                already_prompted = True
            # if the customer chooses not to continue loading, break the loading loop
            if not continue_loading:
                break
        progress_bar.stop()

    def run(self):
        """ starts the REPL """
        self.load_command_table()
        # init customized processing bar
        from .progress import ShellProgressView
        self.cli_ctx.get_progress_controller().init_progress(ShellProgressView())
        self.cli_ctx.get_progress_controller = self.progress_patch

        from .configuration import SHELL_HELP
        self.cli.buffers['symbols'].reset(
            initial_document=Document(u'{}'.format(SHELL_HELP)))
        # flush telemetry for new commands and send successful interactive mode entry event
        telemetry.set_success()
        telemetry.flush()
        while True:
            try:
                # Reset the user input analysis state in completer to clear the hint in command description section
                self.completer.reset()
                document = self.cli.run(reset_current_buffer=True)
                text = document.text
                if not text:
                    # not input
                    self.set_prompt()
                    continue
                cmd = text
                outside = False

            except AttributeError:
                # when the user pressed Control D
                # IDEA: Create learning mode, automatically create temp-resource-group when initialized and put all resources in this temp-resource-group automatically;
                # IDEA: Automatically delete the whole temp-resource-group when the user logs out or when no operation is invoked for one hour.
                # TODO: prompt a notice to ask if the user wants to delete all the resources created
                break
            except (KeyboardInterrupt, ValueError):
                # CTRL C
                # Clear the Screen and refresh interface
                cmd = CLEAR_WORD
                self.set_prompt()
                subprocess.Popen(cmd, shell=True).communicate()
            else:
                self.history.append(text)
                b_flag, c_flag, outside, cmd = self._special_cases(cmd, outside)

                if b_flag:
                    break
                if c_flag:
                    self.set_prompt()
                    continue

                self.set_prompt()

                if outside:
                    subprocess.Popen(cmd, shell=True).communicate()
                else:
                    telemetry.start()
                    # Prefetch the next recommendation using current executing command
                    self.recommender.update_executing(cmd)
                    self.cli_execute(cmd)
                    if self.last_exit_code:
                        telemetry.set_failure()
                    else:
                        telemetry.set_success()
                    # Update execution result of previous command, fetch recommendation if command failed
                    self.recommender.update_exec_result(self.last_exit_code,
                                                        telemetry.get_error_info()['result_summary'])
                    telemetry.flush()
        telemetry.conclude()
