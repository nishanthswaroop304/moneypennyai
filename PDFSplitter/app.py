import os
import json
from docx import Document

def extract_data_from_docx(file_path):
    doc = Document(file_path)
    card_data = {}
    current_heading = None
    current_points = []

    for para in doc.paragraphs:
        if para.style.name == 'Heading 1':
            if current_heading is not None:
                card_data[current_heading] = current_points
                current_points = []
            current_heading = para.text
        else:
            current_points.append(para.text)

    if current_heading is not None:
        card_data[current_heading] = current_points

    return card_data

def process_issuer(issuer_path, issuer_name, output_directory):
    issuer_data = {}

    for filename in os.listdir(issuer_path):
        if filename.endswith('.docx'):
            file_path = os.path.join(issuer_path, filename)
            card_name = filename.replace('.docx', '')
            issuer_data[card_name] = extract_data_from_docx(file_path)

    output_file = os.path.join(output_directory, f"{issuer_name}.json")
    with open(output_file, 'w') as json_file:
        json.dump(issuer_data, json_file, indent=4)

    # Print statement after conversion to .json is complete
    print(f"JSON file for {issuer_name} created successfully.")

def generate_json_files(base_directory):
    # Change output directory to be relative to the root path of app.py
    root_directory = os.path.dirname(os.path.abspath(__file__))  # Gets the directory of app.py
    output_directory = os.path.join(root_directory, 'json_output')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for issuer in os.listdir(base_directory):
        issuer_path = os.path.join(base_directory, issuer)
        if os.path.isdir(issuer_path):
            process_issuer(issuer_path, issuer, output_directory)

# Usage
generate_json_files('credit_card_data')
