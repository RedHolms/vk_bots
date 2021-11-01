class ApiError(Exception): pass

class ApiResponseError(ApiError):
    def __init__(self, response, string: str = "Server response is invalid or contains an error. Response: {response}"):
        self.response = response
        self.string = str(string)
    def __str__(self):
        return self.string.format(response=str(self.response))