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
        self.user_to_passwd[username] = hash_passwd(passwd)
    
    def authenticate_user(self, username: str, hash_passwd:str, valid_hours: int =1) -> str:
        """
        Verify the user's name and hashed password, then issue a session token
        """
        # verify hash password
        if not compare_digest(hash_passwd, self.user_to_passwd.get(username, "")):
            raise ValueError("Invalid password")
        
        # create token content, including name and token expiration timestamp
        now_ds = datetime.datetime.now()
        expiration_ds = now_ds + datetime.timedelta(hours=valid_hours)
        session_token_str = self.__class__.encode_cookie(username, now_ds, expiration_ds)

        # sign the token content, to prevent forfeit. It is not stricly required because of encryption,
        # but it adds extra security (for example, you can give the AES key to other product teams, but save
        # the hash secret key to yourself
        h = blake2b(digest_size=HASH_AUTH_SIZE, key=HASH_SECRET_KEY)
        h.update(session_token_str.encode())
        session_token_sig = h.hexdigest()

        # encrypt the session token
        session_token_full = f'{session_token_str};{session_token_sig}'
        enc_session_token = self.fermet.encrypt(session_token_full.encode())

        return enc_session_token.decode()

    def authenticate_token(self, session_token: str):
        # decrypt the session token
        session_token_full = self.fermet.decrypt(session_token.encode()).decode()
        session_token_str, session_token_sig = session_token_full.split(';')
        
        # verify the session token using hash
        h = blake2b(digest_size=HASH_AUTH_SIZE, key=HASH_SECRET_KEY)
        h.update(session_token_str.encode())
        good_sig = h.hexdigest()
        if not compare_digest(good_sig, session_token_sig):
            raise ValueError('Mismatched signature in session token')
        
        # Parse the session token and verify expiration timestamp
        name, auth_time, expiration_ts = session_token_str.split(',')
        if dateutil.parser.parse(expiration_ts) < datetime.datetime.now():
            raise ValueError('Expired session token')
        logging.info(("Verified {name} is verified; authentication timestamp: {auth_ts}, " +
                     "and token expiration timestamp: {expiration_ts}").format(
                        name=name, auth_ts=auth_time, expiration_ts=expiration_ts
                    ))
        
        return name

    @staticmethod
    def encode_cookie(name: str, auth_timestamp: datetime.datetime, expiration_ts: datetime.datetime):
        return  '{name},{auth_time},{expire_time}'.format(
            name=name, 
            auth_time=auth_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            expire_time=expiration_ts.strftime('%Y-%m-%d %H:%M:%S')
        )


def main():
    accounts = Accounts()

    accounts.register('thomas', '123456')

    hashed_passwd = hash_passwd('123456')
    session_token = accounts.authenticate_user('thomas', hashed_passwd)

    accounts.authenticate_token(session_token)


if __name__ == "__main__":
    main()