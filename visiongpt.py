import os
import glob
import base64
import json
import csv
import requests
import time
from datetime import datetime

# Base directory setup: This is the directory where the script resides.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CONFIG_FOLDER: Folder for configuration files like API keys and settings.
CONFIG_FOLDER = os.path.join(BASE_DIR, "config")

# STATE_FOLDER: Folder for storing state-related files (e.g., last uploaded image info).
STATE_FOLDER = os.path.join(BASE_DIR, "state")

# SCREENSHOTS_FOLDER: Main folder for storing screenshot images.
SCREENSHOTS_FOLDER = os.path.join(BASE_DIR, "SCREENSHOTS")

# AUTO_FOLDER: Subfolder of SCREENSHOTS_FOLDER for automatically scanned images.
AUTO_FOLDER = os.path.join(SCREENSHOTS_FOLDER, "auto_scan")

# MANUAL_FOLDER: Subfolder of SCREENSHOTS_FOLDER for manually added images.
MANUAL_FOLDER = os.path.join(SCREENSHOTS_FOLDER, "manual_scan")

# LOGS_FOLDER: Main folder for logs.
LOGS_FOLDER = os.path.join(BASE_DIR, "LOGS")

# LOG_FOLDER_JSON: Subfolder of LOGS_FOLDER for storing JSON logs.
LOG_FOLDER_JSON = os.path.join(LOGS_FOLDER, "log_json")

# LOG_FOLDER_CSV: Subfolder of LOGS_FOLDER for storing CSV logs.
LOG_FOLDER_CSV = os.path.join(LOGS_FOLDER, "log_csv")

# Create the directories if they don't exist. Ensures proper folder structure.
for folder in [SCREENSHOTS_FOLDER, AUTO_FOLDER, MANUAL_FOLDER, STATE_FOLDER, LOGS_FOLDER, LOG_FOLDER_JSON, LOG_FOLDER_CSV, CONFIG_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Read API Key from config.txt
def read_config():
    config_file_path = os.path.join(CONFIG_FOLDER, "config.txt")
    config = {}
    try:
        with open(config_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("#") or not line:
                    # Skip comments and empty lines
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config
    except FileNotFoundError as e:
        print(f"Config file not found: {e}")
        raise
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise

        
# Read configuration values
config = read_config()
API_KEY = config.get("API_Key")
MODEL = config.get("Model")
PROMPT = config.get("Prompt")
MAX_TOKENS = int(config.get("Max_Tokens", 4000))
API_URL = config.get("API_URL")

LAST_UPLOADED_FILE = os.path.join(STATE_FOLDER, "last_uploaded.txt")
LAST_UPLOADED_MANUAL_FILE = os.path.join(STATE_FOLDER, "last_uploaded_manual.txt")

def find_latest_file(folder_path, extensions):
    """
    Finds the latest file in the given folder with specified extensions.
    """
    list_of_files = []
    for ext in extensions:
        list_of_files.extend(glob.glob(os.path.join(folder_path, f"*.{ext}")))
    return max(list_of_files, key=os.path.getctime, default=None)

def read_write_last_uploaded(file_path, file_name=None):
    """
    Reads or writes the last uploaded file name from/to the given state file.
    If file_name is None, it reads the file name. Otherwise, it writes file_name to the file.
    """
    try:
        if file_name is None:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read().strip()
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(file_name)
    except FileNotFoundError as e:
        print(f"State file not found: {e}")
        raise
    except Exception as e:
        print(f"Error accessing state file {file_path}: {e}")
        raise

def encode_image_to_base64(image_path):
    """
    Encodes the image at the given path to base64.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError as e:
        print(f"Image file not found: {e}")
        return None
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def send_vision_api_request(image_base64, max_retries=3, delay=2):
    """
    Sends a request to the OpenAI Vision API with retries for robustness.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        "max_tokens": MAX_TOKENS
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed, attempt {attempt + 1}/{max_retries}: {e}")
            time.sleep(delay)
    print("API request failed after maximum retries.")
    return None

def log_response_to_json(file_path, response):
    """
    Logs selected information from the given response to a unique JSON file for each processed file.
    Logs the filename (not the full path), model, created timestamp, and the content of the response.
    """
    # Extract just the filename from the file path
    filename = os.path.basename(file_path)

    # Extract the model, created timestamp, and content from the response
    model = response.get("model", "Unknown model")
    created_timestamp = response.get("created", "Unknown timestamp")
    content = "No content found."
    if response.get('choices'):
        messages = response['choices'][0].get('message', {})
        if 'content' in messages:
            content = messages['content']

    # Prepare the data to log
    log_data = {
        "file": filename,
        "model": model,
        "created": created_timestamp,
        "content": content
    }

    # Define a unique log file name based on the image file name
    log_file_name = os.path.join(LOG_FOLDER_JSON, f"{filename}_log_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json")
    
    # Write to the unique log file
    try:
        with open(log_file_name, 'w') as log_file:
            json.dump(log_data, log_file)
            log_file.write("\n")
    except Exception as e:
        print(f"Error logging response for {filename}: {e}")

def log_response_to_csv(file_path, response):
    """
    Logs selected information from the given response to a CSV file called 'total_log.csv'.
    Each processed file's data is appended as a new row.
    """
    # Extract just the filename from the file path
    filename = os.path.basename(file_path)

    # Extract the model, created timestamp, and content from the response
    model = response.get("model", "Unknown model")
    created_timestamp = response.get("created", "Unknown timestamp")
    content = "No content found."
    if response.get('choices'):
        messages = response['choices'][0].get('message', {})
        if 'content' in messages:
            content = messages['content']

    # Prepare the data to log in CSV format
    csv_data = [filename, model, created_timestamp, content]

    # Define the CSV log file name
    csv_log_file_name = os.path.join(LOG_FOLDER_CSV, "total_log.csv")

    # Write to the CSV log file
    try:
        with open(csv_log_file_name, mode='a', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            # If the file is empty, write the header first
            if file.tell() == 0:
                csv_writer.writerow(["File", "Model", "Created", "Content"])
            csv_writer.writerow(csv_data)
    except Exception as e:
        print(f"Error logging response to CSV for {filename}: {e}")
        

def process_image(file_path, is_manual=False):
    """
    Process an image file: analyze it and log the response.
    """
    image_base64 = encode_image_to_base64(file_path)
    if image_base64:
        response = send_vision_api_request(image_base64)
        if response:
            # Extract the content field from the response
            content = 'No content found.'
            if response.get('choices'):
                messages = response['choices'][0].get('message', {})
                if 'content' in messages:
                    content = messages['content']

            filename = os.path.basename(file_path)
            print(f"Analysis for {filename}:\n")
            print(content)
            print() 

            if not is_manual:
                log_response_to_json(file_path, response)
                log_response_to_csv(file_path, response)

def main():
    """
    Main loop to process automated and manual inputs.
    """
    waiting_message_printed = False

    while True:
        try:
            latest_file = find_latest_file(AUTO_FOLDER, ["png"])
            last_uploaded = read_write_last_uploaded(LAST_UPLOADED_FILE)

            latest_manual_file = find_latest_file(MANUAL_FOLDER, ["png", "jpg", "gif"])
            last_uploaded_manual = read_write_last_uploaded(LAST_UPLOADED_MANUAL_FILE)

            new_image_found = False

            if latest_file and latest_file != last_uploaded:
                print("Image received, sending data to OpenAI Vision API...")
                print() 
                process_image(latest_file)
                read_write_last_uploaded(LAST_UPLOADED_FILE, latest_file)
                new_image_found = True

            if latest_manual_file and latest_manual_file != last_uploaded_manual:
                print("Image received, sending data to OpenAI Vision API...")
                print() 
                process_image(latest_manual_file, is_manual=True)
                read_write_last_uploaded(LAST_UPLOADED_MANUAL_FILE, latest_manual_file)
                new_image_found = True

            if not new_image_found:
                if not waiting_message_printed:
                    print("Waiting for image to process...")
                    print() 
                    waiting_message_printed = True
            else:
                waiting_message_printed = False

            time.sleep(5)  # Wait for 5 seconds before next iteration to reduce CPU usage

        except KeyboardInterrupt:
            print("\nGracefully shutting down.")
            break

if __name__ == "__main__":
    main()
