# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import requests


def do_request(
    method: str,
    url: str,
    token: str,
    json: dict | None = None,
    return_bytes: bool = False,
) -> dict | list | str | bytes:
    """Send an authorized HTTP request and return the response body."""
    
    headers = {"Authorization": f"Bearer {token}"}
    request = requests.Request(method=method, url=url, headers=headers, json=json)

    try:
        with requests.Session() as session:
            response = session.send(
                session.prepare_request(request),
                timeout=120,
                # add ignore SSL verification if needed
                verify=False
            )
            response.raise_for_status()

            if return_bytes:
                return response.content

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            
            return response.text

    except requests.RequestException:
        raise

