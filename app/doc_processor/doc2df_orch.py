import PyPDF2
from text2df import Pdftext2df
from textract import TextractProcessor


class DocOrchestrator:
    def __init__(self, aws_access_key_id, aws_secret_access_key, s3_bucket):
        self.Pdftext2df_processor = Pdftext2df()
        self.textract_processor = TextractProcessor(aws_access_key_id, aws_secret_access_key, s3_bucket)

    def is_text_extractable(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            return all([reader.getPage(i).extract_text() != '' for i in range(reader.numPages)])

    def process_pdf(self, pdf_file, pdf_filename):
        if self.is_text_extractable(pdf_file):
            # Process the PDF using PDFProcessor
            text_df = self.Pdftext2df_processor.pdf_to_df(pdf_file)
            # Use the PDFTableExtractor to process the text_df dictionary
            
            return text_df
        else:
            # Process the PDF using TextractProcessor
            return self.Pdftext2df_processor.text_to_dataframe(self.textract_processor.process_pdf(pdf_file, pdf_filename))
             
