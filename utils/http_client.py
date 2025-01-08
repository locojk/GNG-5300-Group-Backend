import requests
from utils.logger import Logger  # Assumes a logger utility is available

logger = Logger(__name__)


class HTTPClient:
    def __init__(self, headers=None):
        self.headers = headers if headers else {}

    def _log_request(self, method, url, data=None, params=None, headers=None):
        logger.info(f"Making {method} request to {url}")
        if params:
            logger.info(f"With params: {params}")
        if data:
            logger.info(f"With data: {data}")
        if headers:
            logger.info(f"With headers: {headers}")

    def _log_error(self, e, response=None):
        if response:
            logger.error(f"Request failed with status code {response.status_code}")
            logger.error(f"Response content: {response.text}")
        else:
            logger.error(f"Request failed: {e}")

    def get(self, url, params=None, headers=None):
        try:
            if not headers:
                headers = self.headers
            self._log_request("GET", url, params=params, headers=headers)
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            logger.info(f"GET request successful: {response.status_code}")
            return response  # Return the full response object
        except requests.exceptions.HTTPError as e:
            self._log_error(e, response)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"GET request failed: Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"GET request failed: Timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {e}")
        return None

    def post(self, url, data=None, json_data=None, headers=None):
        try:
            if not headers:
                headers = self.headers
            self._log_request("POST", url, data=data or json_data, headers=headers)
            response = requests.post(url, headers=headers, data=data, json=json_data)
            response.raise_for_status()
            logger.info(f"POST request successful: {response.status_code}")
            return response  # Return the full response object
        except requests.exceptions.HTTPError as e:
            self._log_error(e, response)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"POST request failed: Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"POST request failed: Timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
        return None

    def put(self, url, data=None, headers=None):
        try:
            if not headers:
                headers = self.headers
            self._log_request("PUT", url, data=data, headers=headers)
            response = requests.put(url, headers=headers, data=data)
            response.raise_for_status()
            logger.info(f"PUT request successful: {response.status_code}")
            return response  # Return the full response object
        except requests.exceptions.HTTPError as e:
            self._log_error(e, response)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"PUT request failed: Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"PUT request failed: Timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"PUT request failed: {e}")
        return None

    def delete(self, url, headers=None):
        try:
            if not headers:
                headers = self.headers
            self._log_request("DELETE", url, headers=headers)
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            logger.info(f"DELETE request successful: {response.status_code}")
            return response  # Return the full response object
        except requests.exceptions.HTTPError as e:
            self._log_error(e, response)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"DELETE request failed: Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"DELETE request failed: Timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE request failed: {e}")
        return None
