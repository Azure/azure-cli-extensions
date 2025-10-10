# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

"""
Client for all CLI actions.
"""

from abc import ABCMeta

from azext_arcdata.core.output import OutputStream
from azext_arcdata.core.services import beget_service
from azure.cli.core._profile import Profile
from knack.cli import CLIError
from knack.log import get_logger
from six import add_metaclass

__all__ = ["beget", "CliClient"]

logger = get_logger(__name__)


def beget(az_cli, kwargs):
    """Client factory"""
    return CliClient(az_cli, kwargs, check_namespace=None)


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


@add_metaclass(ABCMeta)
class BaseCliClient(object):
    def __init__(self):
        pass

    @property
    def stdout(self):
        return OutputStream().stdout.write

    @property
    def stderr(self):
        return OutputStream().stderr.write

    def __str__(self):
        """
        Returns the base string representation of attributes. Sub-class should
        override and implement.
        """
        return "<BaseCliClient>"

    def __repr__(self):
        """For `print` and `pprint`. Sub-class should override and implement."""
        return self.__str__()


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


class CliClient(BaseCliClient):
    """
    Default client injected in every command group. For further command
    customization extend this class.
    """

    def __init__(self, az_cli, kwargs, check_namespace=False):
        super(CliClient, self).__init__()

        self._az_cli = az_cli
        self._args = kwargs
        self._utils = None
        self._terminal = None

        logger.debug(self._args)

        if check_namespace is None:  # tmp for dc
            self._az_cli.data["arcdata_command_args"] = self._args
            service = beget_service(self.az_cli)
            d = dict()
            d[service.name] = service
            self._services = type("", (object,), d)
        else:
            ###############################################################
            # Only tmp until we move sqlmi/postgres over to this new model
            ###############################################################
            from azext_arcdata.core.prompt import prompt
            from azext_arcdata.core.util import load_kube_config
            from azext_arcdata.kubernetes_sdk.client import KubernetesClient
            from knack.prompting import NoTTYException
            from kubernetes.config.config_exception import ConfigException

            self._namespace = None
            self._apis = type("", (object,), {"kubernetes": KubernetesClient()})
            if self._args.get("use_k8s"):
                try:
                    namespace = self._args.get("namespace")
                    logger.debug(
                        "Provided k8s-namespace = {0}".format(namespace)
                    )
                    logger.debug(
                        "Force namespace    = {0}".format(check_namespace)
                    )

                    if not namespace and check_namespace:
                        namespace = load_kube_config().get("namespace")
                        if not namespace:
                            namespace = prompt("Kubernetes Namespace: ")
                    self._namespace = namespace
                    logger.debug(
                        "Using Kubernetes namespace = {0}".format(
                            self.namespace
                        )
                    )
                except NoTTYException:
                    raise NoTTYException(
                        "You must have a tty to prompt "
                        "for Kubernetes namespace. Please provide a "
                        "--k8s-namespace argument instead."
                    )
                except (ConfigException, Exception) as ex:
                    raise CLIError(ex)

                logger.debug(
                    "Using Kubernetes namespace = {0}".format(namespace)
                )

                self._namespace = namespace
            ###############################################################

    @property
    def az_cli(self):
        """
        Gets a reference to this command's `AzCli` execution context.
        """
        return self._az_cli

    @property
    def profile(self):
        """
        Gets the user Profile.
        :return:
        """
        return Profile(cli_ctx=self.az_cli.local_context.cli_ctx)

    @property
    def subscription(self):
        """
        Gets the Azure subscription.
        """

        # Gets the azure subscription by attempting to gather it from:
        # 1. global argument [--subscription] if provided
        # 2. Otherwise active subscription in profile if available
        # 3. Otherwise `None`
        subscription = self.az_cli.data.get("subscription_id")

        if not subscription:
            try:
                subscription = self.profile.get_subscription_id()
            except CLIError:
                subscription = None
        else:
            try:
                subscription = self.profile.get_subscription(
                    subscription=subscription
                ).get("id")
            except CLIError:
                logger.warning("To not see this warning, first login to Azure.")

        return subscription

    @property
    def services(self):
        return self._services

    def args_to_command_value_object(self, kwargs=None):
        """
        Converts a `dict` of command argument name/values into a `Named Tuple`
        representing "Command Value Object" pattern for arguments.

        If no arguments are provided in `kwargs` then we use the original
        superset of arguments provided from the command-line.

        :return: The command's arguments as "Command Value Object",
        """
        from collections import namedtuple

        args = kwargs or self._args

        return namedtuple("CommandValueObject", " ".join(list(args.keys())))(
            **args
        )

    @property
    def apis(self):
        return self._apis

    @property
    def namespace(self):
        return self._namespace

    @property
    def terminal(self):
        """
        Object mapping to supported public `terminal` operations.

         Supported:
        - `progress_indicator`

        Example:

        ```
        progress = client.terminal.progress_indicator
        ...
        ...
        ```

        :return: The Object mapping to supported terminal operations.
        """
        if self._terminal:
            return self._terminal

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------

        class Progress(object):
            """
            Show a spinner on the terminal that automatically
            starts animating around a provided worker function.

            Example:

            ```
            add = lambda a, b: return a + b
            args = {'a': 1, 'b': 2}

            progress = client.terminal.progress_indicator
            result = progress.message('Downloading').worker(
            add, args).start()
            ```

            :return: A `Progress` instance to load-up and start.
            """

            def __init__(self):
                self._defaults()

            def _defaults(self):
                self._show_time = True
                self._worker = {"fn": None, "args": {}}
                self._message = ""

            def worker(self, fn, args):
                self._worker = {"fn": fn, "args": args}
                return self

            def message(self, message):
                self._message = message
                return self

            def show_time(self, show_time):
                self._show_time = show_time
                return self

            def start(self):
                from azext_arcdata.core.util import is_windows
                from humanfriendly.terminal.spinners import AutomaticSpinner

                message = self._message
                worker_fn = self._worker.get("fn")
                arguments = self._worker.get("args")
                show_time = self._show_time

                assert worker_fn

                try:
                    if not is_windows():
                        with AutomaticSpinner(message, show_time=show_time):
                            return worker_fn(**arguments)
                    else:
                        # TODO: Make the same experience for windows ps1/dos
                        OutputStream().stdout.write(message)
                        result = worker_fn(**arguments)
                        return result
                finally:
                    self._defaults()  # reset

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        from azext_arcdata.core.text import Text

        self._terminal = type(
            "", (object,), {"progress_indicator": Progress(), "text": Text()}
        )

        return self._terminal

    @property
    def utils(self):
        """
        Object mapping to supported public `utils` operations.

        Supported:
        - `download`
        - `import_api`

        Example:
        ```
        client.utils.download(...)
        client.utils.import_api(...)
        ```

        :return: The Object mapping to supported `utils` operations.
        """
        if self._utils:
            return self._utils

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------

        def download(
            url,
            filename,
            destination=None,
            label="Downloading",
            show_progress=True,
        ):
            """
            Helper to download a file given the url and a write destination.
            If no
            destination is given the file download is sent to a temporary
            location.

            :param url: The URL to the file to be downloaded.
            :param filename: Name the downloaded file.
            :param destination: Location where to save file.
            :param label: Work with `show_progress` to define the label for the
                   optional spinner (a string or None, defaults to Downloading).
            :param show_progress: To display a progress spinner on the terminal.
            :return: The path to the downloaded file.
            """
            import os
            import shutil
            import tempfile
            import time
            import urllib

            def _download(uri, name, dest):
                stage_dir = tempfile.mkdtemp()
                try:
                    file_path = os.path.join(stage_dir, name)
                    num_blocks = 0
                    chunk_size = 4096
                    req = urllib.request.urlopen(uri)

                    with open(file_path, "wb") as f:
                        while True:
                            data = req.read(chunk_size)
                            time.sleep(0.5)
                            num_blocks += 1

                            if not data:
                                break

                            f.write(data)

                    return (
                        shutil.copyfile(file_path, dest) if dest else file_path
                    )
                except IsADirectoryError:
                    from urllib.error import URLError

                    raise URLError("Not able to download file", filename=uri)
                finally:
                    if dest:
                        shutil.rmtree(stage_dir, ignore_errors=True)

            if destination and not os.path.isdir(destination):
                raise ValueError(
                    "Destination directory does not exist {0}".format(
                        destination
                    )
                )

            # -- download and show progress indicator --
            if not show_progress:
                return _download(url, filename, destination)
            else:
                return (
                    self.terminal.progress_indicator.worker(
                        _download,
                        {"uri": url, "name": filename, "dest": destination},
                    )
                    .message(label)
                    .start()
                )

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------

        self._utils = type("", (object,), {"download": download})

        return self._utils
