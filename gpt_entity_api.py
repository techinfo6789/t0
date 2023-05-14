import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.doc_reader.doc2text import DocReader
from app.gpt_extractor.run_gpt import GPTExtractor
import boto3
import threading
from dotenv import load_dotenv
from app.gpt_extractor.fields_finder import create_fields_prompt
from app.gpt_extractor.prompts import entity_extraction_prompt, entity_extraction_prompt2
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EntityExtractionInput(BaseModel):
    prompt_template: str = entity_extraction_prompt2
    s3_url: str = ''

class EntityExtractionOutput(BaseModel):
    entities: Dict[str, Any]

class TaskStatusOutput(BaseModel):
    status: str
    result_url: str = None


# Set up your AWS and OpenAI credentials
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
s3_bucket = os.environ['S3_BUCKET']
openai_api_key = os.environ['OPENAI_API_KEY']
model_name = 'gpt-3.5-turbo'

# Create instances of DocReader and GPTExtractor
doc_reader = DocReader(aws_access_key_id, aws_secret_access_key, s3_bucket)
gpt_extractor = GPTExtractor(openai_api_key, model_name)

# Set up S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

tasks = {}

results_folder = "results"

if not os.path.exists(results_folder):
    os.makedirs(results_folder)

def process_pdf_task(key, pdf_file_path, prompt_template):
    pdf_text = doc_reader.read_text(pdf_file_path)
    os.remove(pdf_file_path)

    if pdf_text:
        prompt_template = entity_extraction_prompt2
        try:
            extracted_entities = gpt_extractor.entity_extractor(pdf_text, prompt_template)
            result_filename = f"{key}.json"
            local_result_filepath = os.path.join(results_folder, result_filename)

            with open(local_result_filepath, 'w') as result_file:
                extracted_entities = json.loads(extracted_entities)
                json.dump(extracted_entities, result_file, indent=4)

            s3.upload_file(local_result_filepath, s3_bucket, result_filename)

            tasks[key]['status'] = 'completed'
        except Exception as e:
            tasks[key]['status'] = 'failed'
            raise HTTPException(status_code=500, detail=f"Failed to extract entities: {str(e)}")
    else:
        tasks[key]['status'] = 'failed'
        raise HTTPException(status_code=400, detail="PDF file could not be read")



@app.post('/extract_entities')
async def extract_entities(prompt_template: str = '', pdf: UploadFile = File(...)):

    key = str(uuid.uuid4())
    tasks[key] = {'status': 'processing'}

    with open(key, 'wb') as f:
        f.write(pdf.file.read())

    thread = threading.Thread(target=process_pdf_task, args=(key, key, prompt_template))
    thread.start()

    return {'key': key}

@app.get('/check_status/{key}', response_model=TaskStatusOutput)
async def check_status(key: str) -> TaskStatusOutput:
    if key not in tasks:
        raise HTTPException(status_code=400, detail="Invalid key")

    task_status = tasks[key]['status']

    if task_status == 'completed':
        result_filename = f"{key}.json"
        result_url = f"https://{s3_bucket}.s3.amazonaws.com/{result_filename}"
        return TaskStatusOutput(status='completed', result_url=result_url)
    else:
        return TaskStatusOutput(status=task_status)

@app.get("/get_results/{key}", response_model=EntityExtractionOutput)
async def get_results(key: str) -> EntityExtractionOutput:
    if key not in tasks:
        raise HTTPException(status_code=400, detail="Invalid key")

    task_status = tasks[key]["status"]

    if task_status == "completed":
        result_filename = f"{key}.json"
        try:
            # Download the JSON file from S3
            s3.download_file(s3_bucket, result_filename, result_filename)

            # Read the JSON file and parse its content
            with open(result_filename, "r") as result_file:
                results = json.load(result_file)

            # Remove the JSON file from the local directory
            os.remove(result_filename)

            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")
    elif task_status == "processing":
        raise HTTPException(status_code=200, detail="Task is still processing")
    else:
        raise HTTPException(status_code=500, detail="Task failed to complete")


@app.post('/docai_entities', response_model=EntityExtractionOutput)
async def extract_and_get_results(input_data: EntityExtractionInput) -> EntityExtractionOutput:
    s3_url = input_data.s3_url
    prompt_template = input_data.prompt_template

    if not s3_url:
        raise HTTPException(status_code=400, detail="S3 URL is required")

    
    local_pdf_path = f"temp/{s3_url.split('/')[-1]}"

    # Download the PDF file from S3
    try:
        s3.download_file(s3_bucket, s3_url.split('/')[-1], local_pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download PDF from S3: {str(e)}")

    pdf_text = doc_reader.read_text(local_pdf_path)
    #os.remove(local_pdf_path)

    if pdf_text:
        prompt_template = entity_extraction_prompt2
        try:
            extracted_entities = gpt_extractor.entity_extractor(pdf_text, prompt_template)
            return EntityExtractionOutput(entities=json.loads(extracted_entities))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract entities: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="PDF file could not be read")
