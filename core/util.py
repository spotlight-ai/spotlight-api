import hashlib

from core.errors import MaskingErrors


def one_way_hash_mask(text: str, pii_type: str) -> str:
    """
    Masks PII in a one-way process so that the same value is generated for any input.
    :param text: Input PII text to mask
    :param pii_type: Type of PII (needed for determining masking function)
    :return: Masked string of PII
    """
    numeric_types: set = {"ssn", "ein", "routing", "usa_phone"}

    if pii_type in numeric_types:
        hash_val = str(
            int(hashlib.blake2b(text.encode("utf-8")).hexdigest(), 16) % 10 ** len(text)
        )

        hash_val.ljust(len(text), "0")

        return format_numeric_mask(hash_val, pii_type)
    else:
        raise AttributeError(MaskingErrors.PII_TYPE_NOT_SUPPORTED)


def format_numeric_mask(masked_text: str, masked_pii_type: str) -> str:
    """
    Formats a numeric PII token into the correct format.
    :param masked_text: Masked PII token
    :param masked_pii_type: PII type
    :return: Formatted String object
    """
    # Dictionary of formatting functions for each type of PII
    format_funcs = {
        "usa_phone": lambda x: f"+1 {x[:3]}-{x[3:6]}-{x[6:10]}",
        "ssn": lambda x: f"{x[:3]}-{x[3:5]}-{x[5:9]}",
        "ein": lambda x: f"{x[:2]}-{x[2:9]}",
    }

    # Call the function from the dictionary with the masked token, pass-through if no special format required
    return format_funcs.get(masked_pii_type, lambda x: x)(masked_text)
