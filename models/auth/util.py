import hashlib
import datetime

invalid_tokens = []

def delete_expired_tokens():
    curr_time = datetime.datetime.utcnow()
    for token in invalid_tokens:
        if token["expiry"] < curr_time :
            invalid_tokens.remove(token)
    return
        
def add_invalid_token(token, expiry):
    invalid_tokens.append({"token": hash_token(token), "expiry": expiry})
    delete_expired_tokens()
    return "Token invalidated successfully"

def check_validity(token):
    token_hash = hash_token(token)
    is_valid = True
    for token in invalid_tokens:
        if (token["token"] == token_hash):
            is_valid = False
    return is_valid

def hash_token(token):
    return hashlib.sha512(token.encode()).hexdigest()
