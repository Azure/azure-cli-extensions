# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from itertools import product
import json
import os
import subprocess
import tempfile
import time
import pytest
import docker

from azext_confcom.custom import acifragmentgen_confcom

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))
SAMPLES_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "..", "..", "samples"))


@pytest.fixture()
def docker_image():

    client = docker.from_env()

    registry_container = client.containers.run(
        image="registry:2",
        detach=True,
        ports={"5000/tcp": 0},
    )
    time.sleep(10) # TODO: Replace with polling
    registry_container.reload()
    registry_port = registry_container.attrs['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']

    test_container_repo = f"127.0.0.1:{registry_port}/hello-world"
    test_container_tag = "latest"
    test_container_ref = f"localhost:{registry_port}/hello-world:{test_container_tag}"
    client.images.pull("hello-world").tag(repository=test_container_repo, tag=test_container_tag)
    client.images.push(repository=test_container_repo, tag=test_container_tag)

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

    registry_container.stop()
    registry_container.remove()


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
        )

        oras_referrers = subprocess.run(
            ["oras", "discover", image_ref],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        ).stdout

        # Confirm the fragment is attached to the image
        assert "application/x-ms-ccepolicy-frag" in oras_referrers


def test_acifragmentgen_fragment_push(docker_image, cert_chain):

    image_ref, spec_file_path = docker_image
    fragment_ref = image_ref.replace("hello-world", "fragment")

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
            push_fragment_to=fragment_ref,
            output_filename=os.path.relpath(os.path.join(temp_dir, "fragment.rego"), os.getcwd()), # Must be relative for oras
        )

    # Confirm the fragment exists in the registry
    subprocess.run(
        ["oras", "discover", fragment_ref],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout


def test_acifragmentgen_fragment_attach(docker_image, cert_chain):

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
            attach_fragment_to=image_ref,
            output_filename=os.path.relpath(os.path.join(temp_dir, "fragment.rego"), os.getcwd()), # Must be relative for oras
        )

    oras_referrers = subprocess.run(
        ["oras", "discover", image_ref],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    ).stdout

    # Confirm the fragment is attached to the image
    assert "application/x-ms-ccepolicy-frag" in oras_referrers, oras_referrers
