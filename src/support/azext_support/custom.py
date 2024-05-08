# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals

from datetime import date, datetime, timedelta

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
        from azure.cli.core.aaz import AAZUndefined

        super().pre_operations()
        args = self.ctx.args
        if args.technical_resource != AAZUndefined:
            _validate_tickets_create(
                self.cli_ctx,
                str(args.problem_classification),
                str(args.ticket_name),
                str(args.technical_resource),
            )
        else:
            _validate_tickets_create(
                self.cli_ctx, str(args.problem_classification), str(args.ticket_name)
            )

    class SupportTicketsCreate(_CreateTicket.SupportTicketsCreate):

        @property
        def content(self):
            from azure.cli.core.aaz import AAZUndefined

            body = super().content
            args = self.ctx.args
            service_name = parse_support_area_path(
                body["properties"]["problemClassificationId"]
            )["service_name"]
            body["properties"]["serviceId"] = (
                "/providers/Microsoft.Support/services/{0}".format(service_name)
            )
            if args.start_time == AAZUndefined:
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
        from azure.cli.core.aaz import AAZUndefined

        super().pre_operations()
        args = self.ctx.args
        if args.technical_resource != AAZUndefined:
            _validate_tickets_create_no_subscription(
                self.cli_ctx,
                str(args.problem_classification),
                str(args.ticket_name),
                str(args.technical_resource),
            )
        else:
            _validate_tickets_create_no_subscription(
                self.cli_ctx, str(args.problem_classification), str(args.ticket_name)
            )

    class SupportTicketsNoSubscriptionCreate(
        _CreateTicketNoSubscription.SupportTicketsNoSubscriptionCreate
    ):

        @property
        def content(self):
            from azure.cli.core.aaz import AAZUndefined

            body = super().content
            args = self.ctx.args
            service_name = parse_support_area_path(
                body["properties"]["problemClassificationId"]
            )["service_name"]
            body["properties"]["serviceId"] = (
                "/providers/Microsoft.Support/services/{0}".format(service_name)
            )
            if args.start_time == AAZUndefined:
                start_time = datetime.utcnow().strftime(("%Y-%m-%dT%H:%M:%SZ"))
                body["properties"]["problemStartTime"] = start_time
            return body


class TicketList(_List):

    class SupportTicketsList(_List.SupportTicketsList):

        @property
        def query_parameters(self):
            from azure.cli.core.aaz import AAZUndefined

            parameters = super().query_parameters
            args = self.ctx.args
            if args.filter == AAZUndefined and args.pagination_limit == AAZUndefined:
                parameters["$filter"] = "CreatedDate ge " + str(
                    date.today() - timedelta(days=7)
                )
            return parameters


class TicketListNoSubscription(_ListNoSubscription):

    class SupportTicketsNoSubscriptionList(
        _ListNoSubscription.SupportTicketsNoSubscriptionList
    ):

        @property
        def query_parameters(self):
            from azure.cli.core.aaz import AAZUndefined

            parameters = super().query_parameters
            args = self.ctx.args
            if args.filter == AAZUndefined and args.pagination_limit == AAZUndefined:
                parameters["$filter"] = "CreatedDate ge " + str(
                    date.today() - timedelta(days=7)
                )
            return parameters


class CommunicationCreate(_CreateCommunication):

    def pre_operations(self):
        from azext_support._validators import (
            _check_name_availability_subscription_ticket,
        )

        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_subscription_ticket(
            self.cli_ctx,
            str(args.ticket_name),
            str(args.communication_name),
            "Microsoft.Support/communications",
        )


class CommunicationNoSubscriptionCreate(_CreateNoSubscriptionCommunication):

    def pre_operations(self):
        from azext_support._validators import (
            _check_name_availability_no_subscription_ticket,
        )

        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_no_subscription_ticket(
            self.cli_ctx,
            str(args.ticket_name),
            str(args.communication_name),
            "Microsoft.Support/communications",
        )


class FileWorkspaceCreateNoSubscription(_CreateNoSubscriptionFileWorkspace):

    def pre_operations(self):
        from azext_support._validators import _check_name_availability_no_subscription

        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_no_subscription(
            self.cli_ctx,
            str(args.file_workspace_name),
            "Microsoft.Support/fileWorkspaces",
        )


class FileWorkspaceCreateSubscription(_CreateFileWorkspace):

    def pre_operations(self):
        from azext_support._validators import _check_name_availability_subscription

        super().pre_operations()
        args = self.ctx.args
        _check_name_availability_subscription(
            self.cli_ctx,
            str(args.file_workspace_name),
            "Microsoft.Support/fileWorkspaces",
        )


def upload_files_no_subscription(cmd, file_path, file_workspace_name):

    from .aaz.latest.support.no_subscription.file import (
        Create,
        Upload,
    )

    upload_file(cmd, file_path, file_workspace_name, Create, Upload)


def upload_files_in_subscription(
    cmd, file_path, file_workspace_name
):
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
