
import streamlit as st
import pandas as pd
import fitz
import base64
from zipfile import ZipFile
from PIL import Image

def pdf_page_to_image(pdf_path, page_number):
    pdf_document = fitz.open(pdf_path)
    pdf_page = pdf_document.load_page(page_number)
    pdf_page_image = pdf_page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
    image = Image.frombytes("RGB", [pdf_page_image.width, pdf_page_image.height], pdf_page_image.samples)
    return image


def display_result(coa_df_dict):
    if not coa_df_dict:
        st.warning('No table found in the PDF file.')
    else:
        st.success('Table(s) extracted from the PDF file:')
        for page, df in coa_df_dict.items():
            st.subheader(f'Page {page}:')
            st.write(df)



def display_pdf(pdf_path):
    # Opening file from file path
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    #pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="800px" height="600px" type="application/pdf">'

    pdf_display = F'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank">Open PDF in new tab</a>'


    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def get_excel_download_link(coa_df_dict, excel_name):
    # Create an Excel writer object
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')

    # Iterate over the dictionary and save each value as a separate sheet in the Excel file
    for sheet_name, df in coa_df_dict.items():
        df.to_excel(writer, sheet_name=str(sheet_name), index=False)

    writer.save()

    # Display the extracted tables
    display_result(coa_df_dict)

    # Create a download link for the Excel file
    with open(excel_name, 'rb') as f:
        excel_bytes = f.read()
        b64 = base64.b64encode(excel_bytes).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{excel_name}">Download Excel file</a>'
        st.markdown(href, unsafe_allow_html=True)
