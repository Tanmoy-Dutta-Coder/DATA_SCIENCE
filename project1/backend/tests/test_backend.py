from app.services.config_service import config_service
from app.services.search_service import search_service

def test_load_agents_config():
    agents = config_service.get_all_agents()
    assert len(agents) >= 3, f"Expected at least 3 agents, got {len(agents)}"
    agent_ids = {a.id for a in agents}
    assert "antigravity" in agent_ids
    assert "claude" in agent_ids
    assert "codex" in agent_ids

    # Verify required fields exist for each agent
    for a in agents:
        assert a.display_name, f"Agent {a.id} missing display_name"
        assert len(a.file_patterns) > 0, f"Agent {a.id} missing file_patterns"
        assert len(a.repo_topics) > 0, f"Agent {a.id} missing repo_topics"
        assert a.install_path_hint, f"Agent {a.id} missing install_path_hint"
        print(f"Verified {a.id}: {a.display_name} -> {a.install_path_hint}")

def test_query_builders():
    antigravity_agent = config_service.get_agent("antigravity")
    assert antigravity_agent is not None
    q1 = search_service._build_code_query_tier1(antigravity_agent, "pdf parser")
    assert "filename:SKILL.md" in q1
    assert "pdf parser" in q1

    claude_agent = config_service.get_agent("claude")
    assert claude_agent is not None
    q2 = search_service._build_code_query_tier2(claude_agent, "mcp")
    assert "filename:CLAUDE.md" in q2
    assert "mcp" in q2

    codex_agent = config_service.get_agent("codex")
    assert codex_agent is not None
    q3 = search_service._build_repo_query(codex_agent, "test")
    assert "topic:copilot-instructions" in q3 or "copilot" in q3

if __name__ == "__main__":
    test_load_agents_config()
    test_query_builders()
    print("All backend tests with agents_config.json passed successfully!")
