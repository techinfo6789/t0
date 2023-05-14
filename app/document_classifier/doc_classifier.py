
import os
import re
import glob
import json
import pdfplumber
import PyPDF2
from typing import Dict
from config.table_headers import doc_type_header_dict

class DocumentClassifier:

    def __init__(self, doc_type_header_dict: Dict):
        self.doc_type_header_dict = doc_type_header_dict

    def is_text_extractable(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            return all([reader.getPage(i).extract_text() != '' for i in range(reader.numPages)])

    def find_headers(self, pdf_content):
        for doc_type, headers in self.doc_type_header_dict.items():
            for header in headers:
                if re.search(header, pdf_content, re.IGNORECASE):
                    return doc_type
        return None

    def get_pdf_content(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            pdf_content = ''.join([page.extract_text().lower() for page in pdf.pages])
        return pdf_content

    def classify_document_search(self, pdf_path):
        pdf_content = self.get_pdf_content(pdf_path)
        doc_type = self.find_headers(pdf_content)
        if doc_type is not None:
            return doc_type.upper()
        else:
            return "Header not Found"


def main():

    classifier = DocumentClassifier(doc_type_header_dict)
    out_dict = classifier.classify_documents('../data/test/1.pdf')
    print(out_dict)

if __name__ == '__main__':
    main()
