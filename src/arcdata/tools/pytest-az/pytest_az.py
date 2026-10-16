# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------
# -*- coding: utf-8 -*-

from vcr import VCR

import json
import os
import ast
import pytest
from urllib.parse import urlparse
from types import SimpleNamespace

RECORD_MODES = {
    "rerecord": "rerecord",
    "replay": "once",
    "once": "once",
    "all": "all",
    "new_episodes": "new_episodes",
    "none": None,
}
"""
The different VCR modes.
"""

MOCK_CATALOG = {
    "host": "https://mock-host",
    "subscription": "a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39",
    "body": {
        "username": "username",
        "password": "Placeholder001",
        # -- Add more key/value POST body mocks when needed --
    },
}
"""
Catalog holding all mock name/values used in unit-testing.
"""


def pytest_addoption(parser):
    """
    Register argparse-style options and ini-style config values. This is called
    once at the beginning of a test run intended for helpful azure-cli testing
    features:
    - VCR.py simplifies and speeds up tests that make HTTP requests.
    - In-process az API
    """

    group = parser.getgroup("az_vcr")
    group.addoption(
        "--az-vcr-record",
        action="store",
        dest="az_record",
        default=None,
        choices=list(RECORD_MODES.keys()),
        help="Set the recording mode for VCR.py.",
    )

    group.addoption(
        "--disable-az-vcr",
        action="store_true",
        dest="disable_az",
        help="Run tests without playing back from VCR.py cassettes.",
    )


def pytest_load_initial_conftests(early_config, parser, args):
    early_config.addinivalue_line(
        "markers", "az_vcr: Mark the test as using `VCR.py`."
    )


def normalize_path(path, *paths):
    """
    Windows needs this sometimes when running the e2e tests from the
    `build unit-tests` task-runner. This can be slightly different than running
    from PyCharm/editor.
    """
    path = os.path.join(path, *paths)
    return path.replace("\\", "/")


@pytest.fixture(scope="module")
def az_vcr_config():
    """
    Custom configuration for `VCR.py`. Tests can use this fixture to override
    any VCR configurations. Default is to filter Authorisation headers and other
    sensitive information. Please see full configuration list:
    `https://vcrpy.readthedocs.io/en/latest/advanced.html`
    """

    def _mock_body(body):
        """
        Replace any sensitive info in the post body with mock value.
        """

        def _replace(obj, mock_key, mock_value):
            if mock_key in obj:
                obj[mock_key] = mock_value

            for k, v in obj.items():
                if isinstance(v, dict):
                    _replace(v, mock_key, mock_value)

        if body:
            # returned in bytes, here we convert to dict
            from vcr.filters import decode_response
            import gzip

            try:
                data = gzip.decompress(body)
                body = str(data, "utf-8")
                body = json.loads(body)
            except gzip.BadGzipFile:
                body = str(body, "utf-8")
                try:
                    body = json.loads(body)
                except Exception as e:
                    # application/x-www-form-urlencoded
                    return body

            for key in MOCK_CATALOG["body"]:
                # replace with mock value
                _replace(body, key, MOCK_CATALOG["body"][key])
            body = bytes(json.dumps(body), "utf8")
        return body

    def scrub_request(request):
        def _mock_uri(uri):
            """
            Replace real host with a "mock-host"
            """
            parsed_uri = urlparse(uri)
            if "subscriptions" in parsed_uri.path:
                split_uri = parsed_uri.path.split("/")
                index = split_uri.index("subscriptions") + 1

                u = MOCK_CATALOG["host"] + parsed_uri.path.replace(
                    "//", "/"
                ).replace(split_uri[index], MOCK_CATALOG["subscription"])

                if parsed_uri.query:
                    u = u + "?" + parsed_uri.query

                return u

            return MOCK_CATALOG["host"] + parsed_uri.path

        try:
            request.uri = _mock_uri(request.uri)
            request.body = _mock_body(request.body)
        except Exception as e:
            pass

        return request

    def scrub_response(response):
        try:
            if response["body"] and response["body"]["string"]:
                response["body"]["string"] = _mock_body(
                    response["body"]["string"]
                )
        except Exception as e:
            pass
        return response

    return {
        "filter_headers": ["authorization"],
        "before_record_request": scrub_request,
        "before_record_response": scrub_response,
    }


@pytest.fixture(autouse=True)
def _az_marker(request):
    """
    Defines the necessary pytest custom metadata marker.
    """

    marker = request.node.get_closest_marker("az_vcr")
    if marker:
        request.getfixturevalue("az_vcr_cassette")


@pytest.fixture(scope="module")
def az_vcr(request, az_vcr_config, az_vcr_cassette_dir):
    """
    The `VCR` instance used for all `az-cli` HTTP interactions.
    """

    kwargs = dict(
        cassette_library_dir=az_vcr_cassette_dir,
        path_transformer=VCR.ensure_suffix(".yaml"),
    )
    kwargs.update(az_vcr_config)
    _merge_vcr_kwargs(request, kwargs)

    return VCR(**kwargs)


@pytest.fixture
def az_vcr_cassette(request, az_vcr, az_vcr_cassette_file):
    """
    Wrap a az test function in a `VCR` cassette.
    """

    kwargs = {}
    _merge_vcr_kwargs(request, kwargs)
    cassette_name = az_vcr_cassette_file["name"]

    # -- drop old cassettes and rerecord --
    mode = kwargs.get("record_mode", kwargs.get(RECORD_MODES["rerecord"], None))
    mode = RECORD_MODES["once"] if mode == RECORD_MODES["replay"] else mode

    if mode == RECORD_MODES["rerecord"]:
        VCRState().record_mode = mode
        cassette = az_vcr_cassette_file["cassette"]
        if os.path.exists(cassette):
            os.remove(cassette)

    if os.path.exists(az_vcr_cassette_file["cassette"]):
        VCRState().cassette_exists = True

    with az_vcr.use_cassette(cassette_name, **kwargs) as cassette:
        yield cassette


@pytest.fixture(scope="module")
def az_vcr_cassette_dir(request):
    """
    Fixture for pointing to the recorded cassette assets directory.
    """

    return os.path.join(request.node.fspath.dirname, "cassettes")


@pytest.fixture
def az_vcr_cassette_file(request, az_vcr_cassette_dir):
    """
    Fixture defining the name of the `VCR` and full-path location of the
    cassette.
    """

    test_class = request.cls
    if test_class:
        name = "{}.{}".format(test_class.__name__, request.node.name)
    else:
        name = request.node.name

    return {
        "name": name,
        "cassette": os.path.join(az_vcr_cassette_dir, name) + ".yaml",
    }


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class VCRState(object):
    """
    Holds VCR state information across fixtures.
    """

    def __init__(self):
        self._record_mode = RECORD_MODES["once"]
        self._cassette_exists = False

    @property
    def record_mode(self):
        return self._record_mode

    @record_mode.setter
    def record_mode(self, record_mode):
        self._record_mode = record_mode

    @property
    def cassette_exists(self):
        return self._cassette_exists

    @cassette_exists.setter
    def cassette_exists(self, cassette_exists):
        self._cassette_exists = cassette_exists


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def _to_dot_notation(d):
    class _Namespace(SimpleNamespace):
        @property
        def to_dict(self):
            class _Encoder(json.JSONEncoder):
                def default(self, o):
                    return o.__dict__

            return json.loads(json.dumps(self, indent=4, cls=_Encoder))

    return json.loads(
        json.dumps(d), object_hook=lambda item: _Namespace(**item)
    )


@pytest.fixture
def mock_constants():
    # Add more here when needed
    return _to_dot_notation(MOCK_CATALOG)


@pytest.fixture
def mock_kube_config():
    """
    Fixture for helping to create repeated mock `.kube` configurations.

    usage:

    ```
    def test_fn(mock_kube_config):
       mock_kube_config()  # apply default mock
       mock_kube_config(config="/path/to/.kube")  # apply custom override mock
    ```
    """

    def beget(config=normalize_path(os.path.dirname(__file__), "kube_config")):
        os.environ["KUBECONFIG"] = config

    return beget


@pytest.fixture
def mock_az_profile(monkeypatch):
    """
    Fixture for helping to create repeated mock `az profile` configurations for
    authentication purposes post VRC record.

    usage:

    ```
    def test_fn(mock_az_profile):
       mock_az_profile()  # apply default mock
    ```
    """

    class _AzureCliCredentialMock(object):
        def get_token(self, *scopes: str, **kwargs: any):
            class _AccessTokenMock(object):
                token = "JWT_TOKEN_MOCK"
                expires_on = 4500
                expires_in = 4500

            return _AccessTokenMock()

    def _get_azure_credentials_mock():
        return {
            "credentials": _AzureCliCredentialMock(),
            "subscription": MOCK_CATALOG["subscription"],
            "expires_on": 4500,
        }

    def beget():
        monkeypatch.setattr(
            "azext_arcdata.core.services.ArmMixin.get_azure_credentials",
            lambda az_cli: _get_azure_credentials_mock(),
        )

    return beget


@pytest.fixture
def az(mock_kube_config, mock_az_profile, capsys):
    """
    Fixture for making az-cli invocations from the same process easy.
    """

    class AzCliResponse(object):
        SUCCESS = 0
        """
        Exit code that means a successful process exit.
        """

        FAILURE = 1
        """
        Exit code that means a catchall for general process errors.
        """

        ARGUMENT_REQUIRED_ERROR = 2
        """
        Exit code that means a CLI argument is required but not provided.
        """

        def __init__(self):
            self._out_err = {"stdout": "", "stderr": ""}
            self.exit_code = AzCliResponse.SUCCESS

        @property
        def exit_code(self):
            return self._exit_code

        @exit_code.setter
        def exit_code(self, exit_code):
            self._exit_code = exit_code

        @property
        def out(self):
            return self._out_err["stdout"]

        @out.setter
        def out(self, out):
            self._out_err["stdout"] = out

        @property
        def err(self):
            return self._out_err["stderr"]

        @err.setter
        def err(self, err):
            self._out_err["stderr"] = err

        def to_dict(self):
            import json

            try:
                return {
                    "out": json.loads(self.out) if self.out else None,
                    "err": (
                        json.loads(self.err.strip("ERROR:"))
                        if self.err
                        else None
                    ),
                }
            except json.JSONDecodeError:
                return None

    def run(command, expect_failure=False, disable_vcr=False, **kwargs):
        """
        The az-cli command with optional arguments to run.

        Test success:
        ```
        def test_app_list(az)
           res = az('app list --name my-app')
           assert res.exit_code == 0
           assert res.output == '[]'

        def test_app_list(az)
           res = az('app list', name='my-app')
           assert res.exit_code == 0
           assert res.output == '[]'
        ```
        ```

        Test failures:
        ```
        def test_app_list(az)
           res = az('app list --name my-app', expect_failure=True)
           assert res.exit_code == 1
           assert res.output = 'some failure in stderr'
        ```

        Commands that do not need VRC:
        ```
        def test_cmd_with_no_http_calls(az)
           res = az('cmd --arg 1', disable_vcr=True)
           assert res.exit_code == 0
        ```

        :param command: The command with optional arguments.
        :param disable_vcr: To disable cassette recording in VCR. Default is
                           set to `True`.
        :param expect_failure: Catch expected errors for test and supply a
                               return value.
        :return: The `AzCliResponse` otherwise error.
        """
        from azure.cli.core import get_default_cli as az_cli
        import io
        import shlex

        # let az know about this extension from repo location
        ext = normalize_path(os.path.dirname(__file__), "..", "..")
        os.environ["AZURE_EXTENSION_DIR"] = ext

        # if a cassette already exists and recorded, make sure to apply mock
        st = VCRState()
        if disable_vcr or (
            st.record_mode != RECORD_MODES["rerecord"] and st.cassette_exists
        ):
            mock_kube_config()  # default
            mock_az_profile()  # default

        stdout_buf = io.StringIO()
        response = AzCliResponse()
        command = command[3:] if command.startswith("az ") else command

        # -- combine arbitrary arguments (hello=world ===>  --hello world) --
        args = []
        for arg, value in kwargs.items():
            if value is None:
                continue
            args.append("--{0} {1}".format(arg.replace("_", "-"), value))

        if args:
            command = "{0} {1}".format(command, " ".join(args))

        try:
            az = az_cli()
            response.exit_code = (
                az.invoke(shlex.split(command), out_file=stdout_buf)
                or AzCliResponse.SUCCESS
            )

            if response.exit_code == AzCliResponse.SUCCESS:
                if stdout_buf.getvalue() and stdout_buf.getvalue() != "":
                    response.out = stdout_buf.getvalue()
                else:
                    response.out = capsys.readouterr().out
            else:
                response.err = az.result.error

            return response
        except SystemExit as e:
            if (
                e.code == AzCliResponse.ARGUMENT_REQUIRED_ERROR
                and expect_failure
            ):
                response.exit_code = e.code
                response.out = stdout_buf.getvalue() or capsys.readouterr().err
                return response
            else:
                raise e

        # pylint: disable=broad-except
        except (KeyboardInterrupt, Exception) as e:
            if expect_failure:
                response.exit_code = AzCliResponse.FAILURE
                response.out = stdout_buf.getvalue() or capsys.readouterr().err
                return response
            else:
                raise e
        finally:
            stdout_buf.close()

    return run


# ------------------------------------------------------------------------------
# -- Private helpers                                                          --
# ------------------------------------------------------------------------------


def _merge_vcr_kwargs(request, kwargs):
    marker = request.node.get_closest_marker("az_vcr")
    record_mode = request.config.getoption("--az-vcr-record")

    if marker:
        if record_mode == RECORD_MODES["rerecord"]:
            marker.kwargs["record_mode"] = record_mode
        kwargs.update(marker.kwargs)
    else:
        record_mode = request.config.getoption("--az-vcr-record")
        if record_mode:
            kwargs["record_mode"] = record_mode

    if request.config.getoption("--disable-az-vcr"):
        kwargs["record_mode"] = "new_episodes"
        kwargs["before_record_response"] = lambda *args, **kwargs: None


def _to_dot_notation(d):
    class _Namespace(SimpleNamespace):
        @property
        def to_dict(self):
            class _Encoder(json.JSONEncoder):
                def default(self, o):
                    return o.__dict__

            return json.loads(json.dumps(self, indent=4, cls=_Encoder))

    return json.loads(
        json.dumps(d), object_hook=lambda item: _Namespace(**item)
    )
