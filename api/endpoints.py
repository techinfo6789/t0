import sys
sys.path.append('../')

from flask import Blueprint, request, jsonify
import os
import tempfile
from app.pdf_processing.table_extraction import PDFTableExtractor
from config.table_headers import coa_table_header_list as header_list
from config.table_headers import doc_type_header_dict, table_header_list
from app.utils.aws_utils import download_pdf
from app.document_classification.doc_classifier import DocumentClassifier

extract = Blueprint('extract', __name__)

# Instantiate the PDFTableExtractor class with the header list



@extract.route('/v1/get_pdf', methods=['POST'])
def get_pdf():
    # Get the URL of the PDF file from the request data
    pdf_url = request.json['pdf_url']

    # Download the PDF file to the server
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, 'temp.pdf')
    download_pdf(pdf_url, file_path)

    # Return the saved file path in JSON format
    result = {'file_path': file_path}

    return jsonify(result)

@extract.route('/v1/classify', methods=['POST'])
def classify_document():
    pdf_file = request.files.get('pdf_file')

    if not pdf_file:
        return jsonify({'error': 'No PDF file provided'}), 400

    # Save the file to a temporary directory
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, pdf_file.filename)
    pdf_file.save(file_path)

    # Classify document using DocumentClassifier
    classifier = DocumentClassifier(doc_type_header_dict)
    if classifier.is_text_extractable(file_path):
        doc_type = classifier.classify_document_search(file_path)
        result = {'document_type': doc_type}
    else:
        result = {'error': 'Text is not extractable from the provided PDF'}

    # Remove the temporary directory and file
    os.remove(file_path)
    os.rmdir(temp_dir)

    return jsonify(result)


@extract.route('/v1/extract', methods=['POST'])
def extract_tables():
    pdf_url = False  # request.form.get('pdf_url')
    pdf_file = request.files.get('pdf_file')
    doc_type = request.form.get('doc_type', None)

    if not pdf_url and not pdf_file:
        return jsonify({'error': 'No PDF file provided'}), 400

    if pdf_url and pdf_file:
        return jsonify({'error': 'Both PDF URL and file provided. Please provide only one.'}), 400

    if pdf_url:
        # Download the PDF file to a temporary directory
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, 'temp.pdf')
        download_pdf(pdf_url, file_path)

    elif pdf_file:
        if pdf_file.filename == '':
            return jsonify({'error': 'No file provided'}), 400

        # Save the file to a temporary directory
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, pdf_file.filename)
        pdf_file.save(file_path)

    if not doc_type:
        classifier = DocumentClassifier(doc_type_header_dict)
        doc_type = classifier.classify_document_search(file_path)

    headers = table_header_list[doc_type.lower()]
    extractor = PDFTableExtractor(headers)    
    # Extract tables from the PDF file
    if os.path.exists(file_path):
        print(f"*#&#*#*#*#*#*#*#**#*#*File exists{file_path}")
    tables, headers = extractor.process_pdf(file_path)
    print(f"************{tables}************")
    # Serialize the extracted tables and headers to JSON format
    result = {
        'tables': {str(page): table.to_dict(orient='list') for page, table in tables.items()},
    }

    return jsonify(result)

