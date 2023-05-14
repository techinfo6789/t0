from flask import Flask, request, jsonify
from threading import Thread
from textract.aws_ocr import TextractProcessor
import io
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

# Get the AWS credentials and S3 bucket name from environment variables
aws_access_key = os.environ['AWS_ACCESS_KEY']
aws_secret_key = os.environ['AWS_SECRET_KEY']
s3_bucket_name = os.environ['S3_BUCKET_NAME']


processor = TextractProcessor(aws_access_key, aws_secret_key, s3_bucket_name)

app = Flask(__name__)

file_status = {}


@app.route('/process_pdf', methods=['POST'])
def process_pdf_endpoint():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    pdf_file = request.files['pdf_file']
    pdf_filename = pdf_file.filename
    pdf_content = pdf_file.read()
    pdf_buffer = io.BytesIO(pdf_content)

    file_id = str(uuid.uuid4())

    file_status[file_id] = {
        "status": "processing",
        "url": None
    }

    def process_pdf_thread():
        text_file_url = processor.process_pdf(pdf_buffer, pdf_filename)
        file_status[file_id]["status"] = "done"
        file_status[file_id]["url"] = text_file_url

    thread = Thread(target=process_pdf_thread)
    thread.start()

    return jsonify({"file_id": file_id})


@app.route('/status/<file_id>', methods=['GET'])
def check_status(file_id):
    if file_id not in file_status:
        return jsonify({"error": "File not found"}), 404

    status = file_status[file_id]["status"]
    if status == "done":
        return jsonify({"status": "done", "url": file_status[file_id]["url"]})
    else:
        return jsonify({"status": "processing"})


if __name__ == '__main__':
    app.run(debug=True, port = 5999)
