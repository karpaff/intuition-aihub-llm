import requests
from typing import Dict, Any
from config import API_URL


class RagApiClient:
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url

    def get_answer(self, question: str, timeout: int = 30) -> Dict[str, Any]:
        response = requests.post(
            self.api_url,
            params={"question": question},
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
