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
    ).stdout

    registry_port = subprocess.run(
        ["docker", "port", registry_id],
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.split(":")[-1].strip()

    test_container_ref = f"localhost:{registry_port}/hello-world:latest"
    subprocess.run(["docker", "pull", "hello-world"])
    subprocess.run(["docker", "tag", "hello-world", test_container_ref])
    subprocess.run(["docker", "push", test_container_ref])

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
    oras_result = subprocess.run(
        ["oras", "discover", image_ref, "--format", "json"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    print(f"{oras_result.decode('utf-8')=}")
    fragment_ref = json.loads(oras_result)["referrers"][0]["reference"]

    fragment_path = json.loads(subprocess.run(
        ["oras", "pull", fragment_ref, "--format", "json", "-o", "/tmp"],
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
        ["oras", "pull", fragment_ref, "--format", "json", "-o", "/tmp"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout)["files"][0]["path"]

    with open(fragment_path, "rb") as f:
        assert f.read() == signed_fragment


def test_acifragmentgen_fragment_attach(docker_image, cert_chain, capsysbinary):

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
    fragment_ref = json.loads(subprocess.run(
        ["oras", "discover", image_ref, "--format", "json"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout)["referrers"][0]["reference"]

    fragment_path = json.loads(subprocess.run(
        ["oras", "pull", fragment_ref, "--format", "json", "-o", "/tmp"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout)["files"][0]["path"]

    with open(fragment_path, "rb") as f:
        assert f.read() == signed_fragment
