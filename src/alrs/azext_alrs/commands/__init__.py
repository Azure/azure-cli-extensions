from azext_alrs.commands import (  # registers helps on import
    distro,
    package,
    publication,
    remote,
    repository,
    repository_package,
    repository_release,
    task,
)

_MODULES = (
    repository,
    repository_package,
    repository_release,
    remote,
    distro,
    package,
    publication,
    task,
)


def load_command_table(loader, _args):
    for mod in _MODULES:
        mod.register_commands(loader)


def load_arguments(loader, command):
    for mod in _MODULES:
        mod.load_arguments(loader, command)
