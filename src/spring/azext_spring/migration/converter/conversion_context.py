# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os

from knack.log import get_logger

logger = get_logger(__name__)


# Context Class
class ConversionContext:
    def __init__(self, source):
        self.source = source
        self.converters = []

    def register_converter(self, converter_class):
        self.converters.append(converter_class)

    def run_converters(self):
        converted_contents = {}
        for converter_class in self.converters:
            converter = converter_class(self.source)
            items = converter.convert()
            converted_contents.update(items)
        return converted_contents

    def save_to_files(self, converted_contents, output_path):
        logger.debug(f"Start to save the converted content to files in folder {os.path.abspath(output_path)}...")
        os.makedirs(os.path.abspath(output_path), exist_ok=True)

        for filename, content in converted_contents.items():
            output_filename = os.path.join(output_path, filename)
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                logger.info(f"Generating the file {output_filename}...")
                output_file.write(content)
