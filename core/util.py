import hashlib

# ssn, routing are 9-digit number
def one_way_hash_mask(text, pii_type):
    if pii_type == "ssn":
        hash_value = str(
            int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (10 ** 9)
        )
        if len(hash_value) < 9:
            hash_value += "0" * (9 - len(hash_value))

        if "-" in text:
            return hash_value[:3] + "-" + hash_value[3:5] + "-" + hash_value[5:]
        else:
            return hash_value

    if pii_type == "ein":
        hash_value = str(
            int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (10 ** 9)
        )

        if len(hash_value) < 9:
            hash_value += "0" * (9 - len(hash_value))

        if "-" in text:
            return hash_value[:2] + "-" + hash_value[2:]
        else:
            return hash_value

    if pii_type == "routing":
        hash_value = str(
            int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (10 ** 9)
        )

        if len(hash_value) < 9:
            hash_value = ("0" * (9 - len(hash_value))) + hash_value

        return hash_value

    if pii_type == "usa_phone":
        hash_value = str(
            int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (10 ** 10)
        )

        if len(hash_value) < 10:
            hash_value += "0" * (10 - len(hash_value))

        if "+1" in text:
            return "+1-" + hash_value[:3] + "-" + hash_value[3:6] + "-" + hash_value[6:]
        elif "(" in text:
            return "(" + hash_value[:3] + ") " + hash_value[3:6] + "-" + hash_value[6:]
        elif "-" in text:
            return hash_value[:3] + "-" + hash_value[3:6] + "-" + hash_value[6:]
        elif " " in text:
            return hash_value[:3] + " " + hash_value[3:6] + " " + hash_value[6:]
        else:
            return hash_value

    return None
