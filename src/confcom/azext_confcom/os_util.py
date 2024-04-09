# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import binascii
import shutil
import json
import os
from tarfile import TarFile
from azext_confcom.errors import (
    eprint,
)


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def str_to_base64(data: str) -> str:
    data_bytes = data.encode("ascii")
    return bytes_to_base64(data_bytes)


def base64_to_str(data: str) -> str:
    try:
        data_bytes = base64.b64decode(data)
        data_str = data_bytes.decode("ascii")
    except binascii.Error:
        eprint(f"Invalid base64 string: {data}")
    return data_str


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


def map_image_from_tar_backwards_compatibility(image_name: str, tar: TarFile, tar_location: str):
    tar_dir = os.path.dirname(tar_location)
    # grab all files in the folder and only take the one that's named with hex values and a json extension
    members = tar.getmembers()
    info_file_name = [
        file
        for file in members
        if file.name.endswith(".json") and not file.name.startswith("manifest")
    ]
    info_file = None
    # if there's more than one image in the tarball, we need to do some more logic
    if len(info_file_name) > 0:
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
                    item for item in info_file_name if item.name == image.get("Config")
                ][0]
                break
        # remove the extracted manifest file to clean up
        os.remove(manifest_path)
    else:
        eprint(f"Tarball at {tar_location} contains no images")

    if not info_file:
        return None
    tar.extract(info_file.name, path=tar_dir)

    # get the path of the json file and read it in
    image_info_file_path = os.path.join(tar_dir, info_file.name)
    image_info_raw = load_json_from_file(image_info_file_path)
    # delete the extracted json file to clean up
    os.remove(image_info_file_path)
    image_info = image_info_raw.get("config")
    # importing the constant from config.py gives a circular dependency error
    image_info["Architecture"] = image_info_raw.get("architecture")

    return image_info


def map_image_from_tar(image_name: str, tar: TarFile, tar_location: str):
    tar_dir = os.path.dirname(tar_location)
    info_file = None
    info_file_name = "manifest.json"
    # if there's more than one image in the tarball, we need to do some more logic
    if len(info_file_name) > 0:
        # extract just the manifest file and see if any of the RepoTags match the image_name we're searching for
        # the manifest.json should have a list of all the image tags
        # and what json files they map to to get env vars, startup cmd, etc.
        tar.extract(info_file_name, path=tar_dir)
        manifest_path = os.path.join(tar_dir, info_file_name)
        manifest = load_json_from_file(manifest_path)
        # if we match a RepoTag to the image, stop searching
        for image in manifest:
            if image_name in image.get("RepoTags"):
                info_file = image.get("Config")
                break
        # remove the extracted manifest file to clean up
        os.remove(manifest_path)
    else:
        eprint(f"Tarball at {tar_location} contains no images")

    if not info_file:
        return None
    tar.extract(info_file, path=tar_dir)

    # get the path of the json file and read it in
    image_info_file_path = os.path.join(tar_dir, info_file)
    image_info_raw = load_json_from_file(image_info_file_path)
    # delete the extracted json file to clean up
    os.remove(image_info_file_path)
    image_info = image_info_raw.get("config")
    # importing the constant from config.py gives a circular dependency error
    image_info["Architecture"] = image_info_raw.get("architecture")

    return image_info
