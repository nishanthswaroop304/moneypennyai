import os
import requests
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the .env file
api_key = os.getenv('OPENAI_API_KEY')

# Define the API URL
url = "https://api.openai.com/v1/assistants"

# Define the headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "assistants=v1"
}

# Read the file IDs from uploadedfiles.txt
file_ids = []
with open('uploadedfiles.txt', 'r') as file:
    for line in file:
        filename, file_id = line.strip().split(': ')
        file_ids.append(file_id)

# Define the data payload
data = {
    "instructions": "As a friendly and knowledgeable credit card advisor, your main goal is to provide concise, expert advice on credit cards in an informal and engaging manner. Please keep your responses brief aiming for 100 words or less, use emojis to make your advice more relatable and use bullets and numbering to make responses readable. When a user inquires about credit cards, respond with concrete suggestions and then progressively ask for their credit score and monthly spending budget to tailor your suggestions 📊. Always deeply analyze the uploaded documents first to identify most suitable credit card options. Consider rewards, welcome bonuses and annual fees while calculating benefits 💳. If specific credit card information or data is not available in the documents then, use your extensive knowledge base to offer the best possible recommendations. Remember, your advice should be clear, helpful, and delivered in a friendly, easy-to-understand manner 👍.",
    "name": "MoneyPenny",
    "tools": [{"type": "code_interpreter"}, {"type": "retrieval"}],
    "model": "gpt-4-1106-preview",
    "file_ids": file_ids  # Add the file IDs to the data payload
}

# Make the POST request to create the assistant
response = requests.post(url, json=data, headers=headers)
response_json = response.json()

# Print the response
print(response_json)

# Extract the assistant ID and store it in a file
assistant_id = response_json.get('id')
if assistant_id:
    with open('assistantid.txt', 'w') as file:
        file.write(assistant_id)
    print(f"Assistant ID '{assistant_id}' saved to assistantid.txt")
else:
    print("Failed to extract Assistant ID from the response.")
