from typing import TypeVar
import requests

TBody = TypeVar('TBody', list, dict)

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
    
    def get(self, endpoint: str, headers: dict = {}) -> TBody:
        
        response = APIClient._make_request('GET', endpoint, headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Response returned status {response.status_code}')