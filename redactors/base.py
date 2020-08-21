from abc import ABC, abstractmethod

import redactors

class FileRedactor(ABC):
    
    @abstractmethod
    def redact_file(self, file_obj) -> str:
        raise NotImplementedError
 

class FileRedactorCreator(ABC):
    # Store redactor objects in memory
    _redactors: dict = dict()
    
    # Redactor keys
    TEXT_FILE_REDACTOR = 'text_file_redactor'
    PDF_FILE_REDACTOR = 'pdf_file_redactor'
    # Accepted file extensions
    TEXT_FILE_TYPES: set = {'.txt', '.md', '.csv', '.tsv'}
    PDF_FILE_TYPES: set = {'.pdf'}
    
    def get_redactor(self, extension: str) -> FileRedactor:
        
        if extension in self.TEXT_FILE_TYPES:
            if self.TEXT_FILE_REDACTOR not in self._redactors:
                self._redactors[self.TEXT_FILE_REDACTOR] = redactors.TextFileRedactor()
            return self._redactors.get(self.TEXT_FILE_REDACTOR)
        elif extension in self.PDF_FILE_TYPES:
            if self.PDF_FILE_REDACTOR not in self._redactors:
                self._redactors[self.PDF_FILE_REDACTOR] = redactors.PdfFileRedactor()
            return self._redactors.get(self.PDF_FILE_REDACTOR)      
        else:
            raise KeyError(f"Extension {extension} not supported.")
    
