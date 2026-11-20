# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.aaz import has_value
from azure.cli.core.aaz.exceptions import AAZInvalidArgValueError
from azure.cli.core.azclierror import InvalidArgumentValueError

from ._create import Create
from ._show import Show
from ._update import Update


class _PasswordWrite:
    _arguments_schema = None
    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        schema = super()._build_arguments_schema(*args, **kwargs)
        password = schema.administrator_login_password
        validate = password._fmt  # pylint: disable=protected-access

        def validate_without_echo(ctx, value):
            try:
                return validate(ctx, value)
            except AAZInvalidArgValueError:
                # The default AAZ string-length error includes the supplied value.
                raise AAZInvalidArgValueError("Password must contain 8 to 128 characters.") from None

        password._fmt = validate_without_echo  # pylint: disable=protected-access
        return schema

    def _cli_arguments_loader(self):
        arguments = super()._cli_arguments_loader()
        password = dict(arguments)['administrator_login_password']

        class LiteralPasswordAction(password.type.settings['action']):
            # Do not interpret punctuation or AAZ shorthand in a password.
            decode_str = staticmethod(str)

        password.action = LiteralPasswordAction
        return arguments

    def _output(self, *args, **kwargs):
        if hasattr(self.ctx.vars, 'instance'):
            return super()._output(*args, **kwargs)
        # A successful async operation can finish without a resource body.
        return Show(cli_ctx=self.cli_ctx)(command_args={
            'subscription': self.ctx.subscription_id,
            'resource_group': self.ctx.args.resource_group.to_serialized_data(),
            'cluster_name': self.ctx.args.cluster_name.to_serialized_data(),
        })


class _NoBodyLogging:
    def __call__(self, *args, **kwargs):
        # CLI's network trace policy otherwise logs the entire request body under --debug.
        kwargs['logging_enable'] = False
        return super().__call__(*args, **kwargs)


class PasswordCreate(_PasswordWrite, Create):
    def pre_operations(self):
        args = self.ctx.args
        credentials_supplied = has_value(args.administrator_login) or has_value(args.administrator_login_password)
        if credentials_supplied and args.state != 'Enabled':
            raise InvalidArgumentValueError("Setting administrator credentials requires --state Enabled.")

    class PasswordAuthenticationsCreateOrReplace(_NoBodyLogging, Create.PasswordAuthenticationsCreateOrReplace):
        pass


class PasswordUpdate(_PasswordWrite, Update):
    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.administrator_login_password):
            if args.state == 'Disabled':
                raise InvalidArgumentValueError("A password reset cannot be combined with --state Disabled.")
        elif not has_value(args.state):
            raise InvalidArgumentValueError("Specify --state or --administrator-login-password.")

    class PasswordAuthenticationsUpdate(_NoBodyLogging, Update.PasswordAuthenticationsUpdate):
        pass
