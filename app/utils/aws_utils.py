import os
import requests

def download_pdf(url, file_path):
    # Check if the file already exists
    if os.path.isfile(file_path):
        print(f'File already exists at {file_path}')
        return
    
    # Download the file from the URL
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'Error downloading file from {url}: {e}')
        return
    
    # Save the file to the local directory
    try:
        with open(file_path, 'wb') as f:
            f.write(response.content)
    except IOError as e:
        print(f'Error saving file to {file_path}: {e}')
        return
    
    print(f'File downloaded to {file_path}')

if __name__ == '__main__':
    url = 'https://example.com/myfile.pdf'
    file_path = '/path/to/local/file.pdf'
    download_pdf(url, file_path)
