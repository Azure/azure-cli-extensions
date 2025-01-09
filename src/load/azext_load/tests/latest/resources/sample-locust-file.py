# END
from locust import HttpUser, constant_throughput, task

base_url = "https://app-petclinic-yalrccgejv64o.azurewebsites.net/"


class WebsiteUser(HttpUser):
    host = base_url
    wait_time = constant_throughput(1)

    @task
    def mainPage(self):
        self.client.get("/", name="Homepage")