import sys
import json


_, index_file, public_index = sys.argv


curr_index = json.loads(index_file).get("extensions")
public_index = json.loads(public_index)

print(curr_index, public_index)