import os
import json
import base64
import requests
import streamlit as st
from typing import Dict
from time import sleep

API_BASE_URL = "http://0.0.0.0:8000"

def upload_pdf(file):
    url = f"{API_BASE_URL}/api/extract_entities"
    response = requests.post(url, files={'pdf': file})
    try:
        return response.json()
    except json.JSONDecodeError:
        st.error(f"Unexpected response from server: {response.status_code}\n{response.text}")
        return None

def check_status(key):
    url = f"{API_BASE_URL}/api/check_status/{key}"
    response = requests.get(url)
    return response.json()

def download_results(key):
    url = f"{API_BASE_URL}/api/get_results/{key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Unexpected response from server: {response.status_code}\n{response.text}")
        return None

st.title("PDF Extraction")

uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

tasks = []

for uploaded_file in uploaded_files:
    result = upload_pdf(uploaded_file)
    if result:
        task_id = result["key"]
        tasks.append({"name": uploaded_file.name, "task_id": task_id, "status": "processing"})

for task in tasks:
    with st.expander(f"Result: {task['name']}"):
        while task["status"] == "processing":
            sleep(5)
            status_response = check_status(task["task_id"])
            task["status"] = status_response["status"]

        if task["status"] == "completed":
            results = download_results(task["task_id"])

            st.write("Download the data:")
            results_string = json.dumps(results, indent=2)
            b64 = base64.b64encode(results_string.encode()).decode()
            download_link = f'<a href="data:application/json;base64,{b64}" download="{task["name"]}_results.json">Download Results</a>'
            st.markdown(download_link, unsafe_allow_html=True)
