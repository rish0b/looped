from abc import ABC, abstractmethod
import time


class AuthManager(ABC):
    """A base class for handling token management."""
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.token_expiry = None

    def is_token_valid(self):
        """Check if the current token is still valid. If token_expiry is none, then it was user provided"""
        return self.access_token and (self.token_expiry is None or time.time() < self.token_expiry)

    def store_token(self, access_token, expires_in):
        """Store the access token and its expiry time."""
        self.access_token = access_token
        self.token_expiry = time.time() + expires_in

    def get_access_token(self):
        """Get the current access token or trigger authentication if needed."""
        if not self.is_token_valid():
            self.authenticate()
        return self.access_token

    @abstractmethod
    def authenticate(self):
        """Abstract method to be implemented by handlers."""
        pass