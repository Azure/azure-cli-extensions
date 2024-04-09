import re
import os

# Open the file
with open("src/apic-extension/setup.py", "r") as f:
    content = f.read()

# Find the version string
version_match = re.search(r"VERSION = '(.*?)'", content)
if version_match is None:
    raise ValueError("Could not find version string in setup.py")

# Extract the original version
original_version = version_match.group(1)

# Get the commit hash
commit_hash = os.getenv("GITHUB_SHA", "daily")[:7]

# Create the new version string
new_version = original_version + "+" + commit_hash

# Replace the old version string with the new one
content_new = re.sub(r"VERSION = '(.*?)'", f"VERSION = '{new_version}'", content)

# Write the updated content back to the file
with open("src/apic-extension/setup.py", "w") as f:
    f.write(content_new)