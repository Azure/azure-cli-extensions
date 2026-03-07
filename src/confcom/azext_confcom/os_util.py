# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from typing import List, Union
import yaml
import yaml.scanner
import binascii
import shutil
import json
import os
import stat
from knack.log import get_logger
from tarfile import TarFile
from azext_confcom.errors import (
    eprint,
)

logger = get_logger(__name__)


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def str_to_base64(data: str) -> str:
    data_bytes = data.encode("ascii")
    return bytes_to_base64(data_bytes)


def base64_to_str(data: str) -> str:
    try:
        data_bytes = base64.b64decode(data)
        data_str = data_bytes.decode("ascii")
    except binascii.Error as e:
        raise ValueError(f"Invalid base64 string: {data}") from e
    return data_str


def clean_up_temp_folder(temp_file_path: str) -> None:
    # clean up the folder that the fragment was downloaded to
    folder_name = os.path.dirname(temp_file_path)
    logger.info("cleaning up folder with fragment: %s", folder_name)
    shutil.rmtree(folder_name)


def load_json_from_str(data: str) -> dict:
    if data:
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            eprint(f"Invalid json formatting for data: {data}")
    return {}


def load_json_from_file(path: str) -> dict:
    raw_data = load_str_from_file(path)
    return load_json_from_str(raw_data)


def load_yaml_from_str(data: str) -> dict:
    if data:
        try:
            return yaml.load(data, Loader=yaml.SafeLoader)
        except yaml.YAMLError:
            eprint(f"Invalid YAML formatting for data: {data}")
    return {}


def load_multiple_yaml_from_file(path: str) -> dict:
    raw_data = load_str_from_file(path)
    return load_multiple_yaml_from_str(raw_data)


def load_multiple_yaml_from_str(data: str) -> dict:
    if data:
        try:
            return list(yaml.safe_load_all(data))
        except yaml.YAMLError:
            eprint(f"Invalid YAML formatting for data: \n{data}")
    return {}


def load_yaml_from_file(path: str) -> dict:
    raw_data = load_str_from_file(path)
    return load_yaml_from_str(raw_data)


def copy_file(src: str, dest: str) -> None:
    try:
        shutil.copy(src, dest)
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
        eprint(f"File not found at path: {src}")


def load_str_from_file(path: str) -> str:
    if path:
        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read()
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError):
            eprint(f"File not found at path: {path}")
    return ""


def write_json_to_file(path: str, content: dict) -> None:
    write_str_to_file(
        path,
        json.dumps(
            content,
            indent=2,
        ),
    )


def write_multiple_yaml_to_file(path: str, content: List[dict]) -> None:
    write_str_to_file(
        path,
        yaml.dump_all(
            content
        ),
    )


def write_str_to_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def load_tar_mapping_from_file(path: str) -> dict:
    raw_json = load_json_from_file(path)
    json_path = os.path.dirname(path)

    # we want relative paths to be relative to where the mapping file is, not where the executing terminal is
    # so check if we have an absolute path and if not, append the relative path to the path of the mapping file
    for key, value in raw_json.items():
        if value != os.path.abspath(value):
            path = os.path.join(json_path, value)
            # error check that wherever the path leads, there is a tarball
            if not os.path.isfile(path):
                eprint(f"Tarball does not exist at path: {path}")
            raw_json[key] = path

    return raw_json


def load_tar_mapping_from_config_file(path: str) -> dict:
    raw_json = load_json_from_file(path)
    containers = raw_json.get("containers", [])
    output_dict = {}
    for container in containers:
        tar_path = container.get("path")
        if tar_path and not os.path.isfile(tar_path):
            eprint(f"Tarball does not exist at path: {tar_path}")
        image_name = container.get("properties", {}).get("image", "")
        output_dict[image_name] = tar_path
    return output_dict


def map_image_from_tar_backwards_compatibility(image_name: str, tar: TarFile, tar_location: str):
    tar_dir = os.path.dirname(tar_location)
    # grab all files in the folder and only take the one that's named with hex values and a json extension
    members = tar.getmembers()

    info_file = None
    # if there's more than one image in the tarball, we need to do some more logic
    if len(members) > 0:
        # extract just the manifest file and see if any of the RepoTags match the image_name we're searching for
        # the manifest.json should have a list of all the image tags
        # and what json files they map to to get env vars, startup cmd, etc.
        tar.extract("manifest.json", path=tar_dir)
        manifest_path = os.path.join(tar_dir, "manifest.json")
        manifest = load_json_from_file(manifest_path)
        # if we match a RepoTag to the image, stop searching
        for image in manifest:
            if image_name in image.get("RepoTags"):
                info_file = [
                    item for item in members if item.name == image.get("Config")
                ][0]
                break
        # remove the extracted manifest file to clean up
        force_delete_silently(manifest_path)
    else:
        eprint(f"Tarball at {tar_location} contains no images")

    if not info_file:
        return None
    tar.extract(info_file.name, path=tar_dir)

    # get the path of the json file and read it in
    image_info_file_path = os.path.join(tar_dir, info_file.name)
    image_info_raw = load_json_from_file(image_info_file_path)
    # delete the extracted json file to clean up
    force_delete_silently(image_info_file_path)
    image_info = image_info_raw.get("config")
    # importing the constant from config.py gives a circular dependency error
    image_info["Architecture"] = image_info_raw.get("architecture")

    shutil.rmtree("blobs", ignore_errors=True)
    return image_info


def get_oci_image_name(image_name: str) -> str:
    if "/" not in image_name:
        return f"docker.io/library/{image_name}"
    return image_name


def read_file_from_tar(tar: TarFile, filename: str) -> str:
    try:
        return tar.extractfile(filename).read()
    except KeyError:
        eprint(f"'{filename}' not found in tar file")


def map_image_from_tar_oci_layout_v1(image_name: str, tar: TarFile, tar_location: str):
    # since this uses containerd naming, we need to append the docker.io path
    oci_image_name = get_oci_image_name(image_name)

    index_bytes = read_file_from_tar(tar, "index.json")
    index = load_json_from_str(index_bytes)

    manifests = index.get("manifests") or []
    for manifest in manifests:
        image_annotations = manifest.get("annotations")
        image_name_annotation = ""
        if image_annotations:
            image_name_annotation = image_annotations.get("io.containerd.image.name")
            if image_name_annotation and image_name_annotation != oci_image_name:
                continue
        if (
            manifest.get("mediaType") in
            ["application/vnd.docker.distribution.manifest.v2+json", "application/vnd.oci.image.manifest.v1+json"]
        ):
            hashing_algo, manifest_name = manifest.get("digest").split(":")
            manifest_location = f"blobs/{hashing_algo}/{manifest_name}"

            nested_manifest_bytes = tar.extractfile(manifest_location).read()
            nested_manifest = load_json_from_str(nested_manifest_bytes)
            config = nested_manifest.get("config")

            config_hashing_algo, config_digest = config.get("digest").split(":")
            config_location = f"blobs/{config_hashing_algo}/{config_digest}"
            image_info_raw_bytes = tar.extractfile(config_location).read()
            image_info_raw = load_json_from_str(image_info_raw_bytes)
            image_info = image_info_raw.get("config")
            image_info["Architecture"] = image_info_raw.get("architecture")
            return image_info
    eprint(f"Image '{image_name}' is not found in '{tar_location}'")


def map_image_from_tar(image_name: str, tar: TarFile, tar_location: str):
    tar_dir = os.path.dirname(tar_location)
    info_file = None
    info_file_name = "manifest.json"

    # extract just the manifest file and see if any of the RepoTags match the image_name we're searching for
    # the manifest.json should have a list of all the image tags
    # and what json files they map to to get env vars, startup cmd, etc.
    tar.extract(info_file_name, path=tar_dir)
    manifest_path = os.path.join(tar_dir, info_file_name)
    manifest = load_json_from_file(manifest_path)
    try:
        # if we match a RepoTag to the image, stop searching
        for image in manifest:
            if image_name in image.get("RepoTags"):
                info_file = image.get("Config")
                break
    finally:
        # remove the extracted manifest file to clean up
        force_delete_silently(manifest_path)

    if not info_file:
        return None
    tar.extract(info_file, path=tar_dir)

    # get the path of the json file and read it in
    image_info_file_path = os.path.join(tar_dir, info_file)
    image_info_raw = load_json_from_file(image_info_file_path)
    # delete the extracted json file to clean up
    force_delete_silently(image_info_file_path)
    image_info = image_info_raw.get("config")
    # importing the constant from config.py gives a circular dependency error
    image_info["Architecture"] = image_info_raw.get("architecture")

    return image_info


# sometimes image tarfiles have readonly members. this will try to change their permissions and delete them
def force_delete_silently(filename: Union[str, list[str]]) -> None:
    if isinstance(filename, str):
        filename = [filename]
    for f in filename:
        try:
            os.chmod(f, stat.S_IWRITE)
        except FileNotFoundError:
            pass
        except PermissionError:
            eprint(f"Permission denied to edit file: {f}")
        except OSError as e:
            eprint(f"Error editing file: {f}, {e}")
        delete_silently(f)


# helper function to delete a file that may or may not exist
def delete_silently(filename: Union[str, list[str]]) -> None:
    if isinstance(filename, str):
        filename = [filename]
    for f in filename:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass
        except PermissionError:
            eprint(f"Permission denied to delete file: {f}")
        except OSError as e:
            eprint(f"Error deleting file: {f}, {e}")
