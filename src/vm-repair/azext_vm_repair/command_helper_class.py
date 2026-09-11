# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-instance-attributes

import logging
import timeit
import inspect
from knack.log import get_logger

from azure.cli.core.commands.client_factory import get_subscription_id

from .telemetry import _track_command_telemetry, _track_run_command_telemetry, _track_command_telemetry_repair_and_restore

from .repair_utils import _get_function_param_dict

STATUS_SUCCESS = 'SUCCESS'
STATUS_ERROR = 'ERROR'
VM_REPAIR_RUN_COMMAND = 'vm repair run'
VM_REPAIR_AND_RESTORE_COMMAND = 'vm repair repair-and-restore'


class command_helper:
    """
    The command helper stores command state data and helper functions for vm-repair commands.
    It will also execute needed functions at the start and end of commands such as sending telemetry data
    and displaying progress controller
    """

    def __init__(self, logger, cmd, command_name):
        """
        The command helper object should always be initialized at the start of a command
        """
        # Start timer for custom telemetry
        self.start_time = timeit.default_timer()

        # Fetch and store command parameters
        self.command_params = _get_function_param_dict(inspect.getouterframes(inspect.currentframe())[1].frame)

        # Logger
        self.logger = logger

        # CLI cmd object
        self.cmd = cmd

        # Command name
        self.command_name = command_name

        # Init script data if command is vm repair run
        if command_name == VM_REPAIR_RUN_COMMAND:
            self.script = script_data()
            self.script.run_id = self.command_params['run_id']

        # Return message
        self.message = ''

        # Return error message
        self.error_message = ''

        # Return Status: STATUS_SUCCESS | STATUS_ERROR
        self.status = ''

        # Error stack trace
        self.error_stack_trace = ''

        # Return dict
        self.return_dict = {}

        # Resource shape used for telemetry. Commands populate this after fetching the source VM.
        self.os_family = None
        self.vm_size = None
        self.disk_controller_type = None
        self.repair_vm_disk_controller_type = None
        self.hyperv_generation = None

        # Verbose flag for command
        self.is_verbose = any(handler.level == logging.INFO for handler in get_logger().handlers)

        # Begin progress reporting for long running operation if not verbose
        if not self.is_verbose:
            self.cmd.cli_ctx.get_progress_controller().begin()
            self.cmd.cli_ctx.get_progress_controller().add(message='Running')

    def __del__(self):
        """
        This object will have the same life time as an invoked command.
        We will run all telemetry and clean-up work through the destructor.
        """

        # End long running op for process if not verbose
        if not self.is_verbose:
            self.cmd.cli_ctx.get_progress_controller().end()
        # Track telemetry data
        elapsed_time = timeit.default_timer() - self.start_time
        if self.command_name == VM_REPAIR_RUN_COMMAND:
            _track_run_command_telemetry(self.logger, self.command_name, self.command_params, self.status, self.message, self.error_message, self.error_stack_trace, elapsed_time, get_subscription_id(self.cmd.cli_ctx), self.return_dict, self.script.run_id, self.script.status, self.script.output, self.script.run_time, self.os_family, self.vm_size, self.disk_controller_type, self.repair_vm_disk_controller_type, self.hyperv_generation)
        elif self.command_name == VM_REPAIR_AND_RESTORE_COMMAND:
            _track_command_telemetry_repair_and_restore(self.logger, self.command_name, self.status, self.message, self.error_message, self.error_stack_trace, elapsed_time, get_subscription_id(self.cmd.cli_ctx), self.os_family, self.vm_size, self.disk_controller_type, self.repair_vm_disk_controller_type, self.hyperv_generation)
        else:
            _track_command_telemetry(self.logger, self.command_name, self.command_params, self.status, self.message, self.error_message, self.error_stack_trace, elapsed_time, get_subscription_id(self.cmd.cli_ctx), self.return_dict, self.os_family, self.vm_size, self.disk_controller_type, self.repair_vm_disk_controller_type, self.hyperv_generation)

    def set_resource_context(self, os_family=None, vm_size=None, disk_controller_type=None,
                             repair_vm_disk_controller_type=None, hyperv_generation=None):
        """Store resource-shape dimensions for telemetry without recording resource identity."""
        if os_family is not None:
            self.os_family = os_family
        if vm_size is not None:
            self.vm_size = vm_size
        if disk_controller_type is not None:
            self.disk_controller_type = disk_controller_type
        if repair_vm_disk_controller_type is not None:
            self.repair_vm_disk_controller_type = repair_vm_disk_controller_type
        if hyperv_generation is not None:
            self.hyperv_generation = hyperv_generation

    def set_status_success(self):
        """ Set command status to success """
        self.status = STATUS_SUCCESS

    def set_status_error(self):
        """ Set command status to error """
        self.status = STATUS_ERROR

    def is_status_success(self):
        return self.status == STATUS_SUCCESS

    def init_return_dict(self):
        """ Returns the command return dictionary """
        self.return_dict = {}
        self.return_dict["status"] = self.status
        self.return_dict["message"] = self.message
        if not self.is_status_success():
            self.return_dict["error_message"] = self.error_message
            if self.error_message:
                self.logger.error(self.error_message)
            if self.message:
                self.logger.error(self.message)

        return self.return_dict


class script_data:
    """ Stores repair script data. """
    def __init__(self):
        # Unique run-id
        self.run_id = ''

        # Script status
        self.status = ''

        # Script Output
        self.output = ''

        # Script run time
        self.run_time = None

    def set_status_success(self):
        """ Set command status to success """
        self.status = STATUS_SUCCESS

    def set_status_error(self):
        """ Set command status to error """
        self.status = STATUS_ERROR
