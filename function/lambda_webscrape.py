import requests
import os
import shutil
import json
from bs4 import BeautifulSoup

# Fetch URL and extract text
def get_page_content(url):
    try:
        response = requests.get(url)
        if response.history:  # Check if there were any redirects
            print(f"Redirect detected for {url}")
            return None  # Return None to indicate a redirect occurred
        elif response:
            return response.text
        else:
            raise Exception("No response from the server.")
    except Exception as e:
        print(f"Error while fetching content from {url}: {e}")
        return None

def empty_tmp_folder():
    try:
        for filename in os.listdir('/tmp'):
            file_path = os.path.join('/tmp', filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        print("Temporary folder emptied.")
        return "Temporary folder emptied."
    except Exception as e:
        print(f"Error while emptying /tmp folder: {e}")
        return None

def save_to_tmp(filename, content):
    try:
        if content is not None:
            print(content)
            with open(f'/tmp/{filename}', 'w') as file:
                file.write(content)
            print(f"Saved {filename} to /tmp")
            return f"Saved {filename} to /tmp"
        else:
            raise Exception("No content to save.")
    except Exception as e:
        print(f"Error while saving {filename} to /tmp: {e}")
        return None

def check_tmp_for_data(query):
    try:
        data = []
        for filename in os.listdir('/tmp'):
            if query in filename:
                with open(f'/tmp/{filename}', 'r') as file:
                    data.append(file.read())
        print(f"Found {len(data)} file(s) in /tmp for query {query}")
        return data if data else None
    except Exception as e:
        print(f"Error while checking /tmp for query {query}: {e}")
        return None

# Modify handle_search function to use tmp folder instead of S3
def handle_search(event):
    # Extract 'inputURL' from parameters
    parameters = event.get('parameters', [])
    input_url = next((param['value'] for param in parameters if param['name'] == 'inputURL'), '')

    if not input_url:
        return {"error": "No URL provided"}

    # Ensure URL starts with http:// or https://
    if not input_url.startswith(('http://', 'https://')):
        input_url = 'http://' + input_url

    # Check /tmp directory first
    tmp_data = check_tmp_for_data(input_url)
    if tmp_data:
        return {"results": tmp_data}

    # Empty the /tmp directory before saving new files
    empty_tmp_result = empty_tmp_folder()
    if empty_tmp_result is None:
        return {"error": "Failed to empty /tmp folder"}

    # Scrape content from the provided URL
    content = get_page_content(input_url)
    if content is None:
        return {"error": "Failed to retrieve content"}

    # Parse and clean HTML content
    cleaned_content = parse_html_content(content)

    filename = input_url.split('//')[-1].replace('/', '_') + '.txt'
    save_result = save_to_tmp(filename, cleaned_content)

    if save_result is None:
        return {"error": "Failed to save to /tmp"}

    return {"results": {'url': input_url, 'content': cleaned_content}}


def parse_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    # Get text
    text = soup.get_text()
    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines and concatenate into a single string
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    # Truncate to ensure it does not exceed 25KB
    max_size = 25000  # Max size in characters
    if len(cleaned_text) > max_size:
        cleaned_text = cleaned_text[:max_size]  # Truncate to the max size
    
    return cleaned_text



def lambda_handler(event, context):
    # Initialize default success status code
    response_code = 200
    # Extract routing information from the incoming event
    action_group = event['actionGroup']    # Identifies the service group (e.g., 'webscrape')
    api_path = event['apiPath']           # The endpoint being called (e.g., '/search')

    # Log the complete incoming event for debugging
    print("THE EVENT: ", event)

    # Route the request based on API path
    if api_path == '/search':
        # Handle web scraping request by calling handle_search function
        result = handle_search(event)
    else:
        # If path not recognized, set 404 error and create error message
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"

    # Format the result in the required response_body structure
    # This wraps the result in a standardized JSON format
    response_body = {
        'application/json': {             # Specifies content type
            'body': result                # Contains the actual data/result
        }
    }

    # Create the action_response with full context
    # This includes metadata about the request and response
    action_response = {
        'actionGroup': event['actionGroup'],    # Service identifier
        'apiPath': event['apiPath'],           # Endpoint called
        'httpMethod': event['httpMethod'],      # HTTP method used (POST/GET)
        'httpStatusCode': response_code,        # Success/error status
        'responseBody': response_body           # The wrapped result
    }

    # Create the final api_response
    # This is the standardized outer wrapper required by AWS services
    api_response = {
        'messageVersion': '1.0',               # API version for compatibility
        'response': action_response            # Complete response with metadata
    }

    # Log response details for debugging/monitoring
    print("action_response: ", action_response)
    print("response_body: ", response_body)

    # Return the complete response to AWS Lambda
    return api_response
