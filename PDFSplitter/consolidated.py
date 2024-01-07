import os
from docx import Document

def consolidate_docx_to_txt(issuer_folder, output_folder_txt):
    issuer_name = os.path.basename(issuer_folder)
    txt_content = ''

    for filename in os.listdir(issuer_folder):
        if filename.endswith('.docx'):
            doc_path = os.path.join(issuer_folder, filename)
            doc = Document(doc_path)
            text = '\n\n'.join([paragraph.text.replace('•', '-') for paragraph in doc.paragraphs])

            # Append a header for each document with ===
            txt_content += f'=== {filename} ===\n\n{text}\n\n'

    # Write to Text file
    with open(os.path.join(output_folder_txt, f'{issuer_name}.txt'), 'w') as txt_file:
        txt_file.write(txt_content)

# Create directories if they don't exist
os.makedirs('textFiles', exist_ok=True)

# Path to the credit_card_data folder
credit_card_data_folder = 'credit_card_data'

# Process each issuer's folder
for issuer in os.listdir(credit_card_data_folder):
    issuer_folder = os.path.join(credit_card_data_folder, issuer)
    if os.path.isdir(issuer_folder):
        consolidate_docx_to_txt(issuer_folder, 'textFiles')
