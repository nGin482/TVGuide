import requests

from exceptions.service_error import HTTPRequestError

class APIClient:


    @staticmethod
    def _make_request(method: str, url: str, additional_headers: dict):

        headers = {
            'User-Agent': 'Chrome/119.0.0.0'
        }

        headers.update(additional_headers)
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers
        )

        return response
    
    def get(self, endpoint: str, headers: dict = {}):
        
        response = APIClient._make_request('GET', endpoint, headers)
        if response.ok:
            return response.json()
        else:
            raise HTTPRequestError(f'Response returned status {response.status_code} {response.reason}')