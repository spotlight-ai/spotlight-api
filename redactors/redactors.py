import os
from loguru import logger
from redactors.base import FileRedactor
from core.constants import Masks
from core.util import one_way_hash_mask

from PyPDF2 import PdfFileReader, PdfFileWriter,PdfFileMerger
from redactors.pdf_parser import pdf_redactor

class TextFileRedactor(FileRedactor):
    def redact_file(self, file_name, permission_descriptions, markers, mask):
        file = open(file_name, "r+").read()

        total_diff: int = 0
        i: int = 0
        sorted_markers: list = sorted(
            markers, key=lambda k: (k.start_location, -k.end_location)
        )

        total_markers: int = len(sorted_markers)

        hash_pii_types: set = Masks.HASH_PII_TYPES

        redaction_text = (
            "<REDACTED>"  # The PII's will be replaced with this text if not masked.
        )
        marker_to_be_excluded = []
        
        """
        Below is the algorithm to modify the marker co-ordinates after replacing the PII values
        with the Redaction text or a randomly generated Hash value.
        """
        
        while i < len(sorted_markers):
            marker_start = sorted_markers[i].start_location
            marker_end = sorted_markers[i].end_location
            j = i
            last_end = i
            permit = True
            while (j < total_markers) and (
                sorted_markers[j].start_location < marker_end
            ):
                if not permit:
                    marker_to_be_excluded.append(j)
                elif permit and (
                    sorted_markers[j].pii_type not in permission_descriptions
                ):
                    permit = False
                    for k in range(i, j + 1):
                        marker_to_be_excluded.append(k)
                if sorted_markers[j].end_location > marker_end:
                    marker_end = sorted_markers[j].end_location
                    last_end = j
                j += 1
            if not permit:
                file_start, file_end = (
                    marker_start - total_diff,
                    marker_end - total_diff,
                )
                if (i == last_end) and mask:
                    if sorted_markers[i].pii_type in hash_pii_types:
                        masked_value = one_way_hash_mask(
                            file[file_start:file_end], sorted_markers[i].pii_type
                        )
                    else:
                        masked_value = redaction_text
                else:
                    masked_value = redaction_text
                marker_len = marker_end - marker_start
                file = (masked_value).join([file[:file_start], file[file_end:]])
                total_diff = total_diff + marker_len - len(masked_value)
            else:
                for k in range(i, j):
                    sorted_markers[k].start_location -= total_diff
                    sorted_markers[k].end_location -= total_diff
            i = j
        
        """ Return only the markers which are permitted """
       
        modified_markers = [
            marker
            for i, marker in enumerate(sorted_markers)
            if i not in marker_to_be_excluded
        ]

        open(file_name, "w").write(file)
        return modified_markers
        
class PdfFileRedactor(FileRedactor):
    def redact_file(self, file_name, permission_descriptions, markers, mask):
        pdf = PdfFileReader(file_name)
        for page in range(pdf.getNumPages()):
            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(pdf.getPage(page))
            output_filename = 'page_{}.pdf'.format(
                 page+1)
            with open(output_filename, 'wb') as out:
                pdf_writer.write(out)
            dem_name = f'page_{page+1}.pdf'
            with open(dem_name, 'r') as file:
                file_text,document,text_layer = self.parse_file_to_text(file)[0]
                
            current_page_pii = [self.format_marker(marker) for marker in markers if (marker.page_number == (page+1) and marker.pii_type not in permission_descriptions)]

            self.parse_text_to_pdf(document, text_layer, current_page_pii, page) 
                
        mergedObject = PdfFileMerger()
        for fileNumber in range(1, pdf.getNumPages()+1):
            mergedObject.append(PdfFileReader('pager_' + str(fileNumber)+ '.pdf', 'rb'))
        mergedObject.write(file_name)
        for fileNumber in range(1,pdf.getNumPages()+1):
            f1 = f'page_{fileNumber}.pdf'
            f2 = f'pager_{fileNumber}.pdf'
            os.system(f'rm {f1}')
            os.system(f'rm {f2}')
            
        return markers
    
    def format_marker(self, marker):
        return {"pii_type": marker.pii_type, "start_location": marker.start_location,
                "end_location": marker.end_location, "confidence": marker.confidence}
                
    def parse_text_to_pdf(self, document,text_layer,pii,page):
        text_layer = pdf_redactor.update_text_with_pii(*text_layer,pii)
        document = pdf_redactor.apply_updated_text(document,*text_layer)
        dem_name= f'pager_{page+1}.pdf'
        pdf_redactor.write_pdf(document,dem_name) 
        
    def parse_file_to_text(self,file_obj) -> str:
        options = pdf_redactor.RedactorOptions()
        options.xmp_filters = [lambda xml: None]
        options.content_filters = [
            (
               
                lambda m: "annotation?"
            )
        ]
        output,document,text_layer = pdf_redactor.redactor(options, file_obj.name)
        # logger.debug(f"Parsed text output : {output}")
        return output,document,text_layer

        

        
        
        
        
        
        
        
        
        
