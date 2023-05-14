import PyPDF2
import os
from app.doc_reader.ocr import TextractProcessor



class DocReader:
    def __init__(self, aws_access_key_id, aws_secret_access_key, s3_bucket):
            self.aws_access_key_id = aws_access_key_id
            self.aws_secret_access_key = aws_secret_access_key
            self.s3_bucket = s3_bucket

    def is_text_extractable(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            return all([reader.getPage(i).extract_text() != '' for i in range(reader.numPages)])
        

    def read_text_noocr(self, pdf_path):
        if self.is_text_extractable(pdf_path):
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfFileReader(file)
                return ''.join([reader.getPage(i).extract_text() for i in range(reader.numPages)])
        else:
            return None
        
    def read_text_ocr(self, pdf_path):
       ocr_processor = TextractProcessor(self.aws_access_key_id, self.aws_secret_access_key, self.s3_bucket)
       
       return ocr_processor.process_pdf(pdf_path, os.path.basename(pdf_path))
    
    def read_text(self, pdf_path):
        if self.is_text_extractable(pdf_path):
            return self.read_text_noocr(pdf_path)
        else:
            return self.read_text_ocr(pdf_path)
        