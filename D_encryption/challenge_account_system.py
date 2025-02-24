import datetime
import dateutil
import logging

from hashlib import blake2b
from hmac import compare_digest
from cryptography.fernet import Fernet
import dateutil.parser

logging.basicConfig(level=logging.INFO)

HASH_SECRET_KEY = b'hashing secret key'
HASH_AUTH_SIZE = 16


def hash_passwd(passwd: str):
    h = blake2b()
    h.update(passwd.encode())
    return h.hexdigest()


class Accounts():
    def __init__(self):
        self.user_to_passwd = {}
        key = Fernet.generate_key()
        self.fermet = Fernet(key)

    def register(self, username: str, passwd: str):
        # ***** WRITE YOUR CODE HERE  *****
        pass
    
    def authenticate_user(self, username: str, hash_passwd:str, valid_hours: int =1) -> str:
        """
        ***** WRITE YOUR CODE HERE  *****

        Verify the user's name and hashed password, then issue a session token
        """
        pass

    def authenticate_token(self, session_token: str):
        #  ***** WRITE YOUR CODE HERE  *****
        pass


def main():
    accounts = Accounts()

    accounts.register('thomas', '123456')

    hashed_passwd = hash_passwd('123456')
    session_token = accounts.authenticate_user('thomas', hashed_passwd)

    accounts.authenticate_token(session_token)


if __name__ == "__main__":
    main()