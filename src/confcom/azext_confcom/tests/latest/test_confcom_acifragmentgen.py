# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import contextlib
import io
import json
import os
import subprocess
import tempfile
from unittest.mock import MagicMock, patch
import pytest

from azext_confcom.custom import acifragmentgen_confcom, fragment_push, fragment_attach

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
SAMPLES_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples"))


@pytest.fixture()
def docker_image():

    registry_id = subprocess.run(
        ["docker", "run", "-d", "-p", "0:5000", "registry:2"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()

    registry_port = subprocess.run(
        ["docker", "port", registry_id],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.split(":")[-1].strip()

    test_container_ref = f"localhost:{registry_port}/hello-world:latest"
    subprocess.run(["docker", "pull", "hello-world"], check=True)
    subprocess.run(["docker", "tag", "hello-world", test_container_ref], check=True)
    subprocess.run(["docker", "push", test_container_ref], check=True)

    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=True) as temp_file:
        json.dump({
            "version": "1.0.0",
            "containers": [
                {
                    "name": "hello-world",
                    "properties": {
                        "image": test_container_ref,
                    },
                }
            ]
        }, temp_file)
        temp_file.flush()

        yield test_container_ref, temp_file.name

    subprocess.run(["docker", "stop", registry_id])


@pytest.fixture(scope="session")
def cert_chain():
    with tempfile.TemporaryDirectory() as temp_dir:
        subprocess.run(
            [
                os.path.join(SAMPLES_DIR, "certs", "create_certchain.sh"),
                temp_dir
            ],
            check=True,
        )
        yield temp_dir


def test_acifragmentgen_fragment_gen(docker_image):

    image_ref, spec_file_path = docker_image

    with tempfile.TemporaryDirectory() as temp_dir: # Prevent test writing files to repo
        acifragmentgen_confcom(
            image_name=None,
            tar_mapping_location=None,
            key=None,
            chain=None,
            minimum_svn=None,
            input_path=spec_file_path,
            svn="1",
            namespace="contoso",
            feed="test-feed",
            outraw=True,
            output_filename=os.path.join(temp_dir, "fragment.rego"),
            out_signed_fragment=False,
        )

    # TODO: Implement a proper validation for the fragment, this is hard
    # because each test run will have a unique image to have unique local
    # registries on different ports


def test_acifragmentgen_fragment_sign(docker_image, cert_chain):

    image_ref, spec_file_path = docker_image

    with tempfile.TemporaryDirectory() as temp_dir: # Prevent test writing files to repo
        acifragmentgen_confcom(
            image_name=None,
            tar_mapping_location=None,
            key=os.path.join(cert_chain, "intermediateCA", "private", "ec_p384_private.pem"),
            chain=os.path.join(cert_chain, "intermediateCA", "certs", "www.contoso.com.chain.cert.pem"),
            minimum_svn=None,
            input_path=spec_file_path,
            svn="1",
            namespace="contoso",
            feed="test-feed",
            outraw=True,
            output_filename=os.path.join(temp_dir, "fragment.rego"),
            out_signed_fragment=False,
        )

    # TODO: Implement a proper validation for the cose document


def test_acifragmentgen_fragment_upload_fragment(docker_image, cert_chain):

    image_ref, spec_file_path = docker_image

    with tempfile.TemporaryDirectory() as temp_dir: # Prevent test writing files to repo
        acifragmentgen_confcom(
            image_name=None,
            tar_mapping_location=None,
            key=os.path.join(cert_chain, "intermediateCA", "private", "ec_p384_private.pem"),
            chain=os.path.join(cert_chain, "intermediateCA", "certs", "www.contoso.com.chain.cert.pem"),
            minimum_svn=None,
            input_path=spec_file_path,
            svn="1",
            namespace="contoso",
            feed="test-feed",
            outraw=True,
            upload_fragment=True,
            output_filename=os.path.relpath(os.path.join(temp_dir, "fragment.rego"), os.getcwd()), # Must be relative for oras
            out_signed_fragment=False,
        )

    # Confirm the fragment exists and is attached in the registry
    oras_result = json.loads(subprocess.run(
        ["oras", "discover", image_ref, "--format", "json"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout)

    if "referrers" in oras_result:
        fragment_ref = oras_result["referrers"][0]["reference"]
    elif oras_result.get("manifests")[0].get("artifactType") == "application/x-ms-ccepolicy-frag":
        fragment_ref = oras_result["manifests"][0]["reference"]
    else:
        raise AssertionError(f"{oras_result=}")

    fragment_path = json.loads(subprocess.run(
        ["oras", "pull", fragment_ref, "--format", "json", "-o", tempfile.gettempdir()],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout)["files"][0]["path"]


    with open(fragment_path, "rb") as actual_fragment_file:
        with open(os.path.join(temp_dir, "fragment.rego.cose"), "rb") as expected_fragment_file:
            assert actual_fragment_file.read() == expected_fragment_file.read()


def test_acifragmentgen_fragment_push(docker_image, cert_chain, capsysbinary):

    image_ref, spec_file_path = docker_image
    fragment_ref = image_ref.replace("hello-world", "fragment")

    acifragmentgen_confcom(
        image_name=None,
        tar_mapping_location=None,
        key=os.path.join(cert_chain, "intermediateCA", "private", "ec_p384_private.pem"),
        chain=os.path.join(cert_chain, "intermediateCA", "certs", "www.contoso.com.chain.cert.pem"),
        minimum_svn=None,
        input_path=spec_file_path,
        svn="1",
        namespace="contoso",
        feed="test-feed",
        out_signed_fragment=True,
    )

    signed_fragment = capsysbinary.readouterr()[0]
    signed_fragment_io = io.BytesIO(signed_fragment)
    signed_fragment_io.name = "<stdin>"

    fragment_push(
        signed_fragment=signed_fragment_io,
        manifest_tag=fragment_ref,
    )

    # Confirm the fragment exists in the registry
    fragment_path = json.loads(subprocess.run(
        ["oras", "pull", fragment_ref, "--format", "json", "-o", tempfile.gettempdir()],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout)["files"][0]["path"]

    with open(fragment_path, "rb") as f:
        assert f.read() == signed_fragment


# ── Unit tests for prepend_docker_registry ─────────────────────────────────


def test_prepend_docker_registry_official_image():
    """Official image names get docker.io/library/ prepended."""
    from azext_confcom.oras_proxy import prepend_docker_registry
    assert prepend_docker_registry("nginx:latest") == "docker.io/library/nginx:latest"
    assert prepend_docker_registry("alpine") == "docker.io/library/alpine"


def test_prepend_docker_registry_user_image():
    """User-scoped image names get docker.io/ prepended."""
    from azext_confcom.oras_proxy import prepend_docker_registry
    assert prepend_docker_registry("user/image:tag") == "docker.io/user/image:tag"


def test_prepend_docker_registry_custom_registry():
    """Images already referencing a registry are left unchanged."""
    from azext_confcom.oras_proxy import prepend_docker_registry
    assert prepend_docker_registry("myregistry.io/image:tag") == "myregistry.io/image:tag"
    assert prepend_docker_registry("gcr.io/project/image:latest") == "gcr.io/project/image:latest"


def test_prepend_docker_registry_localhost():
    """localhost references are left unchanged."""
    from azext_confcom.oras_proxy import prepend_docker_registry
    assert prepend_docker_registry("localhost:5000/image:tag") == "localhost:5000/image:tag"


# ── Unit tests for get_image_platforms ─────────────────────────────────────

_MANIFEST_LIST_RESPONSE = {
    "mediaType": "application/vnd.oci.image.index.v1+json",
    "content": {
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "manifests": [
            {"platform": {"architecture": "amd64", "os": "linux"}},
            {"platform": {"architecture": "arm64", "os": "linux"}},
        ],
    },
}

_SINGLE_MANIFEST_RESPONSE = {
    "content": {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "layers": [],
    },
}

_SINGLE_MANIFEST_CONFIG = {
    "architecture": "amd64",
    "os": "linux",
}


@patch("azext_confcom.oras_proxy.manifest_fetch", return_value=_MANIFEST_LIST_RESPONSE)
def test_get_image_platforms_manifest_list(mock_fetch):
    """Multi-platform manifest lists return all known platforms."""
    # Note that when we use mocks, we must (re-)import extension modules at call
    # time for the mocks to work, due to reloading in conftest.py run_on_wheel.
    from azext_confcom.oras_proxy import get_image_platforms

    platforms = get_image_platforms("myregistry.io/myimage:latest")
    assert set(platforms) == {"linux/amd64", "linux/arm64"}


@patch(
    "azext_confcom.oras_proxy.manifest_fetch_config",
    return_value=_SINGLE_MANIFEST_CONFIG,
)
@patch(
    "azext_confcom.oras_proxy.manifest_fetch", return_value=_SINGLE_MANIFEST_RESPONSE
)
def test_get_image_platforms_single_manifest(mock_fetch, mock_fetch_config):
    """Single-platform manifests fall back to manifest-config detection."""
    from azext_confcom.oras_proxy import get_image_platforms

    platforms = get_image_platforms("myregistry.io/myimage:latest")
    assert platforms == ["linux/amd64"]


@patch("azext_confcom.oras_proxy.manifest_fetch", return_value=None)
def test_get_image_platforms_fetch_failure(mock_fetch):
    """When manifest_fetch returns None, an empty list is returned."""
    from azext_confcom.oras_proxy import get_image_platforms

    platforms = get_image_platforms("myregistry.io/myimage:latest")
    assert platforms == []


@patch(
    "azext_confcom.oras_proxy.manifest_fetch",
    return_value={
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "content": {
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "manifests": [
                {"platform": {"architecture": "amd64", "os": "linux"}},
                # attestation-style entry with unknown/unknown platform
                {"platform": {"architecture": "unknown", "os": "unknown"}},
            ],
        },
    },
)
def test_get_image_platforms_unknown_platform_excluded(mock_fetch):
    """Platforms with unknown/unknown architecture and OS are excluded."""
    from azext_confcom.oras_proxy import get_image_platforms

    platforms = get_image_platforms("myregistry.io/myimage:latest")
    assert platforms == ["linux/amd64"]


# ── Unit tests for oras_attach ─────────────────────────────────────────────


@patch("azext_confcom.command.fragment_attach.subprocess.run")
@patch(
    "azext_confcom.command.fragment_attach.oras_proxy.get_image_platforms",
    return_value=["linux/amd64", "linux/arm64"],
)
def test_oras_attach_multiarch_error(mock_platforms, mock_run):
    """oras_attach raises SystemExit when multiple platforms are detected and no platform specified."""
    # Note that when we use mocks, we must (re-)import extension modules at call
    # time for the mocks to work, due to reloading in conftest.py run_on_wheel.
    from azext_confcom.command.fragment_attach import oras_attach

    mock_fragment = MagicMock()
    mock_fragment.name = "/tmp/fragment.cose"
    with pytest.raises(SystemExit):
        oras_attach(
            signed_fragment=mock_fragment, manifest_tag="myregistry.io/myimage:latest"
        )
    mock_run.assert_not_called()


@patch("azext_confcom.command.fragment_attach.subprocess.run")
@patch(
    "azext_confcom.command.fragment_attach.oras_proxy.get_image_platforms",
    return_value=[],
)
def test_oras_attach_detection_failure_error(mock_platforms, mock_run):
    """oras_attach raises SystemExit when platform detection fails (empty list)."""
    from azext_confcom.command.fragment_attach import oras_attach

    mock_fragment = MagicMock()
    mock_fragment.name = "/tmp/fragment.cose"
    with pytest.raises(SystemExit):
        oras_attach(
            signed_fragment=mock_fragment, manifest_tag="myregistry.io/myimage:latest"
        )
    mock_run.assert_not_called()


@patch("azext_confcom.command.fragment_attach.subprocess.run")
def test_oras_attach_explicit_platform(mock_run):
    """When platform is explicitly supplied, oras attach is called with --platform."""
    from azext_confcom.command.fragment_attach import oras_attach

    mock_run.return_value = MagicMock(returncode=0)
    mock_fragment = MagicMock()
    mock_fragment.name = "/tmp/fragment.cose"

    oras_attach(
        signed_fragment=mock_fragment,
        manifest_tag="myregistry.io/myimage:latest",
        platform="linux/amd64",
    )

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "--platform" in cmd
    assert "linux/amd64" in cmd
    assert "application/cose-x509+rego" in " ".join(cmd)


@patch("azext_confcom.command.fragment_attach.subprocess.run")
@patch(
    "azext_confcom.command.fragment_attach.oras_proxy.get_image_platforms",
    return_value=["linux/amd64"],
)
def test_oras_attach_auto_detected_platform(mock_platforms, mock_run):
    """When no platform is supplied, the detected platform is passed to oras attach."""
    from azext_confcom.command.fragment_attach import oras_attach

    mock_run.return_value = MagicMock(returncode=0)
    mock_fragment = MagicMock()
    mock_fragment.name = "/tmp/fragment.cose"

    oras_attach(
        signed_fragment=mock_fragment,
        manifest_tag="myregistry.io/myimage:latest",
    )

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "--platform" in cmd
    assert "linux/amd64" in cmd
    assert "application/cose-x509+rego" in " ".join(cmd)


def test_acifragmentgen_fragment_attach_with_explicit_platform(
    docker_image, cert_chain, capsysbinary
):
    """fragment_attach with an explicit --platform parameter attaches successfully."""
    image_ref, spec_file_path = docker_image

    acifragmentgen_confcom(
        image_name=None,
        tar_mapping_location=None,
        key=os.path.join(
            cert_chain, "intermediateCA", "private", "ec_p384_private.pem"
        ),
        chain=os.path.join(
            cert_chain, "intermediateCA", "certs", "www.contoso.com.chain.cert.pem"
        ),
        minimum_svn=None,
        input_path=spec_file_path,
        svn="1",
        namespace="contoso",
        feed="test-feed",
        out_signed_fragment=True,
    )

    signed_fragment = capsysbinary.readouterr()[0]
    signed_fragment_io = io.BytesIO(signed_fragment)
    signed_fragment_io.name = "<stdin>"

    fragment_attach(
        signed_fragment=signed_fragment_io,
        manifest_tag=image_ref,
        platform="linux/amd64",
    )

    oras_result = json.loads(
        subprocess.run(
            ["oras", "discover", image_ref, "--format", "json"],
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
    )

    if "referrers" in oras_result:
        fragment_ref = oras_result["referrers"][0]["reference"]
    elif (
        oras_result.get("manifests")
        and oras_result["manifests"][0].get("artifactType")
        == "application/x-ms-ccepolicy-frag"
    ):
        fragment_ref = oras_result["manifests"][0]["reference"]
    else:
        raise AssertionError(f"{oras_result=}")

    fragment_path = json.loads(
        subprocess.run(
            [
                "oras",
                "pull",
                fragment_ref,
                "--format",
                "json",
                "-o",
                tempfile.gettempdir(),
            ],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
    )["files"][0]["path"]

    with open(fragment_path, "rb") as f:
        assert f.read() == signed_fragment


def test_acifragmentgen_upload_fragment_multiarch_error(docker_image, cert_chain):
    """acifragmentgen --upload-fragment exits with an error for multiarch images."""
    # Note that when we use mocks, we must (re-)import extension modules at call
    # time for the mocks to work, due to reloading in conftest.py run_on_wheel.
    from azext_confcom.custom import acifragmentgen_confcom as _acifragmentgen

    image_ref, spec_file_path = docker_image

    with patch(
        "azext_confcom.custom.oras_proxy.get_image_platforms",
        return_value=["linux/amd64", "linux/arm64"],
    ):
        with pytest.raises(SystemExit):
            with tempfile.TemporaryDirectory() as temp_dir:
                _acifragmentgen(
                    image_name=None,
                    tar_mapping_location=None,
                    key=os.path.join(
                        cert_chain, "intermediateCA", "private", "ec_p384_private.pem"
                    ),
                    chain=os.path.join(
                        cert_chain,
                        "intermediateCA",
                        "certs",
                        "www.contoso.com.chain.cert.pem",
                    ),
                    minimum_svn=None,
                    input_path=spec_file_path,
                    svn="1",
                    namespace="contoso",
                    feed="test-feed",
                    outraw=True,
                    upload_fragment=True,
                    output_filename=os.path.relpath(
                        os.path.join(temp_dir, "fragment.rego"), os.getcwd()
                    ),
                    out_signed_fragment=False,
                )


def test_acifragmentgen_upload_fragment_no_platform_fallback(docker_image, cert_chain):
    """acifragmentgen --upload-fragment falls back to linux/amd64 when platform detection fails."""
    from azext_confcom.custom import acifragmentgen_confcom as _acifragmentgen

    image_ref, spec_file_path = docker_image

    with patch(
        "azext_confcom.custom.oras_proxy.get_image_platforms", return_value=[]
    ), patch("azext_confcom.custom.oras_proxy.attach_fragment_to_image") as mock_attach:
        with tempfile.TemporaryDirectory() as temp_dir:
            _acifragmentgen(
                image_name=None,
                tar_mapping_location=None,
                key=os.path.join(
                    cert_chain, "intermediateCA", "private", "ec_p384_private.pem"
                ),
                chain=os.path.join(
                    cert_chain,
                    "intermediateCA",
                    "certs",
                    "www.contoso.com.chain.cert.pem",
                ),
                minimum_svn=None,
                input_path=spec_file_path,
                svn="1",
                namespace="contoso",
                feed="test-feed",
                outraw=True,
                upload_fragment=True,
                output_filename=os.path.relpath(
                    os.path.join(temp_dir, "fragment.rego"), os.getcwd()
                ),
                out_signed_fragment=False,
            )

        mock_attach.assert_called_once()
        _, kwargs = mock_attach.call_args
        assert kwargs.get("platform") == "linux/amd64"


def test_acifragmentgen_fragment_attach_without_platform(docker_image, cert_chain, capsysbinary):

    image_ref, spec_file_path = docker_image

    acifragmentgen_confcom(
        image_name=None,
        tar_mapping_location=None,
        key=os.path.join(cert_chain, "intermediateCA", "private", "ec_p384_private.pem"),
        chain=os.path.join(cert_chain, "intermediateCA", "certs", "www.contoso.com.chain.cert.pem"),
        minimum_svn=None,
        input_path=spec_file_path,
        svn="1",
        namespace="contoso",
        feed="test-feed",
        out_signed_fragment=True,
    )

    signed_fragment = capsysbinary.readouterr()[0]
    signed_fragment_io = io.BytesIO(signed_fragment)
    signed_fragment_io.name = "<stdin>"

    fragment_attach(
        signed_fragment=signed_fragment_io,
        manifest_tag=image_ref,
    )

    # Confirm the fragment exists and is attached in the registry
    oras_result = json.loads(subprocess.run(
        ["oras", "discover", image_ref, "--format", "json"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout)

    if "referrers" in oras_result:
        fragment_ref = oras_result["referrers"][0]["reference"]
    elif oras_result["manifests"][0].get("artifactType") == "application/x-ms-ccepolicy-frag":
        fragment_ref = oras_result["manifests"][0]["reference"]
    else:
        raise AssertionError(f"{oras_result=}")

    fragment_path = json.loads(subprocess.run(
        ["oras", "pull", fragment_ref, "--format", "json", "-o", tempfile.gettempdir()],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout)["files"][0]["path"]

    with open(fragment_path, "rb") as f:
        assert f.read() == signed_fragment
