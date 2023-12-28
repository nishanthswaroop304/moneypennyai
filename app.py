from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
import time
import re

# Global variable to store message history
message_history = []


app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Retrieve your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

# Set the headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "assistants=v1"
}

# Create a thread
def create_thread():
    thread_url = "https://api.openai.com/v1/threads"
    thread_response = requests.post(thread_url, headers=headers)
    if thread_response.status_code == 200:
        thread_id = thread_response.json()['id']
        return thread_id
    else:
        print(f"Failed to create thread. Status code: {thread_response.status_code}")
        print("Response:")
        print(thread_response.json())
        return None
    
def get_prompt_suggestions(ai_response):
    global message_history  # Access the global message history

    chat_completion_url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": message_history + [
            {
                "role": "system",
                "content": "You are an expert in crafting concise follow-up questions. Your task is to analyze responses provided by a credit card picker chatbot, as shared by the user. Imagine yourself as a curious user and generate three numbered follow-up questions. Each question should be direct and limited to a maximum of seven words."
            },
            {
                "role": "user",
                "content": ai_response
            }
        ]
    }
    response = requests.post(chat_completion_url, headers=headers, json=payload)
    if response.status_code == 200:
        suggestions = response.json()
        if 'choices' in suggestions and len(suggestions['choices']) > 0:
            content = suggestions['choices'][0]['message']['content']
            #print("Prompt Suggestions Content:", content)
            return content
        else:
            #print("No suggestions found in response.")
            return None
    else:
        #print("Error fetching prompt suggestions:", response.json())
        return None


# Function to create a message
def create_message(thread_id, message_content):
    message_url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    message_data = {
        "role": "user",
        "content": message_content
    }
    message_response = requests.post(message_url, headers=headers, json=message_data)
    return message_response.status_code == 200

# Function to create a run
def create_run(thread_id):
    # Read assistant ID from assistantid.txt file
    with open('assistantid.txt', 'r') as file:
        assistant_id = file.read().strip()

    run_url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    run_data = {
        "assistant_id": assistant_id
    }
    run_response = requests.post(run_url, headers=headers, json=run_data)
    if run_response.status_code == 200:
        return run_response.json()['id']
    else:
        return None

# Function to fetch the run status
def fetch_run_status(thread_id, run_id):
    run_status_url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    status_response = requests.get(run_status_url, headers=headers)
    return status_response.json() if status_response.status_code == 200 else None

# Function to fetch messages from the thread
def fetch_thread_messages(thread_id):
    message_url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    message_response = requests.get(message_url, headers=headers)
    return message_response.json() if message_response.status_code == 200 else None

# Endpoint to render the chat interface
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to receive messages from the UI and send responses
@app.route('/send-message', methods=['POST'])
def send_message():
    global message_history
    data = request.json
    user_message = data['message']

    # Add the user's message to the message history
    message_history.append({
        "role": "user",
        "content": user_message
    })

    global thread_id

    if not create_message(thread_id, user_message):
        return jsonify({'reply': "Failed to create message."}), 500

    run_id = create_run(thread_id)
    if run_id is None:
        return jsonify({'reply': "Failed to create run."}), 500

    # Wait for the run to complete
    while True:
        run_status = fetch_run_status(thread_id, run_id)
        if run_status is None or run_status['status'] in ['failed', 'cancelled']:
            return jsonify({'reply': "Run did not complete successfully."}), 500

        if run_status['status'] == 'completed':
            break

        time.sleep(2)  # Polling interval

    # Fetch and return the latest assistant message
    messages = fetch_thread_messages(thread_id)
    if messages:
        for message in messages['data']:
            if message['role'] == 'assistant':
                for content in message['content']:
                    if content['type'] == 'text':
                        ai_response = content['text']['value']
                        
                        # Add the AI's response to the message history
                        message_history.append({"role": "assistant", "content": ai_response})

                        # Get prompt suggestions and log to the terminal
                        suggestions_content = get_prompt_suggestions(ai_response)

                        # Add the prompt suggestions to the message history
                        message_history.append({"role": "assistant", "content": suggestions_content})

                        # Return both AI response and suggestions in the JSON response
                        return jsonify({'reply': ai_response, 'suggestions': suggestions_content})

    return jsonify({'reply': "No response from assistant."}), 500


if __name__ == '__main__':
    thread_id = create_thread()  # Create a thread when the server starts
    if thread_id is None:
        raise RuntimeError("Failed to create an initial thread.")

    app.run(debug=True)
