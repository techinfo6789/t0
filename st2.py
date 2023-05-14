import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to extract text from a URL
def extract_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        text = ' '.join(t.strip() for t in soup.stripped_strings)
        return text
    else:
        st.error(f"Error {response.status_code}: Unable to access {url}")
        return None

# Streamlit UI
st.title("Text Extractor from URL")
url = st.text_input("Enter the URL")

if url:
    if st.button("Extract Text"):
        text = extract_text(url)
        if text:
            st.subheader("Extracted Text:")
            st.write(text)
