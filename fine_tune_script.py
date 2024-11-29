import openai
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key is missing. Set it in your environment variables.")
openai.api_key = api_key

# File paths
DATASET_FILE = "dataset.jsonl"  # Replace with your dataset file path
PREPARED_DATASET_FILE = "prepared_dataset.jsonl"

def prepare_dataset(file_path):
    """Prepare the dataset for fine-tuning."""
    print("Preparing dataset...")
    response = openai.File.create(
        file=open(file_path),
        purpose="fine-tune"
    )
    file_id = response["id"]
    print(f"Uploaded dataset. File ID: {file_id}")
    return file_id

def start_fine_tuning(file_id):
    """Start fine-tuning with the uploaded file."""
    print("Starting fine-tuning...")
    with open("dataset.jsonl", "rb") as file:
        response = openai.File.upload(file=file, purpose="fine-tune")

    fine_tune_id = response["id"]
    print(f"Fine-tuning started. Fine-tune ID: {fine_tune_id}")
    return fine_tune_id

def monitor_fine_tuning(fine_tune_id):
    """Monitor the fine-tuning process until completion."""
    print("Monitoring fine-tuning process. This may take some time...")
    while True:
        response = openai.FineTune.retrieve(id=fine_tune_id)
        status = response["status"]
        print(f"Status: {status}")
        if status in ["succeeded", "failed"]:
            break
        time.sleep(30)  # Wait 30 seconds before checking again

    if status == "succeeded":
        model_id = response["fine_tuned_model"]
        print(f"Fine-tuning completed successfully. Model ID: {model_id}")
        return model_id
    else:
        print("Fine-tuning failed.")
        return None

def save_model_id(model_id, file_path="fine_tuned_model.txt"):
    """Save the fine-tuned model ID to a file."""
    with open(file_path, "w") as f:
        f.write(model_id)
    print(f"Model ID saved to {file_path}")

def main():
    # Step 1: Prepare the dataset
    if not os.path.exists(DATASET_FILE):
        print(f"Dataset file {DATASET_FILE} not found. Please create it in JSONL format.")
        return
    
    # Step 2: Upload the dataset and get file ID
    file_id = prepare_dataset(DATASET_FILE)

    # Step 3: Start fine-tuning and get fine-tune ID
    fine_tune_id = start_fine_tuning(file_id)

    # Step 4: Monitor the fine-tuning process
    model_id = monitor_fine_tuning(fine_tune_id)

    # Step 5: Save the fine-tuned model ID for later use
    if model_id:
        save_model_id(model_id)

if __name__ == "__main__":
    main()
