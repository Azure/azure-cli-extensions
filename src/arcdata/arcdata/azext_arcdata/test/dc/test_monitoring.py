import base64
from typing import Dict, List
import io
from azext_arcdata.core.util import generate_certificate_and_key
from azext_arcdata.kubernetes_sdk.client import KubernetesClient
import urllib3
from azext_arcdata.core.constants import (
    DEFAULT_LOGSUI_CERT_SECRET_NAME,
    DEFAULT_METRICSUI_CERT_SECRET_NAME,
    LOGSUI_USERNAME,
    LOGSUI_PASSWORD,
    METRICSUI_USERNAME,
    METRICSUI_PASSWORD,
    AZDATA_USERNAME,
    AZDATA_PASSWORD,
)
from azext_arcdata.kubernetes_sdk.dc.constants import (
    LOGSUI_LOGIN_SECRET_NAME,
    METRICSUI_LOGIN_SECRET_NAME,
)

from pytest_az import VCRState, RECORD_MODES
from tempfile import TemporaryDirectory

import os
import pytest
import random
import string

VCR_RECORD_MODE = "once"  # options: None, once, all, rerecord
NAMESPACE = "arc"
TEST_PASSWORD = (
    "a"
    + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    + "aB1"
)


@pytest.mark.usefixtures("setup")
class TestMonitoring(object):
    @pytest.fixture
    def setup(self, az_vcr_cassette, mock_kube_config):
        st = VCRState()
        if st.record_mode != RECORD_MODES["rerecord"] and st.cassette_exists:
            mock_kube_config()

    @pytest.fixture
    def mock_dc_create(self, monkeypatch):
        def _prompt_pass_mock(msg: str, password: str):
            print(msg)
            return password

        monkeypatch.setattr(
            "knack.prompting.prompt_pass",
            lambda msg, confirm: _prompt_pass_mock(msg, "AAAbbb1234"),
        )
        monkeypatch.setattr(
            "azext_arcdata.core.kubernetes.is_instance_ready",
            lambda *args, **kwargs: True,
        )
        monkeypatch.setattr(
            "azext_arcdata.kubernetes_sdk.dc.client.DataControllerClient._dc_create",
            lambda *args, **kwargs: (None, None),
        )
        monkeypatch.setattr(
            "azext_arcdata.kubernetes_sdk.dc.client.DataControllerClient._await_dc_ready",
            lambda *args, **kwargs: (None, None),
        )

    @pytest.fixture
    def mock_dc_arm_create(self, monkeypatch):
        monkeypatch.setattr(
            "azext_arcdata.arm_sdk.client.ArmClient.create_dc",
            lambda *args, **kwargs: (None, None),
        )

    @pytest.fixture
    def mock_create_secret(self, monkeypatch):
        monkeypatch.setattr(
            "azext_arcdata.kubernetes_sdk.client.KubernetesClient.create_secret",
            lambda *args, **kwargs: True,
        )

    @pytest.fixture
    def mock_tty(self, monkeypatch):
        newio = io.StringIO(
            "telemtryadmin\n{0}\n{1}\n1".format(TEST_PASSWORD, TEST_PASSWORD)
        )
        monkeypatch.setattr("sys.stdin", newio)
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    @pytest.fixture
    def mock_no_tty(self, monkeypatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    @pytest.mark.skip(
        reason="Skipping to check in version change for release while under investigation."
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_dc_create_env_vars_tty(
        self, mock_dc_create, mock_create_secret, mock_tty, az
    ):
        metrics_prompts = [
            "Metrics administrator username:",
            "Metrics administrator password:",
        ]
        logs_prompts = [
            "Logs administrator username:",
            "Logs administrator password:",
        ]
        azdata_prompts = [
            "Monitoring administrator username:",
            "Monitoring administrator password",
        ]
        all_prompts = metrics_prompts + logs_prompts + azdata_prompts
        telemetry_prompts = metrics_prompts + logs_prompts

        def _check_out_text(a: List[str], none: List[str], results):
            assert all(m in results.out for m in a)
            assert not any(m in results.out for m in none)

        # -- Logsui vars set
        self._set_dashboard_env_vars(logs_user="admin", logs_pass=TEST_PASSWORD)
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text(metrics_prompts, logs_prompts + azdata_prompts, results)

        # -- metricsui vars set
        self._set_dashboard_env_vars(
            metrics_user="admin", metrics_pass=TEST_PASSWORD
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text(logs_prompts, metrics_prompts + azdata_prompts, results)

        # -- metricsui and azdata vars set
        self._set_dashboard_env_vars(
            metrics_user="admin",
            metrics_pass=TEST_PASSWORD,
            azdata_user="admin",
            azdata_pass=TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_prompts, results)

        # -- logsui and azdata vars set
        self._set_dashboard_env_vars(
            logs_user="admin",
            logs_pass=TEST_PASSWORD,
            azdata_user="admin",
            azdata_pass=TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_prompts, results)

        # -- azdata vars set
        self._set_dashboard_env_vars(
            azdata_user="admin", azdata_pass=TEST_PASSWORD
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_prompts, results)

        # -- telemetry vars set
        self._set_dashboard_env_vars(
            metrics_user="admin",
            metrics_pass=TEST_PASSWORD,
            logs_user="admin",
            logs_pass=TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_prompts, results)

        # -- all vars set
        self._set_dashboard_env_vars(
            "admin",
            TEST_PASSWORD,
            "admin",
            TEST_PASSWORD,
            "admin",
            TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_prompts, results)

        # -- no vars set, prompts for azdata username/password
        self._set_dashboard_env_vars()
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text(azdata_prompts, telemetry_prompts, results)

    @pytest.mark.skip(
        reason="Skipping to check in version change for release while under investigation."
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_dc_create_env_vars_no_tty(
        self, mock_dc_create, mock_create_secret, mock_no_tty, az
    ):
        metrics_vars = [METRICSUI_USERNAME, METRICSUI_PASSWORD]
        logs_vars = [LOGSUI_USERNAME, LOGSUI_PASSWORD]
        azdata_vars = [AZDATA_USERNAME, AZDATA_PASSWORD]
        all_vars = metrics_vars + logs_vars + azdata_vars
        telemetry_vars = metrics_vars + logs_vars

        def _check_out_text(a: List[str], none: List[str], results):
            assert all(m in str(results.err) for m in a)
            assert not any(m in str(results.err) for m in none)

        # -- Logsui vars set
        self._set_dashboard_env_vars(logs_user="admin", logs_pass=TEST_PASSWORD)
        results = az(self._get_dc_create_str())
        assert results.exit_code == 1
        _check_out_text(metrics_vars + azdata_vars, logs_vars, results)

        # -- metricsui vars set
        self._set_dashboard_env_vars(
            metrics_user="admin", metrics_pass=TEST_PASSWORD
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 1
        _check_out_text(logs_vars + azdata_vars, metrics_vars, results)

        # -- metricsui and azdata vars set
        self._set_dashboard_env_vars(
            metrics_user="admin",
            metrics_pass=TEST_PASSWORD,
            azdata_user="admin",
            azdata_pass=TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_vars, results)

        # -- logsui and azdata vars set
        self._set_dashboard_env_vars(
            logs_user="admin",
            logs_pass=TEST_PASSWORD,
            azdata_user="admin",
            azdata_pass=TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_vars, results)

        # -- azdata vars set
        self._set_dashboard_env_vars(
            azdata_user="admin", azdata_pass=TEST_PASSWORD
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_vars, results)

        # -- telemetry vars set
        self._set_dashboard_env_vars(
            metrics_user="admin",
            metrics_pass=TEST_PASSWORD,
            logs_user="admin",
            logs_pass=TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_vars, results)

        # -- all vars set
        self._set_dashboard_env_vars(
            "admin",
            TEST_PASSWORD,
            "admin",
            TEST_PASSWORD,
            "admin",
            TEST_PASSWORD,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0
        _check_out_text([], all_vars, results)

        # -- no vars set, prompts for azdata username/password
        self._set_dashboard_env_vars()
        results = az(self._get_dc_create_str())
        assert results.exit_code == 1
        _check_out_text(azdata_vars, telemetry_vars, results)

    @pytest.mark.skip(
        reason="Skipping to check in version change for release while under investigation."
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_dc_create_env_vars_full_create(
        self, monkeypatch, az, mock_constants
    ):
        monkeypatch.setattr(
            "azext_arcdata.kubernetes_sdk.dc.client.DataControllerClient._dc_create",
            lambda *args, **kwargs: (None, None),
        )
        monkeypatch.setattr(
            "azext_arcdata.kubernetes_sdk.dc.client.DataControllerClient._await_dc_ready",
            lambda *args, **kwargs: (None, None),
        )
        LOGSUI_PASS = "AAAbbb1234"
        METRICSUI_PASS = "AAAbbb12345"

        # -- All telemetry vars set
        self._set_dashboard_env_vars(
            metrics_user="admin",
            metrics_pass=METRICSUI_PASS,
            logs_user="admin2",
            logs_pass=LOGSUI_PASS,
        )
        results = az(self._get_dc_create_str())
        assert results.exit_code == 0

        logsui_secret = KubernetesClient.get_secret(
            "test", LOGSUI_LOGIN_SECRET_NAME
        )
        logsui_creds = logsui_secret.data

        expected_username = mock_constants.body.username
        expected_password = mock_constants.body.password

        # Bcause the pytest az plugin mocks sensitive info like
        # username/password the encode/decode behavior this test is expecting
        # will break since the mocked values are not encoded. Here we just
        # encode them since that is the real behavior for the assertion.
        logsui_creds["username"] = base64.b64encode(
            logsui_creds["username"].encode("ascii")
        )
        logsui_creds["password"] = base64.b64encode(
            logsui_creds["password"].encode("ascii")
        )

        assert self.decode_data(logsui_creds["username"]) == expected_username
        assert self.decode_data(logsui_creds["password"]) == expected_password

        metricsui_secret = KubernetesClient.get_secret(
            "test", METRICSUI_LOGIN_SECRET_NAME
        )
        metricsui_creds = metricsui_secret.data

        # Bcause the pytest az plugin mocks sensitive info like
        # username/password the encode/decode behavior this test is expecting
        # will break since the mocked values are not encoded. Here we just
        # encode them since that is the real behavior for the assertion.
        metricsui_creds["username"] = base64.b64encode(
            metricsui_creds["username"].encode("ascii")
        )
        metricsui_creds["password"] = base64.b64encode(
            metricsui_creds["password"].encode("ascii")
        )

        assert (
            self.decode_data(metricsui_creds["username"]) == expected_username
        )
        assert (
            self.decode_data(metricsui_creds["password"]) == expected_password
        )

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    @pytest.mark.parametrize(
        "arguments, should_fail, expected_error",
        [
            (
                "--logs-ui-private-key-file file1",
                True,
                "Logsui certificate public key file path must be provided "
                "when private key file is provided.",
            ),
            (
                "--logs-ui-public-key-file file1",
                True,
                "Logsui certificate private key file path must be provided "
                "when public key file is provided.",
            ),
            (
                "--metrics-ui-private-key-file file1",
                True,
                "Metricsui certificate public key file path must be provided "
                "when private key file is provided.",
            ),
            (
                "--metrics-ui-public-key-file file1",
                True,
                "Metricsui certificate private key file path must be provided "
                "when public key file is provided.",
            ),
        ],
    )
    def test_dc_create_missing_args(
        self,
        monkeypatch,
        mock_dc_create,
        mock_create_secret,
        az,
        arguments,
        should_fail,
        expected_error,
    ):
        self._set_dashboard_env_vars(
            "admin", "AAAbbb1234", "admin", "AAAbbb1234", "admin", "AAAbbb1234"
        )
        results = az("{0} {1}".format(self._get_dc_create_str(), arguments))
        assert results.exit_code == 1 if should_fail else 0

        if should_fail:
            assert expected_error in str(results.err)

    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_dc_create_mutually_exclusive_monitor_arguments(
        self,
        monkeypatch,
        mock_dc_create,
        mock_create_secret,
        mock_dc_arm_create,
        az,
    ):
        self._set_dashboard_env_vars(
            "admin", "AAAbbb1234", "admin", "AAAbbb1234", "admin", "AAAbbb1234"
        )
        results = az(
            "{0} {1} {2} {3}".format(
                self._get_dc_create_str(use_k8s=False, namespace=None),
                "--custom-location foo",
                "--logs-ui-public-key-file file1",
                "--logs-ui-private-key-file file2",
            )
        )
        assert results.exit_code == 1
        assert (
            "Monitoring endpoint certificate arguments are for indirect mode only."
            in str(results.err)
        )

        results = az(
            "{0} {1} {2} {3}".format(
                self._get_dc_create_str(use_k8s=False, namespace=None),
                "--custom-location foo",
                "--metrics-ui-public-key-file file1",
                "--metrics-ui-private-key-file file2",
            )
        )
        assert results.exit_code == 1
        assert (
            "Monitoring endpoint certificate arguments are for indirect mode only."
            in str(results.err)
        )

    @pytest.mark.skip(
        reason="This test uses random credentials which make cassettes unusable."
    )
    @pytest.mark.az_vcr(record_mode=VCR_RECORD_MODE)
    def test_mock_create_with_valid_certs_succeeds(self, monkeypatch, az):
        def create_certificate_files(
            public_key_pem: str,
            private_key_pem: str,
            tmp_dir: TemporaryDirectory,
        ):
            cert_file = open(
                os.path.join(tmp_dir, "certificate.pem"), "wb"
            )  # note: 'b' opens the file in binary mode
            cert_file.write(public_key_pem)
            cert_file.close()
            private_key_file = open(
                os.path.join(tmp_dir, "privatekey.pem"), "wb"
            )
            private_key_file.write(private_key_pem)
            private_key_file.close()

            return cert_file, private_key_file

        self._set_dashboard_env_vars(
            "admin", "AAAbbb1234", "admin", "AAAbbb1234", "admin", "AAAbbb1234"
        )

        (
            logsui_cert_pem,
            logsui_key_pem,
            logsui_fp,
        ) = generate_certificate_and_key(
            "logsui-external-svc.test.svc.cluster.local",
            "logsui-svc",
            sans=["logsui-svc"],
        )
        (
            metricsui_cert_pem,
            metricsui_key_pem,
            metricsui_fp,
        ) = generate_certificate_and_key(
            "metricsui-external-svc.test.svc.cluster.local",
            "metricsui-svc",
            sans=["metricsui-svc"],
        )

        # Creating temporary directories in a context ensures their cleanup functions are called
        #
        with TemporaryDirectory() as logsui_tmp_dir, TemporaryDirectory() as metricsui_tmp_dir:
            # Create certificate files for logs and metrics in different tmp dirs
            #
            logsui_cert_file, logsui_key_file = create_certificate_files(
                logsui_cert_pem, logsui_key_pem, logsui_tmp_dir
            )
            metricsui_cert_file, metricsui_key_file = create_certificate_files(
                metricsui_cert_pem, metricsui_key_pem, metricsui_tmp_dir
            )

            # Create dc with logs and metrics certificate arguments
            #
            az(
                "{0} {1} {2} {3} {4}".format(
                    self._get_dc_create_str(),
                    "{0} {1}".format(
                        "--logs-ui-private-key-file", logsui_key_file.name
                    ),
                    "{0} {1}".format(
                        "--logs-ui-public-key-file", logsui_cert_file.name
                    ),
                    "{0} {1}".format(
                        "--metrics-ui-private-key-file", metricsui_key_file.name
                    ),
                    "{0} {1}".format(
                        "--metrics-ui-public-key-file", metricsui_cert_file.name
                    ),
                )
            )

            # Verify provided certificate data is present in the certificate secrets
            #
            logsui_secret = KubernetesClient.get_secret(
                "test", DEFAULT_LOGSUI_CERT_SECRET_NAME
            )
            logsui_creds = logsui_secret.data
            assert (
                base64.b64decode(logsui_creds["certificate.pem"])
                == logsui_cert_pem
            )
            assert (
                base64.b64decode(logsui_creds["privatekey.pem"])
                == logsui_key_pem
            )

            # Verify provided certificate data is present in the certificate secrets
            #
            metricsui_secret = KubernetesClient.get_secret(
                "test", DEFAULT_METRICSUI_CERT_SECRET_NAME
            )
            metricsui_creds = metricsui_secret.data
            assert (
                base64.b64decode(metricsui_creds["certificate.pem"])
                == metricsui_cert_pem
            )
            assert (
                base64.b64decode(metricsui_creds["privatekey.pem"])
                == metricsui_key_pem
            )

            monitor = KubernetesClient.get_namespaced_custom_object(
                "monitorstack",
                "test",
                group="arcdata.microsoft.com",
                version="v1beta1",
                plural="monitors",
            )
            logsui_endpoint = monitor["status"]["logSearchDashboard"]

            headers = urllib3.make_headers(
                basic_auth="{0}:{1}".format("admin", "AAAbbb1234")
            )
            http = urllib3.PoolManager(
                ca_certs=logsui_cert_file.name, assert_hostname=False
            )
            resp = http.request("GET", logsui_endpoint, headers=headers)
            assert resp.status == 200

            import ssl

            ssl.get_server_certificate(
                logsui_endpoint[:-1].replace("//", "").split(":")[1:]
            )

            try:
                http = urllib3.PoolManager(assert_hostname=False)
                resp = http.request("GET", logsui_endpoint, headers=headers)
                assert False
            except Exception:
                assert True

    def _get_dc_create_str(self, use_k8s=True, namespace="test"):
        args = """
            --name datacontroller-alias-12345eee8
            --subscription a5082b19-8a6e-4bc5-8fdd-8ef39dfebc39
            --resource-group GCI
            --location eastus
            --connectivity-mode indirect
            --profile azure-arc-unit-test"""

        if use_k8s:
            args += " --use-k8s"

        if namespace:
            args += " --k8s-namespace {0}".format(namespace)

        return "arcdata dc create {0}".format(args)

    def _set_dashboard_env_vars(
        self,
        logs_user="",
        logs_pass="",
        metrics_user="",
        metrics_pass="",
        azdata_user="",
        azdata_pass="",
    ):

        os.environ[LOGSUI_USERNAME] = logs_user
        os.environ[LOGSUI_PASSWORD] = logs_pass
        os.environ[METRICSUI_USERNAME] = metrics_user
        os.environ[METRICSUI_PASSWORD] = metrics_pass
        os.environ[AZDATA_USERNAME] = azdata_user
        os.environ[AZDATA_PASSWORD] = azdata_pass

    def decode_data(self, secret_data: str):
        return str(base64.b64decode(secret_data), "utf-8")
