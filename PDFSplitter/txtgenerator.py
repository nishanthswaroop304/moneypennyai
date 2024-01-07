import os

def concatenate_text_files(subfolder_path, destination_folder):
    """Concatenates all text files in a subfolder into one large text file."""
    all_text = []
    for filename in os.listdir(subfolder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(subfolder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                all_text.append(file.read())
    
    output_file_name = os.path.basename(subfolder_path) + ".txt"
    output_file_path = os.path.join(destination_folder, output_file_name)
    
    with open(output_file_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n\n".join(all_text))
    
    print(f"Successfully created {output_file_path}")

# Paths
base_path = "credit_card_data"
destination_folder = "TextFiles"

# Create destination folder if it doesn't exist
os.makedirs(destination_folder, exist_ok=True)

# Process each subfolder
for subfolder in os.listdir(base_path):
    subfolder_path = os.path.join(base_path, subfolder)
    if os.path.isdir(subfolder_path):
        concatenate_text_files(subfolder_path, destination_folder)
