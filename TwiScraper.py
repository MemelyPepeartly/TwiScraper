import os
import json
import requests
from tkinter import Tk, Label, Entry, Button, filedialog, Checkbutton, IntVar, Text, Scrollbar

def fetch_and_save_images(tags, api_key, directory, include_explicit):
    base_url = "https://twibooru.org/api/v3/search/posts"
    headers = {'Authorization': api_key}

    # Initialize params with tags
    params = {'q': tags}

    # If including explicit content, set the appropriate filter ID
    if include_explicit.get() == 1:
        params['filter_id'] = '2'  # ID for the "Everything" filter

    # Create directories for images and tags
    images_dir = os.path.join(directory, "images")
    tags_dir = os.path.join(directory, "tags")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(tags_dir, exist_ok=True)

    log.insert("end", "Starting download...\n")
    for tag in tags.split(','):
        page = 1
        while True:
            # Update params with current tag and page
            params.update({'q': tag.strip(), 'page': page})
            response = requests.get(base_url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if not data['posts']:
                    break  # Break the loop if no images are returned

                for image in data['posts']:
                    image_url = image['representations']['full']
                    image_tags = image['tags']
                    save_image(image_url, images_dir, tags_dir, image['id'], image_tags)
                    log.insert("end", f"Saved image {image['id']}\n")

                page += 1  # Increment to get the next page of results
            else:
                log.insert("end", f"Failed to retrieve images for tag {tag}\n")
                break
    log.insert("end", "Download complete.\n")


def save_image(url, images_dir, tags_dir, image_id, tags):
    response = requests.get(url)
    if response.status_code == 200:
        file_extension = os.path.splitext(url)[1]
        image_path = os.path.join(images_dir, f"{image_id}{file_extension}")
        with open(image_path, 'wb') as file:
            file.write(response.content)
        save_tags(image_path, tags_dir, tags)

def save_tags(image_path, tags_dir, tags):
    image_id = os.path.splitext(os.path.basename(image_path))[0]
    tags_path = os.path.join(tags_dir, f"{image_id}.txt")

    # Process tags to include both spaced and underscored versions
    processed_tags = []
    for tag in tags:
        spaced = tag
        underscored = tag.replace(' ', '_')
        processed_tags.extend([spaced, underscored])

    with open(tags_path, 'w') as file:
        file.write(', '.join(processed_tags))

def browse_button():
    dirname = filedialog.askdirectory()
    directory_entry.delete(0, "end")
    directory_entry.insert(0, dirname)

def submit():
    tags = tags_entry.get()
    api_key = api_key_entry.get()
    directory = directory_entry.get()
    # Pass include_explicit.get() to the fetch_and_save_images function
    fetch_and_save_images(tags, api_key, directory, include_explicit)

def load_config():
    # Construct the path to config.json file relative to the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'r') as file:
        return json.load(file)
    
def re_encode_files(directory):
    log.insert("end", "Re-encoding text files to UTF-8...\n")
    text_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    for filename in text_files:
        file_path = os.path.join(directory, filename)
        # Open the file in the original encoding and read the contents
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        # Write the contents back to the file in UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    log.insert("end", "Re-encoding completed.\n")

# Load configuration
config = load_config()
api_key = config.get("api_key")

# Set up the GUI
root = Tk()
root.title("Twiborru Image Downloader")

# Checkbox for explicit images
include_explicit = IntVar()
Checkbutton(root, text="Include Explicit Images", variable=include_explicit).grid(row=4, columnspan=2)

# Processing log area
log = Text(root, height=10, width=50)
scroll = Scrollbar(root, command=log.yview)
log.configure(yscrollcommand=scroll.set)
log.grid(row=5, column=0, columnspan=2)
scroll.grid(row=5, column=2, sticky='nsew')

Label(root, text="Tags (comma-separated):").grid(row=0)
Label(root, text="API Key:").grid(row=1)

api_key_entry = Entry(root, show="*")
api_key_entry.grid(row=1, column=1)
# Ensure the API key is inserted after the entry widget has been created
if api_key:  # Only insert if api_key is not None or empty
    api_key_entry.insert(0, api_key)

Label(root, text="Save Directory:").grid(row=2)

tags_entry = Entry(root)
directory_entry = Entry(root)

tags_entry.grid(row=0, column=1)
directory_entry.grid(row=2, column=1)

Button(root, text="Browse", command=browse_button).grid(row=2, column=2)
Button(root, text="Submit", command=submit).grid(row=3, column=1)
Button(root, text="Re-encode Text Files", command=lambda: re_encode_files(directory_entry.get())).grid(row=6, column=1)


root.mainloop()

