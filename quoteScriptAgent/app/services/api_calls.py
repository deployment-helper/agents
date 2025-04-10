class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint):
        # Simulate a GET request
        return f"GET request to {self.base_url}/{endpoint}"

    
    def post(self, endpoint, data):
        # Simulate a POST request
        return f"POST request to {self.base_url}/{endpoint} with data {data}"
    
    def put(self, endpoint, data):
        # Simulate a PUT request
        return f"PUT request to {self.base_url}/{endpoint} with data {data}"
    
    def delete(self, endpoint):
        # Simulate a DELETE request
        return f"DELETE request to {self.base_url}/{endpoint}"