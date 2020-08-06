import hashlib

active_tokens = {}

def add_valid_token(user_id, token):
    active_tokens[user_id] = {"token": hash_token(token), "valid": True}
    return     

def invalidate_token(user_id, token):
    token_hash = hash_token(token)
    if check_validity(user_id, token_hash):
        return "Invalid token received"
    else:
        active_tokens[user_id]["valid"] = False
        return "Token invalidated successfully"    
        
def check_validity(user_id, token):
    token_hash = hash_token(token)
    if user_id in active_tokens and active_tokens[user_id]["token"] == token_hash and active_tokens[user_id]["valid"]:
        return True
    else:
        return False

def hash_token(token):
    return hashlib.sha512(token.encode()).hexdigest()
