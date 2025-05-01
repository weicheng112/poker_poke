# src/player.py
"""
AutoGen wrapper for a poker player.

‣ In the MVP the engine calls solver_tool.get_action(state, agent) and
  ignores the LLM entirely.
‣ Later you can give the agent a true language role (banter, rationales,
  personality) just by tweaking its system/user prompts.
"""

from autogen import AssistantAgent
from dotenv import load_dotenv
load_dotenv()

# ---------- constants ---------------------------------------------------------
LLM_MODEL   = "gpt-4o-mini"   # cheap, fast; won’t actually be used at MVP
MAX_AUTOREPLY = 0             # 0 → no autonomous replies; engine drives turns


# ---------- agent class -------------------------------------------------------
class PlayerAgent(AssistantAgent):
    """
    A lightweight AutoGen AssistantAgent with:
        • name          – seat identifier ("P0", "P1", …)
        • blackboard    – dict where engine can drop private/public state
    """

    def __init__(self, name: str):
        super().__init__(
            name=name,
            system_message=(
                "You are a disciplined poker agent. "
                "Never reveal your private hole cards. "
                "All betting decisions are produced by an external GTO solver "
                "the engine will call on your behalf."
            ),
            llm_config={
                "config_list": [{"model": LLM_MODEL}],
                "cache_seed": 42           # deterministic if LLM ever invoked
            },
            max_consecutive_auto_reply=MAX_AUTOREPLY
        )

        # Storage slot for whatever the dealer wants to give you this turn:
        #   self.blackboard["state"] = { ... }
        self.blackboard = {}

    # -------------------------------------------------------------------------
    # For later: if you *do* want the LLM to speak, uncomment generate_reply
    # and let it read self.blackboard["state"], call a solver tool, etc.
    # -------------------------------------------------------------------------
    #
    # def generate_reply(self, messages, sender, config):
    #     """
    #     messages[-1]['content'] will contain the dealer's prompt
    #     with public info. Use self.blackboard for private info.
    #     Return JSON text like {"action":"call","amount":0,"chat":"..."}.
    #     """
    #     raise NotImplementedError("LLM-driven replies will come later")
    #
