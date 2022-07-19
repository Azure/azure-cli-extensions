from colorama import Fore


def read_int(default_value=0):
    ret = input()
    if ret == '' or ret is None:
        return default_value
    while not ret.isnumeric():
        ret = input("Please input a legal number: ")
        if ret == '' or ret is None:
            return default_value
    return int(ret)


def get_int_option(option_description, min_option, max_option, default_option):
    print(Fore.LIGHTBLUE_EX + ' ? ' + Fore.RESET + option_description, end='')
    option = read_int(default_option)
    while option < min_option or option > max_option:
        print("Please enter a valid option ({}-{}): ".format(min_option, max_option), end='')
        option = read_int(default_option)
    return option


def print_successful_styled_text(message):
    from azure.cli.core.style import print_styled_text, Style, is_modern_terminal

    prefix_text = '\nDone: '
    if is_modern_terminal():
        prefix_text = '\n(✓ )Done: '
    print_styled_text([(Style.SUCCESS, prefix_text), (Style.PRIMARY, message)])