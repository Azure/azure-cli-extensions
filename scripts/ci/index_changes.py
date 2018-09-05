import sys
import json


_, index_file, public_index = sys.argv  # pylint: disable=unbalanced-tuple-unpacking


curr_index = json.loads(index_file).get("extensions")
public_index = json.loads(public_index)

for extension in curr_index:
    if curr_index[extension] != public_index[extension]:
        print(extension)
