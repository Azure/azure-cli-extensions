# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

import os
import sys
import azext_arcdata.core.constants as const

from azext_arcdata.core.util import is_valid_password
from azext_arcdata.core.prompt import prompt, prompt_pass
from knack.log import get_logger
from typing import List
from collections import namedtuple

__all__ = ["Env"]
logger = get_logger(__name__)


class Env:
    CONTROLLER_ENV_LIST = [const.AZDATA_USERNAME, const.AZDATA_PASSWORD]
    """
    Get the list of environment variables required for the controller
    """

    @staticmethod
    def get(env):
        """
        This is the currently supported list of environment values and lookup.
        :return: The given env variable value otherwise `None`.
        """
        e = None
        getenv = os.getenv

        if env == "DOCKER_REGISTRY":
            e = getenv("CONTROLLER_REGISTRY") or getenv("DOCKER_REGISTRY")

        if env == "DOCKER_REPOSITORY":
            e = getenv("CONTROLLER_REPOSITORY") or getenv("DOCKER_REPOSITORY")

        if env == "DOCKER_IMAGE_TAG":
            e = (
                getenv("CONTROLLER_IMAGE_TAG")
                or getenv("DOCKER_IMAGE_TAG")
                or getenv("DOCKER_TAG")
            )

        if env == "DOCKER_IMAGE_POLICY":
            e = getenv("DOCKER_IMAGE_POLICY")

        if env == "DOCKER_USERNAME":
            e = os.getenv("DOCKER_USERNAME") or getenv("REGISTRY_USERNAME")

        if env == "DOCKER_PASSWORD":
            e = os.getenv("DOCKER_PASSWORD") or getenv("REGISTRY_PASSWORD")

        if env == "WORKSPACE_ID":
            e = getenv("WORKSPACE_ID") or getenv("LOG_WORKSPACE_ID")

        if env == "WORKSPACE_SHARED_KEY":
            e = getenv("WORKSPACE_SHARED_KEY") or getenv("LOG_SHARED_KEY")

        if env == "ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN":
            e = getenv("ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN")

        if env == "ARC_DATASERVICES_EXTENSION_VERSION_TAG":
            e = getenv("ARC_DATASERVICES_EXTENSION_VERSION_TAG")

        if env == "AZDATA_USERNAME":
            e = getenv("AZDATA_USERNAME")

        if env == "AZDATA_PASSWORD":
            e = getenv("AZDATA_PASSWORD")

        return e

    @staticmethod
    def is_set(env_var: str) -> bool:
        """
        Checks if the given environment variable is set and not empty/whitespace
        """

        var = os.getenv(env_var)
        return var is not None and len(var.strip()) != 0

    @staticmethod
    def check_environment_variables(target):
        """
        Check if all necessary environment variables are set.
        """

        env_list = Env.CONTROLLER_ENV_LIST
        missing_env = list()
        for env in env_list:
            if not Env.is_set(env):
                missing_env.append(env)

        if len(missing_env) > 0:
            logger.error(
                "Please set the following environment variable(s): %s."
                % missing_env
            )
            sys.exit(1)

    @staticmethod
    def env_vars_are_set(env_vars: List[str]) -> bool:
        """
        Checks if the given list of environment variables are set or not.
        :returns: True if all of the variables are set, false otherwise.
        """

        for var in env_vars:
            if not Env.is_set(var):
                return False

        return True

    @staticmethod
    def _set_credential_vars(vars: List[str], msg: str):
        """
        Prompts the user to enter values for the given vars. Expecting
        a username var to be first in the list and password second.
        """
        if not Env.is_set(vars[0]):
            os.environ[vars[0]] = prompt(msg.strip() + " username: ")
        if not Env.is_set(vars[1]):
            os.environ[vars[1]] = prompt_pass(msg.strip() + " password: ", True)

    @staticmethod
    def _validate_creds_from_env(username_var: str, password_var: str):
        """
        Ensures that both or neither of the username and password
        environment variables are set and that passwords meet complexity
        requirements
        """

        username = os.environ.get(username_var)
        password = os.environ.get(password_var)
        if bool(username) ^ bool(password):
            raise ValueError(
                "Must specify both {0} and {1} or neither.".format(
                    username_var, password_var
                )
            )
        if username and password and not is_valid_password(password, username):
            raise ValueError(
                "Invalid password from "
                + password_var
                + ". Passwords must be at "
                "least 8 characters long, cannot contain the "
                "username, and must contain characters from "
                "three of the following four sets: Uppercase "
                "letters, Lowercase letters, Base 10 digits, "
                "and Symbols. Please try again.\n"
            )

    @staticmethod
    def get_sqlmi_credentials():
        default_vars = [const.AZDATA_USERNAME, const.AZDATA_PASSWORD]
        if not Env.env_vars_are_set(default_vars):
            if sys.stdin.isatty():
                Env._set_credential_vars(
                    default_vars, "SQL Managed Instance admin"
                )
            else:
                raise ValueError(
                    "Missing environment variables. Please set {0} "
                    "and {1}".format(
                        const.AZDATA_USERNAME, const.AZDATA_PASSWORD
                    )
                )

        os.environ[default_vars[0]] = os.getenv(default_vars[0]).strip()
        os.environ[default_vars[1]] = os.getenv(default_vars[1]).strip()

        Env._validate_creds_from_env(default_vars[0], default_vars[1])

        args = {
            "username": os.getenv(default_vars[0]),
            "password": os.getenv(default_vars[1]),
        }

        return namedtuple("SqlMiCredentials", " ".join(list(args.keys())))(
            **args
        )

    @staticmethod
    def get_log_and_metrics_credentials():
        """
        Validates and ensures that two of the three following sets of
        environment variables are set (or just AZDATA_USERNAME and
        AZDATA_PASSWORD): (AZDATA_USERNAME, AZDATA_PASSWORD)
                          (LOGSUI_USERNAME, LOGSUI_PASSWORD)
                          (METRICSUI_USERNAME, METRICSUI_PASSWORD)
        """

        def _raise_error(env_vars: List[str]):
            raise ValueError(
                "Missing environment variables."
                " Please set either {0} and {1} or {2} and {3}".format(
                    const.AZDATA_USERNAME,
                    const.AZDATA_PASSWORD,
                    env_vars[0],
                    env_vars[1],
                )
            )

        # Raise error if only one part of a credential is set
        #
        logs_vars = [const.LOGSUI_USERNAME, const.LOGSUI_PASSWORD]
        metrics_vars = [const.METRICSUI_USERNAME, const.METRICSUI_PASSWORD]
        default_vars = [const.AZDATA_USERNAME, const.AZDATA_PASSWORD]

        Env._validate_creds_from_env(
            logs_vars[0], logs_vars[1]
        )  # CodeQL [SM02736] False Positive: CodeQL wrongly detected hard-coded credentials
        Env._validate_creds_from_env(metrics_vars[0], metrics_vars[1])

        if not (
            Env.env_vars_are_set(logs_vars)
            and Env.env_vars_are_set(metrics_vars)
        ):
            if Env.env_vars_are_set(metrics_vars):
                if not Env.env_vars_are_set(default_vars):
                    if sys.stdin.isatty():
                        Env._set_credential_vars(
                            logs_vars, "Logs administrator"
                        )
                    else:
                        _raise_error(logs_vars)
            elif Env.env_vars_are_set(logs_vars):
                if not Env.env_vars_are_set(default_vars):
                    if sys.stdin.isatty():
                        Env._set_credential_vars(
                            metrics_vars, "Metrics administrator"
                        )
                    else:
                        _raise_error(metrics_vars)
            else:
                if not Env.env_vars_are_set(default_vars):
                    if sys.stdin.isatty():
                        Env._set_credential_vars(
                            default_vars, "Monitoring administrator"
                        )
                    else:
                        raise ValueError(
                            "Missing environment variables. Please set {0} "
                            "and {1}".format(
                                const.AZDATA_USERNAME, const.AZDATA_PASSWORD
                            )
                        )
                Env._validate_creds_from_env(default_vars[0], default_vars[1])

        logs_vars = [const.LOGSUI_USERNAME, const.LOGSUI_PASSWORD]
        metrics_vars = [const.METRICSUI_USERNAME, const.METRICSUI_PASSWORD]
        default_vars = [const.AZDATA_USERNAME, const.AZDATA_PASSWORD]

        azdata_username = os.getenv(default_vars[0])
        azdata_password = os.getenv(default_vars[1])

        logui_username = os.getenv(logs_vars[0])
        logui_password = os.getenv(logs_vars[1])

        metricsui_username = os.getenv(metrics_vars[0])
        metricsui_password = os.getenv(metrics_vars[1])

        if not metricsui_username:
            metricsui_username = azdata_username

        if not metricsui_password:
            metricsui_password = azdata_password

        if not logui_username:
            logui_username = metricsui_username

        if not logui_password:
            logui_password = metricsui_password

        args = {
            "log_username": logui_username,
            "log_password": logui_password,
            "metrics_username": metricsui_username,
            "metrics_password": metricsui_password,
        }

        return namedtuple("LogMetricsCredentials", " ".join(list(args.keys())))(
            **args
        )

    @staticmethod
    def get_active_directory_domain_account_credentials():
        default_vars = [
            const.DOMAIN_SERVICE_ACCOUNT_USERNAME,
            const.DOMAIN_SERVICE_ACCOUNT_PASSWORD,
        ]
        if not Env.env_vars_are_set(default_vars):
            if sys.stdin.isatty():
                Env._set_credential_vars(
                    default_vars, "Active Directory domain service account"
                )
            else:
                raise ValueError(
                    "Missing environment variables. Please set {0} "
                    "and {1}".format(
                        const.DOMAIN_SERVICE_ACCOUNT_USERNAME,
                        const.DOMAIN_SERVICE_ACCOUNT_PASSWORD,
                    )
                )

        os.environ[default_vars[0]] = os.getenv(default_vars[0]).strip()
        os.environ[default_vars[1]] = os.getenv(default_vars[1]).strip()

        args = {
            "username": os.getenv(default_vars[0]),
            "password": os.getenv(default_vars[1]),
        }

        return namedtuple(
            "ADDomainAccountCredentials", " ".join(list(args.keys()))
        )(**args)
