#!/bin/bash

mkdir -p ./api
mkdir -p ./utils
mkdir -p ./pdf_processing
mkdir -p ./document_classification/models
mkdir -p ./templates
mkdir -p ./tests
mkdir -p ./config

touch ./__init__.py
touch ./main.py
touch ./api/__init__.py
touch ./api/endpoints.py
touch ./api/views.py
touch ./utils/__init__.py
touch ./utils/helper_functions.py
touch ./pdf_processing/__init__.py
touch ./pdf_processing/direct_text_extraction.py
touch ./pdf_processing/aws_ocr.py
touch ./pdf_processing/table_extraction.py
touch ./document_classification/__init__.py
touch ./document_classification/doc_classifier.py
touch ./document_classification/models/trained_model.pkl
touch ./templates/index.html

touch ./tests/__init__.py
touch ./tests/test_pdf_processing.py
touch ./tests/test_document_classification.py
touch ./tests/test_endpoints.py

touch ./config/__init__.py
touch ./config/settings.py
touch ./config/aws_credentials.json

touch ./setup.py


