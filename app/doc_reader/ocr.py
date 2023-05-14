import io
import boto3
import time
from app.doc_reader.doc_reader_config import ocr_output_folder_name
import uuid
import os
import json

class TextractProcessor:
    def __init__(self, aws_access_key_id, aws_secret_access_key, s3_bucket):
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.textract = boto3.client('textract', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
        self.s3_bucket = s3_bucket

    def upload_file_to_s3(self, file_obj, s3_object_key, metadata=None):
        # Upload the file to S3 in the specified object key, with metadata if provided
        extra_args = {'Metadata': metadata} if metadata else {}
        self.s3.upload_fileobj(file_obj, self.s3_bucket, s3_object_key, ExtraArgs=extra_args)

    def extract_text_from_pdf(self, s3_object_key):
        # Call the Textract API to extract text from the PDF file
        job_id = self.textract.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.s3_bucket,
                    'Name': s3_object_key
                }
            })["JobId"]

        print(f"Started job with ID: {job_id}")
        job_status = self.textract.get_document_text_detection(JobId=job_id)["JobStatus"]
        print("Job status: {}".format(job_status))

        while job_status == "IN_PROGRESS":
            time.sleep(5)
            job_status = self.textract.get_document_text_detection(JobId=job_id)["JobStatus"]
            print("Job status: {}".format(job_status))

        if job_status == "SUCCEEDED":
            response = self.textract.get_document_text_detection(JobId=job_id)

            # Extract the text from the response
            text = ''
            while True:
                for item in response['Blocks']:
                    if item['BlockType'] == 'LINE':
                        text += f" {item['Text']}"

                next_token = response.get('NextToken', None)

                if next_token is None:
                    break

                response = self.textract.get_document_text_detection(JobId=job_id, NextToken=next_token)

            return text
        else:
            raise Exception(f"Text extraction job failed with status {job_status}")

    def process_pdf(self, pdf_file, pdf_filename):
        # Open the file in binary mode
        with open(pdf_file, "rb") as file_obj:
            self.upload_file_to_s3(file_obj, pdf_filename, {'original_filename': pdf_filename})
        text = self.extract_text_from_pdf(pdf_filename)
        return text
