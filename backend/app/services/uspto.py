import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class USPTOClient:
    BASE_URL = "https://developer.uspto.gov/api/v1"

    async def search(self, query: str):
        """Search USPTO patent database"""
        params = {
            "q": query,
            "api_key": os.getenv("USPTO_API_KEY")  # Set in .env
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/patent", params=params)
            response.raise_for_status()
            return response.json()
