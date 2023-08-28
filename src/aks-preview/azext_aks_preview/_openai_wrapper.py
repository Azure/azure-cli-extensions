# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
import os
import sys
import subprocess

import openai
from colorama import Fore, Style

STATE_IN_CHAT = 1
STATE_IN_CODE = 0

IS_MS_WINDOWS = os.name == 'nt'

if IS_MS_WINDOWS:
    SCRIPT_TYPE = "Windows PowerShell"
else:
    SCRIPT_TYPE = "Bash Script"

AKS_EXPERT = f'''
You are a microsoft Azure Kubernetes Service expert.

Context: The user will provide you a description of what they want to accomplish

Your task is to help user writing a {SCRIPT_TYPE} to automate AKS that leverages the `az` command

When constructing `az` commands to execute, always fill in a default input value for the command by
helping the user to make up names, and come up with sensible default like a specific number or region name.

If there are required input value that you need user to provide, prompt the user for the value,
if possible, provide hints or commands for the user to execute for them to get the required value.

each script block you output enclosed by ``` should be self sufficient to run
if you create variable in a previous script block, repeat it again if it is needed in another script block.

Be aware that as a AI model, your data might be out of date, if user supplied input that you are unaware of, just accept and use it.

The user will not be able save content to file, so if you have text input, supply them as HERE doc to the script.

Write the {SCRIPT_TYPE} and add explanations as comments within script.
'''.strip()
SYSTEM_PROMPT = {"role": "system", "content": AKS_EXPERT}

# Define a platform-specific function to get a single character
if IS_MS_WINDOWS:
    # Windows system
    import msvcrt

    def getch():
        return msvcrt.getch().decode('utf-8')
else:
    # Unix-based system
    import termios
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def run_command_as_shell(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return process.returncode, stderr.decode()
    return process.returncode, stdout.decode()


def run_system_script(script_content: str):
    # do not set capture_output=True, so user can interact with yes/no answer from script
    if IS_MS_WINDOWS:
        cmd = ["powershell", "-Command", script_content]
    else:
        cmd = ["bash", "-c", script_content]
    result = subprocess.run(cmd, text=True)
    return result.returncode


def extract_backticks_commands(text):
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    strip_pattern = r'^(powershell\s*|bash\s*|shell\s*)'
    return [re.sub(strip_pattern, '', match.strip()) for match in matches]


def process_result(text):
    matches = extract_backticks_commands(text)
    return matches


def get_prop(multilayers_dict, key, default=None):
    keys = key.split('.')
    val = multilayers_dict
    try:
        for k in keys:
            if k.isdigit():
                k = int(k)
            val = val[k]
    except Exception:
        return default
    return val


def switch_color_context(state):
    if state == STATE_IN_CHAT:
        print(Fore.CYAN)
    else:
        print(Fore.GREEN)


def chatgpt(messages, params):
    response = openai.ChatCompletion.create(
        # top_p=0.95,
        # frequency_penalty=0,
        # presence_penalty=0,
        messages=messages,
        stop=None,
        stream=True,
        **params,
    )

    state = STATE_IN_CHAT
    switch_color_context(state)
    collected_messages = []
    previous_context = ''
    for _, chunk in enumerate(response):
        content = get_prop(chunk, 'choices.0.delta.content', '')  # extract the message
        if content:
            collected_messages.append(content)  # save the message
            if previous_context:
                content = previous_context + content
                previous_context = ''
            if content in ('``', '`'):
                previous_context = content
                continue
            if re.search(r"""[^`]+``$""", content):
                previous_context = '``'
                content = content[0:-2]
            elif re.search(r"""[^`]+`$""", content):
                previous_context = '`'
                content = content[0:-1]

            parts = content.split('```')
            if len(parts) > 1:
                for i, part in enumerate(parts):
                    if i > 0:
                        if state == STATE_IN_CHAT:
                            state = state ^ 1
                            switch_color_context(state)
                            print('```', end='')
                        else:
                            print('```', end='')
                            state = state ^ 1
                            switch_color_context(state)
                    print(part, end='')
            else:
                print(content, end="")
    if previous_context:
        print(previous_context, end='')
    print("\n", flush=True)
    print(Style.RESET_ALL)

    msg = ''.join(collected_messages)
    messages.append({"role": 'assistant',
                     "content": msg})
    scripts = process_result(msg)
    return msg, scripts, messages


def prompt_user_to_run_script(scripts):
    n_scripts = len(scripts)
    if n_scripts > 1:
        for i, script in enumerate(scripts):
            print(Style.RESET_ALL)
            print(f"Hit `{i}` key to run the script as below:")
            switch_color_context(STATE_IN_CODE)
            print(script)
    elif n_scripts == 1:
        switch_color_context(STATE_IN_CODE)
        print(scripts[0])
    else:
        return
    print(Style.RESET_ALL)
    print(f"Hit `c` to cancel", end="")
    if n_scripts == 1:
        print(", `r` to run the script", end="")
    print(": ", end="", flush=True)
    while True:
        user_input = getch()
        if user_input in ('C', 'c'):
            return
        if user_input in ('R', 'r'):
            user_input = '0'
        ord_0 = ord('0')
        ord_code = ord(user_input)
        if ord_0 <= ord_code < ord_0 + n_scripts:
            i = ord_code - ord_0
            script = scripts[i]
            return run_system_script(script)


USER_INPUT_PROMPT = "Prompt: "


def prompt_chat_gpt(messages, params, start_input=None, insist=True, scripts=''):
    while True:
        if start_input:
            text_input = start_input.strip()
            start_input = None
        else:
            text_input = str(input(USER_INPUT_PROMPT)).strip()
        if re.search(r'[a-zA-Z]', text_input):
            messages.append({"role": "user", "content": text_input})
            _, scripts, messages = chatgpt(messages, params)
            return scripts, messages
        if not insist:
            return scripts, messages


def setup_openai():
    """
    # Setup environmental variables
    export OPENAI_API_KEY='xxxx'
    export OPENAI_API_TYPE="azure"
    export OPENAI_API_BASE="https://xxxinstance.openai.azure.com/"
    export OPENAI_API_VERSION="2023-03-15-preview"
    export OPENAI_API_DEPLOYMENT="gpt-4-32k-0314"
    """
    errors = []
    params = {
        'temperature': os.getenv("OPENAI_API_TEMPERATURE") or 0.1
    }
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        errors.append("Environment variable OPENAI_API_KEY is not set")
    else:
        openai.api_key = api_key

    api_type = os.getenv("OPENAI_API_TYPE", openai.api_type)
    if api_type and api_type.startswith("azure"):
        openai.api_type = api_type

        api_base = os.getenv("OPENAI_API_BASE")
        if not api_base:
            errors.append("Environment variable OPENAI_API_BASE is not set for Azure API Type")
        else:
            openai.api_base = api_base

        api_version = os.getenv("OPENAI_API_VERSION", openai.api_version)
        if not api_version:
            errors.append("Environment variable OPENAI_API_VERSION is not set for Azure API Type")
        else:
            openai.api_version = api_version

        api_deployment = os.getenv("OPENAI_API_DEPLOYMENT")
        if not api_deployment:
            errors.append("Environment variable OPENAI_API_DEPLOYMENT is not set for Azure API Type")
        else:
            params['engine'] = api_deployment
    else:
        api_model = os.getenv("OPENAI_API_MODEL")
        if not api_model:
            errors.append("Environment variable OPENAI_API_MODEL is not set")
        else:
            params['model'] = api_model

    return errors, params
