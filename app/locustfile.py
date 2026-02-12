import random
from locust import HttpUser, task, between

class CacheTestUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.item_ids = [str(i) for i in range(1, 30)]

    @task(1)
    def write_item(self):
        item_id = random.choice(self.item_ids)
        self.client.post("/items/", json={"name": f"Item {item_id}", "description": f"Description for item {item_id}"}) 

    @task(10)
    def read_item(self):
        item_id = random.choice(self.item_ids)
        self.client.get(f"/items/{item_id}")

# locust -f locustfile.py --host http://localhost:8000
