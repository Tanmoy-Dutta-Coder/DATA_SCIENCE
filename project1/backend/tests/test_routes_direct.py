import asyncio
from app.api.routes import get_agents, search_skills_endpoint

async def test_direct_routes():
    agents = await get_agents()
    assert len(agents) == 3
    print("Agents fetched directly:", [a.name for a in agents])

    # Test unknown agent throws ValueError
    try:
        await search_skills_endpoint(agent="nonexistent", q="test")
        assert False, "Should have thrown HTTPException"
    except Exception as e:
        print("Expected rejection for nonexistent agent:", type(e).__name__)

if __name__ == "__main__":
    asyncio.run(test_direct_routes())
    print("Direct route tests passed!")

