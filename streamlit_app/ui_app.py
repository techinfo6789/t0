
import os
import tempfile
import streamlit as st
from PIL import Image
import base64
import requests
import pandas as pd
from io import BytesIO
from ui_utils import display_pdf, display_result
# Add the provided helper functions here (pdf_page_to_image, display_result, display_pdf, get_excel_download_link)
from ui_config import pdf_temp_folder
#from utils.gen_utils import check_dir
API_BASE_URL = "http://localhost:5001/pdf_extract"  # Replace with the actual API base URL




import requests
import pandas as pd

def get_dataframes_from_api(pdf_file_path, doc_type=None):
    url = f'{API_BASE_URL}/v1/extract'
    files = {'pdf_file': open(pdf_file_path, 'rb')}
    data = {'doc_type': doc_type} if doc_type else None

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        json_data = response.json()
        tables = json_data['tables']

        dataframes = {}
        for page, table in tables.items():
            df = pd.DataFrame(table)
            dataframes[int(page)] = df

        return dataframes
    else:
        raise Exception(f"Error: {response.status_code}")






if not os.path.exists(pdf_temp_folder):
    os.mkdir(pdf_temp_folder)

def display_result(tables):
    for page, table in tables.items():
        st.subheader(f"Page {page}")
        st.write(pd.DataFrame(table))

st.set_page_config(layout="wide")
st.title("PDF Document Processing")

st.header("Upload a PDF file")
pdf_file = st.file_uploader("", type="pdf")

if pdf_file:
    with st.spinner("Uploading PDF..."):
        pdf_save_path = os.path.join(pdf_temp_folder, pdf_file.name)

        with open(pdf_save_path, "wb") as f:
            f.write(pdf_file.getbuffer())

    st.success("PDF file uploaded.")
    display_pdf(pdf_save_path)

    st.header("Choose an action")
    action = st.selectbox("", ["", "Classify document", "Extract tables"])
    if action == "Classify document":
        with st.spinner("Classifying document..."):
            response = requests.post(
                f"{API_BASE_URL}/v1/classify", files={"pdf_file": open(pdf_save_path, 'rb')}
            )
            result = response.json()

        if "error" in result:
            st.error(result["error"])
        else:
            st.write(f"Document type: {result['document_type']}")

    elif action == "Extract tables":
        with st.spinner("Extracting tables..."):
            tables = get_dataframes_from_api(pdf_save_path)

        display_result(tables)



