"""Stub ``requests.auth`` module."""


class HTTPBasicAuth:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
