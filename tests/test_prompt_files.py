from seo_incident_copilot.ai.prompt_manager import PromptManager
from seo_incident_copilot.config import default_config


def test_prompt_manager_loads_all_tiers():
    manager = PromptManager(default_config().prompts_dir)
    for tier in ["cheap", "middle", "expensive"]:
        prompt = manager.load_prompt(tier)
        assert "Return strict JSON" in prompt or "Return JSON schema" in prompt
        assert "Business objective" in prompt
        assert "Technical objective" in prompt
