# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import urllib.parse

from locust import HttpUser, constant_throughput, task

base_url = "https://app-petclinic-yalrccgejv64o.azurewebsites.net/"


class WebsiteUser(HttpUser):
    
    host = urllib.parse.quote(base_url, safe=':/')
    wait_time = constant_throughput(1)

    @task
    def mainPage(self):
        self.client.get("/", name="Homepage")