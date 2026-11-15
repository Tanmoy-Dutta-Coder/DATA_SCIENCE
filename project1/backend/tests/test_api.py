import asyncio
import httpx
from app.main import app

async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r_health = await client.get("/health")
        assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
        data_health = r_health.json()
        assert data_health["status"] == "healthy"
        print("Health check OK:", data_health)

        r_agents = await client.get("/api/agents")
        assert r_agents.status_code == 200, f"Agents check failed: {r_agents.text}"
        agents = r_agents.json()
        assert len(agents) == 3
        agent_names = [a["name"] for a in agents]
        print("Loaded agents OK:", agent_names)

        # Test invalid agent returns 400
        r_invalid = await client.get("/api/search?agent=nonexistent")
        assert r_invalid.status_code == 400
        print("Invalid agent validation OK: returned 400")

    print("All API integration tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
