#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time


def main():
    # Generate 100,000 log entries with "Peer down" at line 50,000
    for i in range(1, 100001):
        if i == 50000:
            print("Peer down")
        else:
            print(f"Log entry {i}")

    # Keep pod running
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
