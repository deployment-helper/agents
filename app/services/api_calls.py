import requests


class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint):
        response = requests.get(f"{self.base_url}/{endpoint}")
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data):
        response = requests.post(f"{self.base_url}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint, data):
        response = requests.put(f"{self.base_url}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint):
        response = requests.delete(f"{self.base_url}/{endpoint}")
        response.raise_for_status()
        return response.json()
