
import os
import re
import json
import zipfile

WHEEL_INFO_RE = re.compile(
    r"""^(?P<namever>(?P<name>.+?)(-(?P<ver>\d.+?))?)
    ((-(?P<build>\d.*?))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)
    \.whl|\.dist-info)$""",
    re.VERBOSE).match

def _get_extension_modname(ext_dir):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L153
    EXTENSIONS_MOD_PREFIX = 'azext_'
    pos_mods = [n for n in os.listdir(ext_dir)
                if n.startswith(EXTENSIONS_MOD_PREFIX) and os.path.isdir(os.path.join(ext_dir, n))]
    if len(pos_mods) != 1:
        raise AssertionError("Expected 1 module to load starting with "
                             "'{}': got {}".format(EXTENSIONS_MOD_PREFIX, pos_mods))
    return pos_mods[0]


def _get_azext_metadata(ext_dir):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L109
    AZEXT_METADATA_FILENAME = 'azext_metadata.json'
    azext_metadata = None
    ext_modname = _get_extension_modname(ext_dir=ext_dir)
    azext_metadata_filepath = os.path.join(ext_dir, ext_modname, AZEXT_METADATA_FILENAME)
    if os.path.isfile(azext_metadata_filepath):
        with open(azext_metadata_filepath) as f:
            azext_metadata = json.load(f)
    return azext_metadata


def get_ext_metadata(ext_dir, ext_file, ext_name):
    # Modification of https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/extension.py#L89
    WHL_METADATA_FILENAME = 'metadata.json'
    zip_ref = zipfile.ZipFile(ext_file, 'r')
    zip_ref.extractall(ext_dir)
    zip_ref.close()
    metadata = {}
    dist_info_dirs = [f for f in os.listdir(ext_dir) if f.endswith('.dist-info')]

    azext_metadata = _get_azext_metadata(ext_dir)

    if not azext_metadata:
        raise ValueError('azext_metadata.json for Extension "{}" Metadata is missing'.format(ext_name))

    metadata.update(azext_metadata)

    for dist_info_dirname in dist_info_dirs:
        parsed_dist_info_dir = WHEEL_INFO_RE(dist_info_dirname)
        if parsed_dist_info_dir and parsed_dist_info_dir.groupdict().get('name') == ext_name.replace('-', '_'):
            whl_metadata_filepath = os.path.join(ext_dir, dist_info_dirname, WHL_METADATA_FILENAME)
            if os.path.isfile(whl_metadata_filepath):
                with open(whl_metadata_filepath) as f:
                    metadata.update(json.load(f))
    return metadata

import json
current_meta_dict = {}
with open("current_meta.json", "r") as current_meta:
    current_meta_dict = json.load(current_meta)
print(current_meta_dict)
print()
print()
from deepdiff import DeepDiff
new_meta_dict = get_ext_metadata('whl-test/temp', 'whl-test/azure_sphere-0.1.6-py2.py3-none-any.whl', 'azure-sphere')
with open("new_meta.json", "w") as new_meta:
    new_meta.write(json.dumps(new_meta_dict, indent=4))
print(new_meta_dict)
print()
print()
print(DeepDiff(current_meta_dict, new_meta_dict, ignore_order=True))