from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
import time
import re
import logging
import redis
from flask import Flask
from flask_cors import CORS

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Set up Redis client
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.Redis.from_url(redis_url)

# Global variables 
message_history = [] #store message history

# Global variable declaration
global thread_id
thread_id = None


app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

# Load environment variables from .env file
load_dotenv()

# Retrieve your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    app.logger.error("The OPENAI_API_KEY environment variable is not set.")
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

# Set the headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "assistants=v1"
}

def create_thread():
    global thread_id  # Use the global thread_id variable
    thread_url = "https://api.openai.com/v1/threads"

    try:
        thread_response = requests.post(thread_url, headers=headers)

        if thread_response.status_code == 200:
            thread_id = thread_response.json()['id']
            # Store thread_id in Redis
            redis_client.set('thread_id', thread_id)
            app.logger.debug(f"Thread created with ID: {thread_id}")
            return thread_id
        else:
            app.logger.error(f"Failed to create thread. Status code: {thread_response.status_code}")
            app.logger.error(f"Response: {thread_response.json()}")
            return None
    except Exception as e:
        app.logger.error(f"Exception occurred while creating thread: {e}")
        return None

    
def get_prompt_suggestions(ai_response):
    global message_history  # Access the global message history

    chat_completion_url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": message_history + [
            {
                "role": "system",
                "content": (
            "Below is a response from a credit card advisor chatbot. Based on this response, ALWAYS generate three potential follow-up "
            "inquiries or statements that a user could ask or say to the chatbot. These follow-ups should be relevant to the "
            "content of the chatbot's response, aimed at helping the user to delve deeper into the advice given or to clarify"
            "specific points in less than 10 words. The follow-ups can be either questions or statements, but they should be brief and to the point. "
            "Please format the output as three numbered items: 1, 2, and 3."
            )
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
    app.logger.debug("Rendering index page")
    return render_template('index.html')

# Endpoint to receive messages from the UI and send responses
@app.route('/send-message', methods=['POST'])
def send_message():
    global message_history
    data = request.json
    user_message = data['message']
    app.logger.debug(f"Received message: {user_message}")

    # Add the user's message to the message history
    message_history.append({
        "role": "user",
        "content": user_message
    })

    # Retrieve the current thread ID from Redis
    current_thread_id = get_thread_id()
    if current_thread_id is None:
        app.logger.error("No thread ID found. Creating a new thread.")
        current_thread_id = create_thread()
        if current_thread_id is None:
            return jsonify({'reply': "Failed to create thread."}), 500

    # Use the current_thread_id in your logic
    if not create_message(current_thread_id, user_message):
        return jsonify({'reply': "Failed to create message."}), 500

    run_id = create_run(current_thread_id)
    if run_id is None:
        return jsonify({'reply': "Failed to create run."}), 500

    # Wait for the run to complete
    while True:
        run_status = fetch_run_status(current_thread_id, run_id)
        if run_status is None or run_status['status'] in ['failed', 'cancelled']:
            return jsonify({'reply': "Run did not complete successfully."}), 500

        if run_status['status'] == 'completed':
            break

        time.sleep(2)  # Polling interval

    # Fetch and return the latest assistant message
    messages = fetch_thread_messages(current_thread_id)
    if messages:
        for message in messages['data']:
            if message['role'] == 'assistant':
                for content in message['content']:
                    if content['type'] == 'text':
                        ai_response = content['text']['value']
                        
                        # Add the AI's response to the message history
                        message_history.append({"role": "assistant", "content": ai_response})

                        # Get prompt suggestions
                        suggestions_content = get_prompt_suggestions(ai_response)

                        # Add the prompt suggestions to the message history
                        message_history.append({"role": "assistant", "content": suggestions_content})

                        # Return both AI response and suggestions in the JSON response
                        return jsonify({'reply': ai_response, 'suggestions': suggestions_content})

    return jsonify({'reply': "No response from assistant."}), 500

def get_thread_id():
    try:
        # Attempt to fetch the thread_id from Redis
        thread_id = redis_client.get('thread_id')

        # The get method returns a byte string, so decode it to a string
        if thread_id is not None:
            return thread_id.decode('utf-8')
        else:
            return None
    except Exception as e:
        app.logger.error(f"Error occurred while retrieving thread_id from Redis: {e}")
        return None



if __name__ == '__main__':
    thread_id = create_thread()  # Create a thread when the server starts
    if thread_id is None:
        app.logger.error("Failed to create an initial thread.")
        raise RuntimeError("Failed to create an initial thread.")

    app.run(debug=True)
