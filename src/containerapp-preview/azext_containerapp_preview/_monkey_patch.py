# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys


def uncache(exclude):
    pkgs = []
    for mod in exclude:
        pkg = mod.split('.', 1)[0]
        pkgs.append(pkg)
    to_uncache = []
    for mod in sys.modules:
        if mod in exclude:
            continue
        if mod in pkgs:
            to_uncache.append(mod)
            continue
        for pkg in pkgs:
            if mod.startswith(pkg + '.'):
                to_uncache.append(mod)
                break
    for mod in to_uncache:
        del sys.modules[mod]


# Monkey patch for the PollingAnimation
# removes the spinner and message written to standard out
# which breaks the ability to re-use output from the
# the containerapp compose create command
# example:
# `URL=$(az containerapp compose create -e myenv -g myrg --query [0].properties.configuration.ingress.fqdn -o tsv)`
# In that example, the URL variable would include a number of lines with the polling animation,
# making it difficult to reusue the output from the CLI command.
def tick(self):
    self.currTicker += 1
    self.currTicker = self.currTicker % len(self.tickers)


# Monkey patch for the PollingAnimation (see above)
def flush(self):  # noqa: W0613 pylint: disable=unused-argument
    pass


try:
    from azext_containerapp import custom  # pylint: disable=unused-import
    from azext_containerapp import _utils  # pylint: disable=unused-import
    from azext_containerapp import _clients  # pylint: disable=unused-import
    _clients.PollingAnimation.tick = tick
    _clients.PollingAnimation.flush = flush
    uncache("azext_containerapp._clients")
    from azext_containerapp import _clients  # pylint: disable=unused-import
    from azext_containerapp._clients import ManagedEnvironmentClient   # pylint: disable=unused-import
except ModuleNotFoundError:
    from .vendored_sdks.azext_containerapp import custom  # pylint: disable=unused-import
    from .vendored_sdks.azext_containerapp import _utils  # pylint: disable=unused-import
    from .vendored_sdks.azext_containerapp import _clients  # pylint: disable=unused-import
    _clients.PollingAnimation.tick = tick
    _clients.PollingAnimation.flush = flush
    uncache("azext_containerapp_preview.vendored_sdks.azext_containerapp")
    from .vendored_sdks.azext_containerapp import _clients  # pylint: disable=unused-import
    from .vendored_sdks.azext_containerapp._clients import ManagedEnvironmentClient   # pylint: disable=unused-import
except ImportError:
    from .vendored_sdks.azext_containerapp import custom  # pylint: disable=unused-import
    from .vendored_sdks.azext_containerapp import _utils  # pylint: disable=unused-import
    from .vendored_sdks.azext_containerapp import _clients  # pylint: disable=unused-import
    _clients.PollingAnimation.tick = tick
    _clients.PollingAnimation.flush = flush
    uncache("azext_containerapp_preview.vendored_sdks.azext_containerapp")
    from .vendored_sdks.azext_containerapp._clients import ManagedEnvironmentClient   # pylint: disable=unused-import


# Monkey patch for log analytics workspace name
# this allows the test framework to pass down a specific
# name to support playback of recorded tests.
def override_random_log_analytics_name(resource_group_name):  # pylint: disable=unused-argument
    return _utils.logs_workspace_name  # noqa: F821 pylint: disable=undefined-variable


def create_containerapps_compose_environment(cmd,
                                             name,
                                             resource_group_name,
                                             logs_workspace_name=None,
                                             tags=None):
    if logs_workspace_name is not None:
        monkey_patch = override_random_log_analytics_name
        _utils._generate_log_analytics_workspace_name = monkey_patch  # pylint: disable=protected-access
        _utils.logs_workspace_name = logs_workspace_name
    return custom.create_managed_environment(cmd,
                                             name,
                                             resource_group_name,
                                             tags=tags)


def create_containerapp_from_service(*args, **kwargs):
    return custom.create_containerapp(*args, **kwargs)
