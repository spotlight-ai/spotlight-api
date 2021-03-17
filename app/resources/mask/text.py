import os

import requests
from flask import request
from flask_restful import Resource

from core.constants import Masks
from core.util import one_way_hash_mask

class MaskText(Resource):
    def post(self):
        body = request.get_json(force=True)
        url = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/text'
        raw_text = body.get("text")
        data = {"text": raw_text}

        r = requests.post(url=url, json=data)
        
        markers = r.json()["markers"]
        masked_text: str = raw_text
        
        total_diff: int = 0
        i: int = 0
        
        sorted_markers: list = sorted(
            markers, key=lambda k: (k["start_location"], -k["end_location"])
        )

        total_markers: int = len(sorted_markers)

        hash_pii_types: set = Masks.HASH_PII_TYPES

        redaction_text = (
            "<REDACTED>"  # The PII's will be replaced with this text if not masked.
        )
        
        """
        Below is the algorithm to modify the marker co-ordinates after replacing the PII values
        with the Redaction text or a randomly generated Hash value.
        """
        
        while i < len(sorted_markers):
            marker_start = sorted_markers[i]["start_location"]
            marker_end = sorted_markers[i]["end_location"]
            j = i
            pii_type = sorted_markers[i]["pii_type"]
            while (j < total_markers) and (
                sorted_markers[j]["start_location"] < marker_end
            ):
                if sorted_markers[j]["end_location"] > marker_end:
                    marker_end = sorted_markers[j]["end_location"]
                    pii_type = sorted_markers[j]["pii_type"]
                j += 1
            file_start, file_end = (
                marker_start - total_diff,
                marker_end - total_diff,
            )
            if pii_type in hash_pii_types:
                masked_value = one_way_hash_mask(
                    masked_text[file_start:file_end], pii_type
                )
            else:
                masked_value = redaction_text
                
            marker_len = marker_end - marker_start
            masked_text = (masked_value).join([masked_text[:file_start], masked_text[file_end:]])
            
            for k in range(i, j):
                sorted_markers[k]["start_location"] -= total_diff
                
            total_diff = total_diff + marker_len - len(masked_value)
            
            for k in range(i, j):            
                sorted_markers[k]["end_location"] -= total_diff
                
            i = j

        return {"redacted": masked_text, "markers": sorted_markers}
