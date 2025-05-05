# src/player.py

from autogen import AssistantAgent
from dotenv import load_dotenv
load_dotenv()

# ---------- constants ---------------------------------------------------------
LLM_MODEL   = "gpt-4o-mini"   
MAX_AUTOREPLY = 0             


# ---------- agent class -------------------------------------------------------
class PlayerAgent(AssistantAgent):
    """
    A lightweight AutoGen AssistantAgent with:
        • name          – seat identifier ("P0", "P1", …)
        • blackboard    – dict where engine can drop private/public state
    """

    def __init__(self, name: str):
        # Create a detailed system message for the agent with a unique personality
        from src.solver_tool import get_agent_personality
        
        # Set up a seed based on the name to ensure consistent personality
        import random
        random.seed(hash(name))
        
        # Generate personality traits
        personality_traits = get_agent_personality(None)
        
        # Define personality type based on traits
        personality_type = "aggressive"
        if personality_traits["bluff_tendency"] > 0.4:
            personality_type = "bluffer"
        elif personality_traits["risk_tolerance"] < 0.4:
            personality_type = "conservative"
        
        # Create a comprehensive system message
        system_message = f"""
You are a poker player named {name} with a {personality_type} playing style.

Your personality traits:
- Aggression: {personality_traits["aggression"]:.2f} (0-1 scale)
- Bluff tendency: {personality_traits["bluff_tendency"]:.2f} (0-1 scale)
- Risk tolerance: {personality_traits["risk_tolerance"]:.2f} (0-1 scale)

Core principles:
1. NEVER reveal your exact hole cards to opponents
2. Your betting decisions are determined by an external GTO solver
3. Your role is to communicate naturally with other players
4. Respond to messages in a way that reflects your personality
5. Comment on the game state and actions in an engaging way

As a {personality_type} player:
{
"You're assertive and confident. You believe in applying pressure and taking control of the table. You're not afraid to make big bets when you sense weakness."
if personality_type == "aggressive" else
"You enjoy the psychological aspect of poker. You're unpredictable and like to keep opponents guessing. You occasionally represent hands you don't have."
if personality_type == "bluffer" else
"You're patient and calculated. You prefer to minimize risk and wait for strong hands. You're observant of your opponents' patterns and exploit them methodically."
}

Adapt your communication style to the current game state, your action, and previous messages.
"""
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config={
                "config_list": [{"model": LLM_MODEL}],
                "cache_seed": None,  # Allow for more varied responses
                "temperature": 0.8,  # Slightly higher temperature for more personality
            },
            max_consecutive_auto_reply=MAX_AUTOREPLY,
            human_input_mode="NEVER"  # Don't wait for human input
        )

        # Storage slot for whatever the dealer wants to give you this turn:
        #   self.blackboard["state"] = { ... }
        self.blackboard = {}
        
        # Add a message history to track previous messages
        self.message_history = []
        
        # Store personality traits for reference
        self.personality = personality_traits
        self.personality_type = personality_type


    def generate_reply(self, messages, sender, config):
        """
        Use the LLM to generate a natural response based on the game state and previous messages.
        This method leverages the system prompt and the LLM's capabilities for more natural agent communication.
        """
        import json
        from src.solver_tool import get_action, evaluate_hand_strength
        
        # Get the current state from the blackboard
        state = self.blackboard.get("state")
        if not state:
            return "No state available in blackboard"
        
        # Get the action from the solver
        action = get_action(state, self)
        
        # Extract game information for context
        game_stage = "preflop"
        if hasattr(state, "board") and state.board:
            if len(state.board) == 3:
                game_stage = "flop"
            elif len(state.board) == 4:
                game_stage = "turn"
            elif len(state.board) == 5:
                game_stage = "river"
        
        # Get pot size
        pot = getattr(state, "pot", 0)
        
        # Get board information
        board_info = ""
        if hasattr(state, "board") and state.board:
            board_info = f"Board: {state.board}"
        
        # Get hand strength
        hand_strength = evaluate_hand_strength(state, self)
        
        # Extract a simple action name from the action string
        action_str = str(action).lower()
        action_name = "play"
        if "fold" in action_str:
            action_name = "fold"
        elif "check" in action_str:
            action_name = "check"
        elif "call" in action_str:
            action_name = "call"
        elif "raise" in action_str:
            action_name = "raise"
        elif "bet" in action_str:
            action_name = "bet"
        
        # Extract previous messages for context
        previous_messages = []
        for m in messages:
            if "content" in m and isinstance(m["content"], str):
                if "Opponent says:" in m["content"]:
                    # Extract just the opponent's message
                    opponent_msg = m["content"].replace("Opponent says:", "").strip()
                    previous_messages.append(f"Opponent: {opponent_msg}")
                elif "turn" in m["content"].lower() and "round" in m["content"].lower():
                    # This is likely a dealer message
                    previous_messages.append(f"Dealer: {m['content']}")
        
        # Create a context message for the LLM
        context_message = {
            "role": "user",
            "content": f"""
Current game state:
- Stage: {game_stage}
- Pot: {pot}
- {board_info}
- Your action: {action_name}
- Your hand strength: {"strong" if hand_strength > 0.7 else "medium" if hand_strength > 0.4 else "weak"}

Recent table messages:
{previous_messages[-3:] if previous_messages else "No previous messages"}

Generate a short, natural poker table chat message (1-2 sentences) that reflects your personality, current action, and game state. NEVER reveal your exact cards.
"""
        }
        
        # Use the LLM to generate a response
        try:
            # Use AutoGen's built-in LLM capabilities to generate a response
            # This uses the system prompt we defined in __init__ along with the context message
            
            # Create a proper message list for the LLM
            llm_messages = [
                {"role": "system", "content": self._system_message},
                context_message
            ]
            
            # Use the agent's generate method to get a response from the LLM
            from autogen.agentchat.contrib.capabilities.llm_capability import LLMCapability
            
            # Get the LLM capability from the agent
            llm_capability = None
            for capability in self._capabilities:
                if isinstance(capability, LLMCapability):
                    llm_capability = capability
                    break
            
            if llm_capability:
                # Use the LLM capability to generate a response
                chat_message = llm_capability.generate(llm_messages)
            else:
                # Fallback to using the client directly if available
                try:
                    from autogen.oai.client import OpenAIWrapper
                    
                    # Create an OpenAI client with the agent's configuration
                    client = OpenAIWrapper(**self.llm_config)
                    
                    # Generate a response
                    response = client.create(messages=llm_messages)
                    chat_message = response.choices[0].message.content
                except Exception as inner_e:
                    # If direct client access fails, use a simpler approach
                    # This is a last resort fallback
                    import random
                    
                    # Create some fallback responses in case all LLM methods fail
                    fallback_responses = [
                        f"I'm thinking carefully about my {action_name} here. The {game_stage} is interesting.",
                        f"Let's see how this {game_stage} plays out. I'm {action_name}ing for now.",
                        f"I've made my decision to {action_name}. This {game_stage} requires careful play.",
                        f"In poker, timing is everything. I'll {action_name} and see what happens.",
                        f"The pot is {pot} now. My {action_name} reflects my confidence level."
                    ]
                    
                    # Use a random fallback response as a last resort
                    chat_message = random.choice(fallback_responses)
                    print(f"Warning: Using fallback response due to error: {inner_e}")
            
        except Exception as e:
            # Fallback if there's an error
            chat_message = f"I'm going to {action_name}. Let's see what happens next."
        
        # Store this message in the agent's memory
        self.message_history.append(chat_message)
        
        # Combine action and chat into a response
        response = {
            "action": str(action),
            "chat": chat_message
        }
        
        return json.dumps(response)
    
