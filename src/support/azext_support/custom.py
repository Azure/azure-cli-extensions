# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

from datetime import date, datetime, timedelta
from azure.cli.core.aaz import has_value

from azext_support._utils import (
    parse_support_area_path,
    upload_file,
)
from azext_support._completers import (
    _get_supported_languages as getLanguage,
    _get_supported_timezones as getTimeZone,
)
from knack.log import get_logger
from .aaz.latest.support.in_subscription.tickets import Update as _Update
from .aaz.latest.support.no_subscription.tickets import Update as _UpdateNoSubscription
from .aaz.latest.support.in_subscription.tickets import Create as _CreateTicket
from .aaz.latest.support.no_subscription.tickets import (
    Create as _CreateTicketNoSubscription,
)
from .aaz.latest.support.in_subscription.tickets import List as _List
from .aaz.latest.support.no_subscription.tickets import List as _ListNoSubscription
from .aaz.latest.support.in_subscription.communication import (
    Create as _CreateCommunication,
)
from .aaz.latest.support.no_subscription.communication import (
    Create as _CreateNoSubscriptionCommunication,
)
from .aaz.latest.support.in_subscription.file_workspace import (
    Create as _CreateFileWorkspace,
)
from .aaz.latest.support.no_subscription.file_workspace import (
    Create as _CreateNoSubscriptionFileWorkspace,
)

logger = get_logger(__name__)


def set_configured_defaults(args):
    for arg_name, arg in args:
        if arg_name == "contact_language":
            arg.completer = getLanguage()
        if arg_name == "contact_timezone":
            arg.completer = getTimeZone()
    return args


class TicketUpdate(_Update):

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class TicketUpdateNoSubscription(_UpdateNoSubscription):

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)


class TicketCreate(_CreateTicket):

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)

    def pre_operations(self):
        from azext_support._validators import _validate_tickets_create

        args = self.ctx.args
        if has_value(args.technical_resource):
            _validate_tickets_create(
                self.cli_ctx,
                args.problem_classification.to_serialized_data(),
                args.ticket_name.to_serialized_data(),
                args.technical_resource.to_serialized_data(),
            )
        else:
            _validate_tickets_create(
                self.cli_ctx,
                args.problem_classification.to_serialized_data(),
                args.ticket_name.to_serialized_data(),
            )

    class SupportTicketsCreate(_CreateTicket.SupportTicketsCreate):

        @property
        def content(self):

            body = super().content
            args = self.ctx.args
            service_name = parse_support_area_path(
                body["properties"]["problemClassificationId"]
            )["service_name"]
            body["properties"]["serviceId"] = (
                "/providers/Microsoft.Support/services/{0}".format(service_name)
            )
            if not has_value(args.start_time):
                start_time = datetime.utcnow().strftime(("%Y-%m-%dT%H:%M:%SZ"))
                body["properties"]["problemStartTime"] = start_time
            return body


class TicketCreateNoSubscription(_CreateTicketNoSubscription):

    def _cli_arguments_loader(self):
        args = super()._cli_arguments_loader()
        return set_configured_defaults(args)

    def pre_operations(self):
        from azext_support._validators import (
            _validate_tickets_create_no_subscription,
        )

        args = self.ctx.args
        if has_value(args.technical_resource):
            _validate_tickets_create_no_subscription(
                self.cli_ctx,
                args.problem_classification.to_serialized_data(),
                args.ticket_name.to_serialized_data(),
                args.technical_resource.to_serialized_data(),
            )
        else:
            _validate_tickets_create_no_subscription(
                self.cli_ctx,
                args.problem_classification.to_serialized_data(),
                args.ticket_name.to_serialized_data(),
            )

    class SupportTicketsNoSubscriptionCreate(
        _CreateTicketNoSubscription.SupportTicketsNoSubscriptionCreate
    ):

        @property
        def content(self):

            body = super().content
            args = self.ctx.args
            service_name = parse_support_area_path(
                body["properties"]["problemClassificationId"]
            )["service_name"]
            body["properties"]["serviceId"] = (
                "/providers/Microsoft.Support/services/{0}".format(service_name)
            )
            if not has_value(args.start_time):
                start_time = datetime.utcnow().strftime(("%Y-%m-%dT%H:%M:%SZ"))
                body["properties"]["problemStartTime"] = start_time
            return body


class TicketList(_List):

    def pre_operations(self):

        args = self.ctx.args
        if not has_value(args.filter) and not has_value(args.pagination_limit):
            args.filter = "CreatedDate ge " + str(date.today() - timedelta(days=7))


class TicketListNoSubscription(_ListNoSubscription):

    def pre_operations(self):

        args = self.ctx.args
        if not has_value(args.filter) and not has_value(args.pagination_limit):
            args.filter = "CreatedDate ge " + str(date.today() - timedelta(days=7))


class CommunicationCreate(_CreateCommunication):

    def pre_operations(self):
        from azext_support._validators import (
            _check_name_availability_subscription_ticket,
        )

        args = self.ctx.args
        _check_name_availability_subscription_ticket(
            self.cli_ctx,
            args.ticket_name.to_serialized_data(),
            args.communication_name.to_serialized_data(),
            "Microsoft.Support/communications",
        )


class CommunicationNoSubscriptionCreate(_CreateNoSubscriptionCommunication):

    def pre_operations(self):
        from azext_support._validators import (
            _check_name_availability_no_subscription_ticket,
        )

        args = self.ctx.args
        _check_name_availability_no_subscription_ticket(
            self.cli_ctx,
            args.ticket_name.to_serialized_data(),
            args.communication_name.to_serialized_data(),
            "Microsoft.Support/communications",
        )


class FileWorkspaceCreateNoSubscription(_CreateNoSubscriptionFileWorkspace):

    def pre_operations(self):
        from azext_support._validators import _check_name_availability_no_subscription

        args = self.ctx.args
        _check_name_availability_no_subscription(
            self.cli_ctx,
            args.file_workspace_name.to_serialized_data(),
            "Microsoft.Support/fileWorkspaces",
        )


class FileWorkspaceCreateSubscription(_CreateFileWorkspace):

    def pre_operations(self):
        from azext_support._validators import _check_name_availability_subscription

        args = self.ctx.args
        _check_name_availability_subscription(
            self.cli_ctx,
            args.file_workspace_name.to_serialized_data(),
            "Microsoft.Support/fileWorkspaces",
        )


def upload_files_no_subscription(cmd, file_path, file_workspace_name):

    from .aaz.latest.support.no_subscription.file import (
        Create,
        Upload,
    )

    upload_file(cmd, file_path, file_workspace_name, Create, Upload)


def upload_files_in_subscription(cmd, file_path, file_workspace_name):
    from .aaz.latest.support.in_subscription.file import (
        Create as Create_Sub,
        Upload as Upload_Sub,
    )

    upload_file(
        cmd,
        file_path,
        file_workspace_name,
        Create_Sub,
        Upload_Sub,
    )
