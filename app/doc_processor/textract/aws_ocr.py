import boto3
import os
import tempfile
import uuid
import time
from textract.textract_config import ocr_output_folder_name
class TextractProcessor:
    def __init__(self, aws_access_key_id, aws_secret_access_key, s3_bucket):
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.textract = boto3.client('textract', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.s3_bucket = s3_bucket

    def startJob(self, s3BucketName, objectName):
        response = None
        response = self.textract.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': objectName
            }
        })
        return response["JobId"]

    def isJobComplete(self, jobId):
        time.sleep(5)
        response = self.textract.get_document_text_detection(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))
        while(status == "IN_PROGRESS"):
            time.sleep(5)
            response = self.textract.get_document_text_detection(JobId=jobId)
            status = response["JobStatus"]
            print("Job status: {}".format(status))
        return status

    def process_pdf(self, pdf_file, pdf_filename):
        # Generate a unique document ID for the PDF
        doc_id = str(uuid.uuid4())

        pdf_base_name = os.path.splitext(pdf_filename)[0]
        # Upload the PDF file to S3 in a folder with the document ID, with original file name as metadata
        s3_pdf_key = f"{ocr_output_folder_name}/{doc_id}/{pdf_base_name}.pdf"
        self.upload_file_to_s3(pdf_file, s3_pdf_key, {'original_filename': pdf_filename})
        
        # Extract text from the PDF file using Textract
        text = self.extract_text_from_pdf(s3_pdf_key)
        
        # Save the extracted text to S3 in the same folder as the PDF file
        s3_text_key = f"{ocr_output_folder_name}/{doc_id}/{pdf_base_name}_ocr.txt"
        self.save_text_to_s3(text, s3_text_key)
        
        # Return the URL of the saved text file
        return f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_text_key}"

    def upload_file_to_s3(self, file_obj, s3_object_key, metadata=None):
        # Upload the file to S3 in the specified object key, with metadata if provided
        extra_args = {'Metadata': metadata} if metadata else {}
        self.s3.upload_fileobj(file_obj, self.s3_bucket, s3_object_key, ExtraArgs=extra_args)

    def extract_text_from_pdf(self, s3_object_key):
        # Call the Textract API to extract text from the PDF file
        job_id = self.startJob(self.s3_bucket, s3_object_key)
        job_status = self.isJobComplete(job_id)

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

    def save_text_to_s3(self, text, s3_object_key):
        # Save the text to S3 in the specified object key
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(text.encode('utf-8'))
            temp_file.flush()
            temp_file.seek(0)
            self.s3.upload_fileobj(temp_file, self.s3_bucket, s3_object_key)