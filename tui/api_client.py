import httpx
from typing import List, Dict, Any

class BackendClient:
    """A thin asynchronous HTTP client to communicate with the FastAPI backend."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url)

    async def list_flags(self) -> List[Dict[str, Any]]:
        response = await self._client.get("/flags")
        response.raise_for_status()
        return response.json()

    async def toggle_flag(self, flag_id: str, current_status: bool) -> Dict[str, Any]:
        """Toggles the enabled status of a flag."""
        response = await self._client.patch(
            f"/flags/{flag_id}", 
            json={"enabled": not current_status}
        )
        response.raise_for_status()
        return response.json()

    async def delete_flag(self, flag_id: str) -> None:
        response = await self._client.delete(f"/flags/{flag_id}")
        response.raise_for_status()

    async def list_configs(self) -> List[Dict[str, Any]]:
        response = await self._client.get("/configs")
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()

# Global instance for the TUI to use
api = BackendClient()