from colorama import Fore

def provide_project_or_dc_warning():
    print(Fore.RED + 'You must provide either a project (--project --project-name) or dev center (--dev-center --dev-center-name -dc)' + Fore.RESET, end='')
