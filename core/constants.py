class AuditConstants:
    DATASET_CREATED = "DATASET_CREATED"
    DATASET_VERIFIED = "DATASET_VERIFIED"
    DATASET_OWNERS_MODIFIED = "Dataset owners list modified"


class NotificationConstants:
    DATASET_SHARED_TITLE = "A dataset has been shared with you"
    DATASET_SHARED_DETAIL = "You have been granted access to Dataset(s):"


class UserConstants:
    PUBLIC_DOMAINS = ["gmail.com", "yahoo.com", "msn.com", "hotmail.com"]


class Masks:
    def __init__(self):
        self.hash_pii_types = ["ssn", "ein", "routing", "usa_phone"]
        self.masks = {
            "name": "NAME",
            "email": "user@domain",
            "usa_phone": "1111111111",
            "ssn": "000000000",
            "routing": "999999999",
            "cc_number": "0000123456789000",
            "city": "New Delhi",
            "country": "India",
            "state": "Texas",
            "currency": "$0000",
            "ein": "222222222",
            "ip_address": "000.000.0.0",
        }
