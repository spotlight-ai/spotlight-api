from core.constants import AnonymizationType

CHARACTER_FORMATS: set = {".txt"}
REDACTION_CHAR_STR: str = "<REDACTED>"


def anonymize_file(filepath: str, markers: list, perms: list,
                   anon_method: AnonymizationType = AnonymizationType.REDACT) -> list:
    file = open(filepath, mode="r+").read()
    
    # Sort marker list by start location
    sorted_markers: list = sorted(markers, key=lambda x: (x.start_location, -x.end_location))
    
    current_file_pos: int = 0
    current_offset: int = 0
    
    new_markers: list = []
    
    for marker in sorted_markers:
        start: int = marker.start_location
        
        if start < current_file_pos:
            continue
        
        start += current_offset
        end: int = marker.end_location + current_offset
        type: str = marker.pii_type
        length: int = end - start
        
        if type not in perms:
            previous_text = file[:start]
            next_text = file[end:]
            file = REDACTION_CHAR_STR.join([previous_text, next_text])
            current_offset += len(REDACTION_CHAR_STR) - length
            current_file_pos = end
        else:
            marker.start = start
            marker.end = end
            new_markers.append(marker)
    
    print(file, flush=True)
    
    open(filepath, "w").write(file)
    
    return new_markers
