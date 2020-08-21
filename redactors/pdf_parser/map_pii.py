from loguru import logger

def mapper(text_content,text_tok,pii):

    for item in pii :
        dem_text = text_content[item.get('start_location'):item.get('end_location')]
        if text_tok.find(dem_text) != -1 :
            item['start_location'] = text_tok.find(dem_text)
            item['end_location'] = text_tok.find(dem_text) + len(dem_text)
    return pii
