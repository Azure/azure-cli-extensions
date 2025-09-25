# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
from ._validators import validate_data_product_name, validate_source_path, validate_destination_path


def load_arguments(self, _):
    with self.argument_context('network-analytics data-product ingest') as c:
        c.argument("data_product_name", options_list=["--data-product-name"], help="The data product resource name.", id_part="name", validator=validate_data_product_name)
        c.argument('data_type', options_list=["--data-type"], help="The name of the data type into which you wish to ingest the specified file(s).")
        c.argument("source", options_list=["--source"], help="Source relative or absolute file path.", validator=validate_source_path)
        c.argument("destination", options_list=["--destination"], help="Destination file path which should be at least two directories deep.", validator=validate_destination_path)
