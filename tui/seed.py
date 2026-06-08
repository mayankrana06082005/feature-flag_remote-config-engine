import httpx
import asyncio

async def seed():
    base_url = "http://127.0.0.1:8000"
    
    # The exact flags from your project requirements mockup!
    flags = [
        {
            "id": "new_checkout_flow",
            "name": "New Checkout Flow",
            "description": "Redesigned 3-step checkout",
            "enabled": True,
            "targeting_rule": {"type": "group", "groups": ["beta_users"]}
        },
        {
            "id": "dark_mode_beta",
            "name": "Dark Mode",
            "description": "App-wide dark mode",
            "enabled": False,
            "targeting_rule": {"type": "everyone"}
        },
        {
            "id": "ai_recommendations",
            "name": "AI Recommendations",
            "description": "Smart product suggestions",
            "enabled": True,
            "targeting_rule": {"type": "everyone"}
        }
    ]
    
    print(f"Connecting to backend at {base_url}...")
    
    async with httpx.AsyncClient() as client:
        for flag in flags:
            try:
                resp = await client.post(f"{base_url}/flags", json=flag)
                if resp.status_code == 200:
                    print(f"✅ Successfully created flag: {flag['id']}")
                elif resp.status_code == 400:
                    print(f"ℹ️ Flag already exists: {flag['id']}")
                else:
                    print(f"⚠️ Failed to create {flag['id']}: {resp.text}")
            except Exception as e:
                print(f"❌ Connection error! Is your FastAPI server running? Details: {e}")
                return

    print("\nDone! Go to your TUI and press 'r' to refresh!")

if __name__ == "__main__":
    asyncio.run(seed())