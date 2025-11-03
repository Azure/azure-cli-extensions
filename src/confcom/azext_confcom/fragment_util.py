# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
from typing import List

import yaml
from azext_confcom import config, oras_proxy
from azext_confcom.errors import eprint
from azext_confcom.template_util import (case_insensitive_dict_get,
                                         extract_containers_from_text,
                                         extract_namespace_from_text,
                                         extract_svn_from_text)
from knack.log import get_logger

logger = get_logger(__name__)


def sanitize_fragment_fields(fragments_list: List[dict]) -> List[dict]:
    fields_to_keep = [
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED,
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN,
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_INCLUDES,
        config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_ISSUER
    ]
    out_list = copy.deepcopy(fragments_list)
    for fragment in out_list:
        keys_to_remove = [key for key in fragment.keys() if key not in fields_to_keep]
        for key in keys_to_remove:
            fragment.pop(key, None)
    return out_list


# input is the full rego file as a string
# output is all of the containers in the rego files as a list of dictionaries
def combine_fragments_with_policy(all_fragments):
    out_fragments = []
    for fragment in all_fragments:
        container_text = extract_containers_from_text(fragment, "containers := ")
        container_text = container_text.replace("\t", "    ")
        containers = yaml.load(container_text, Loader=yaml.FullLoader)
        out_fragments.extend(containers)
    return out_fragments


def get_all_fragment_contents(
    image_names: List[str],
    fragment_imports: List[dict],
) -> List[str]:
    # was getting errors with pass by reference so we need to copy it
    remaining_fragments = copy.deepcopy(fragment_imports)

    def remove_from_list_via_feed(fragment_import_list, feed):
        for i, fragment_import in enumerate(fragment_import_list):
            if fragment_import.get("feed") == feed:
                fragment_import_list.pop(i)

    all_fragments_contents = []
    # get all the image attached fragments
    for image in image_names:
        # TODO: make sure this doesn't error out if the images aren't in a registry.
        # This will probably be in the discover function
        image_attached_fragments, feeds = oras_proxy.pull_all_image_attached_fragments(image)
        for fragment, feed in zip(image_attached_fragments, feeds):
            all_feeds = [
                case_insensitive_dict_get(temp_fragment, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_FEED)
                for temp_fragment in remaining_fragments
            ]
            feed_idx = all_feeds.index(feed) if feed in all_feeds else -1

            if feed_idx != -1:
                import_statement = remaining_fragments[feed_idx]

                if (
                    int(
                        case_insensitive_dict_get(
                            import_statement, config.POLICY_FIELD_CONTAINERS_ELEMENTS_REGO_FRAGMENTS_MINIMUM_SVN
                        )
                    ) <= extract_svn_from_text(fragment)
                ):
                    remove_from_list_via_feed(remaining_fragments, feed)
                    all_fragments_contents.append(fragment)
            else:
                logger.warning("Fragment feed %s not in list of feeds to use. Skipping fragment.", feed)
    # grab the remaining fragments which should be standalone
    standalone_fragments, _ = oras_proxy.pull_all_standalone_fragments(remaining_fragments)
    all_fragments_contents.extend(standalone_fragments)

    # make sure there aren't conflicts in the namespaces
    namespaces = set()
    for fragment in all_fragments_contents:
        namespace = extract_namespace_from_text(fragment)
        if namespace in namespaces:
            eprint("Duplicate namespace found: %s. This may cause issues.", namespace)
        namespaces.add(namespace)

    return combine_fragments_with_policy(all_fragments_contents)
