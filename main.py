from  app.document_classifier.doc_classifier import DocumentClassifier
from config.table_headers import doc_type_header_dict, table_header_list
from app.doc_extractor import PDFTableExtractor

def main():
    pdf_path = './data/pdfs/1.pdf'
    classifier = DocumentClassifier(doc_type_header_dict)
    doc_type = classifier.classify_document_search('./data/pdfs/1.pdf').lower()
    
    headers = table_header_list[doc_type]
    
    extractor = PDFTableExtractor(headers)
    extracted_tables, header_df = extractor.process_pdf(pdf_path)
    print(extracted_tables)

if __name__ == '__main__':
    main()