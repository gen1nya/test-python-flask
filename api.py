import requests
from urllib.parse import parse_qs
import json
import yaml
import csv
import xmltodict
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REQUEST_MAX_RETRY = 3

def log_request_response(request, response=None, error=None):
    log_message = {
        'url': request.url,
        'method': request.method,
        'headers': dict(request.headers),
        'params': dict(request.params) if hasattr(request, 'params') else None,
        'response_status_code': response.status_code if response else None,
        #'response_content': response.text if response else None,
        'error': str(error) if error else None
    }
    logging.info(json.dumps(log_message, indent=2))

def get_data_from_url(url, headers, params):
    request_retry_count = 0
    response = None

    while request_retry_count < REQUEST_MAX_RETRY:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()  # Raise HTTPError for bad responses
            log_request_response(response.request, response=response)
            break
        except requests.exceptions.RequestException as e:
            log_request_response(response.request if response else requests.Request('GET', url, headers=headers, params=params), response=response, error=e)
            logging.warning(f"Request failed: {e}. Retrying {request_retry_count + 1}/{REQUEST_MAX_RETRY}")
            request_retry_count += 1

    if response is None:
        raise requests.exceptions.RequestException("Failed to fetch data after multiple retries.")

    content_type = response.headers.get("Content-Type", "")

    if content_type.startswith("application/json"):
        return response.json()
    elif content_type.startswith("application/xml"):
        return xmltodict.parse(response.text)
    elif content_type.startswith("application/x-www-form-urlencoded"):
        return parse_qs(response.text)
    elif content_type.startswith("application/yaml"):
        return yaml.load(response.text, Loader=yaml.Loader)
    elif content_type.startswith("text/plain") or content_type.startswith("text/html"):
        return response.text
    elif content_type.startswith("text/csv"):
        return list(csv.DictReader(response.text.splitlines()))
    else:
        logging.warning(f"Unknown content type: {content_type}")
        return response.text
