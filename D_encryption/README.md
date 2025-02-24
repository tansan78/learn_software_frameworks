
## Encryption Introduction

Encryption is the process of transforming data into an unreadable format to protect it from unauthorized access. It ensures confidentiality, integrity, and authenticity in digital communications.

- **Symmetric Encryption**: Uses the same key for encryption and decryption (e.g., AES, DES). It is fast but requires secure key sharing.
- **Asymmetric Encryption**: Uses a key pair—public key for encryption and private key for decryption (e.g., RSA, ECC). It enables secure key exchange and digital signatures.
- **Hash Signatures**: Use cryptographic hash functions (e.g., SHA-256) to generate fixed-size representations of data. When combined with private key encryption (e.g., in digital signatures), they verify data integrity and authenticity without revealing the original message.


## Challenges
Before starting, please read the [How to Use](#how-to-use) section, and the [API section](#apis).

### Accounts and Authentication
Implement an account system, which can
1. register user with name and password (do not store original password for security reason)
2. authentication user using hashed password, then issue a session token with expiration, for subsequent easy authentication
3. verify the provided session token and verify that the session token is not expired

The code template is provided at [challenge_account_system.py](./challenge_account_system.py).

## How to use

In a terminal tab, start virtual environment and run the code
```
$ bash start_env.sh
$ python3 challenge_accounts.py
```

## APIs

We use [hashlib](https://docs.python.org/3/library/hashlib.html#examples) for password hashing and also for possible signature

We use [cryptography](https://cryptography.io/en/latest/fernet/) for encryption