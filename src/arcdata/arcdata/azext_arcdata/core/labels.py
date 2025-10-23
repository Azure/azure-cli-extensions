# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

__all__ = ["parse_labels"]


def parse_labels(label_str):
    labels = dict()
    labels_split = label_str.split(",")

    for label_raw in labels_split:
        label_kv = label_raw.split(":")

        if len(label_kv) != 2:
            raise ValueError(
                "Labels must be of form 'key1: value1, key2: " "value2,...'"
            )

        label_key, label_value = label_kv

        if label_key in labels.keys():
            raise ValueError("Duplicate label key {}".format(label_key))

        labels[label_key.strip()] = label_value.strip()

    return labels
