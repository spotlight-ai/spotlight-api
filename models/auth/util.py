import hashlib


def hash_token(token):
    return hashlib.sha512(token.encode()).hexdigest()
