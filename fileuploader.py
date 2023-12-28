import os
import requests
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the .env file
api_key = os.getenv('OPENAI_API_KEY')

# Define the API URL
url = "https://api.openai.com/v1/files"

# Path to your folder containing PDF files
folder_path = 'CreditCardData'

# Open (or create) the file to store the upload details
with open('uploadedfiles.txt', 'w') as log_file:
    # Iterate over each file in the folder and upload it
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            
            # Define the headers
            headers = {
                "Authorization": f"Bearer {api_key}"
            }

            # Define the files and data payload
            files = {
                'purpose': (None, 'assistants'),
                'file': (filename, open(file_path, 'rb'))
            }

            # Make the POST request to upload the file
            response = requests.post(url, headers=headers, files=files)
            response_json = response.json()

            # Check if the upload was successful and log the details
            if response.status_code == 200:
                file_id = response_json.get('id')
                log_file.write(f"{filename}: {file_id}\n")
                print(f"Successfully uploaded {filename}, File ID: {file_id}")
            else:
                print(f"Failed to upload {filename}")

            # Close the file to avoid resource leakage
            files['file'][1].close()
