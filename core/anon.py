import os
import img2pdf

from core.constants import AnonymizationType, SupportedFiles
from loguru import logger
from pdf2image import convert_from_path
from PIL import Image


REDACTION_CHAR_STR: str = "<REDACTED>"

class ImageRedactor:
    def __init__(self, filepath):
        self.filepath = filepath
        _, ext = os.path.splitext(filepath)
        self.is_pdf = False
        if ext == ".pdf":
            self.imgs = self.convert_pdf_to_images(filepath)
            self.is_pdf = True
        elif ext in SupportedFiles.IMAGE_BASED:
            self.imgs = [Image.open(filepath)]

    @staticmethod
    def convert_pdf_to_images(pdf_path: str) -> list:
        """ 
        converts each page of the pdf into an image

        returns a list of Images
        """
        pages = convert_from_path(pdf_path, dpi=600)
        img_name, _ = os.path.splitext(os.path.basename(pdf_path))
        for i, page in enumerate(pages):
            page.filename = f"{img_name}_{i}.png"
        return pages

    def _redact_images(self, markers: list):
        masked_imgs = []
        for img in self.imgs:
            if type(img) == str:
                img = Image.open(img)
            masked_imgs.append(img)
        for marker in markers:
            pg_num = 0 # TODO: ADD SUPPORT FOR MULTI-PAGE PDF
            width, height = masked_imgs[pg_num].size
            coord_tuple = self._convert_coordinates(marker, height)
            masked_imgs[pg_num].paste(0, coord_tuple[:4]) # draws the bbox on the page
        return masked_imgs

    def redact(self, output_location: str, markers: list):
        masked_imgs = self._redact_images(markers)
        if self.is_pdf:
            self.convert_masked_to_pdf(output_location, masked_imgs)
        else:
            assert len(masked_imgs) == 1
            img = masked_imgs[0]
            img.save(output_location)

        logger.debug(f"Successfully redacted file {output_location}")

    @staticmethod
    def convert_masked_to_pdf(output_location: str, masked_imgs: list):
        """ Converts the list of masked images into a pdf.  Intermediary step of saving
            the masked images first, then giving the filepath to img2pdf.convert()
            The PDF and masked images are saved into the directory either 
            (1) specified in convert_pdf_to_images(), or
            (2) the directory the non-masked image was uploaded from.
            
            Then deleting the intermediary masked image files
            
        """
        for i, img in enumerate(masked_imgs):
            img.save(img.filename)
        with open(output_location,"wb") as f:
            f.write(img2pdf.convert([img.filename for img in masked_imgs]))
        # removes the masked image
        for img in masked_imgs:
            os.remove(img.filename)

        return output_location

    @staticmethod
    def _convert_coordinates(marker, height):
        left, bottom, right, top = marker.x1, marker.y1, marker.x2, marker.y2

        return (left, height - top, right, height - bottom) 



def anonymize_file(filepath: str, markers: list, perms: list,
                   anon_method: AnonymizationType = AnonymizationType.REDACT) -> list:
    _, ext = os.path.splitext(filepath)
    if ext in SupportedFiles.CHARACTER_BASED:
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
        
        open(filepath, "w").write(file)
    elif ext in SupportedFiles.IMAGE_BASED:
        new_markers = []
        redacted_markers = []
        for marker in markers:
            if marker.pii_type in perms:
                new_markers.append(markers)
            else:
                redacted_markers.append(marker)
        img_redactor = ImageRedactor(filepath)

        img_redactor.redact(filepath, redacted_markers)
    
    return new_markers
