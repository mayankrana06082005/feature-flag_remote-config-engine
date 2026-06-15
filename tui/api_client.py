import httpx
from typing import List, Dict, Any

class BackendClient:
    """A thin asynchronous HTTP client to communicate with the FastAPI backend."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    async def list_flags(self) -> List[Dict[str, Any]]:
        # Use async with to create the client INSIDE the active event loop
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get("/flags")
            response.raise_for_status()
            return response.json()

    async def toggle_flag(self, flag_id: str, current_status: bool) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(
                f"/flags/{flag_id}", 
                json={"enabled": not current_status}
            )
            response.raise_for_status()
            return response.json()
    
    async def create_config(self, config_data: dict) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post("/configs", json=config_data)
            response.raise_for_status()
            return response.json()

    async def delete_flag(self, flag_id: str) -> None:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.delete(f"/flags/{flag_id}")
            response.raise_for_status()

    async def list_configs(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get("/configs")
            response.raise_for_status()
            return response.json()
    
    async def create_flag(self, flag_data: dict) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post("/flags", json=flag_data)
            response.raise_for_status()
            return response.json()

    async def update_flag(self, flag_id: str, flag_update: dict) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(f"/flags/{flag_id}", json=flag_update)
            response.raise_for_status()
            return response.json()

    async def update_config(self, config_id: str, config_update: dict) -> Dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(f"/configs/{config_id}", json=config_update)
            response.raise_for_status()
            return response.json()

# Global instance for the TUI to use
api = BackendClient()
