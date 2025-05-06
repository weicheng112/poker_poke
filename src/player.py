# src/player.py

from autogen import AssistantAgent
from dotenv import load_dotenv
import pokers as pk
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
        • personality   – fixed personality traits that influence decision making
    """

    def __init__(self, name: str, personality_type=None):
        """
        Initialize a PlayerAgent with a specific or random personality.
        
        Args:
            name (str): The name of the agent (e.g., "P0", "P1")
            personality_type (str, optional): The type of personality to use.
                                             If None, a random one will be selected.
                                             Options: "tight_aggressive", "loose_passive",
                                             "maniac", "rock", "tricky", "calling_station"
        """
        # Import the personality profiles
        from src.personalities import get_personality_profile, OPPONENT_PROFILES
        
        # Set up a seed based on the name to ensure consistent personality
        import random
        random.seed(hash(name))
        
        # Get a personality profile (either specified or random)
        if personality_type and personality_type in OPPONENT_PROFILES:
            profile = OPPONENT_PROFILES[personality_type]
            self.personality_type = personality_type
        else:
            # If no valid personality type is provided, choose a random one
            self.personality_type = random.choice(list(OPPONENT_PROFILES.keys()))
            profile = OPPONENT_PROFILES[self.personality_type]
        
        # Store the personality traits
        self.personality = profile["traits"].copy()
        
        # Get the play style description
        play_style = profile["play_style"]
        
        # Create a comprehensive system message
        system_message = f"""
You are a poker player named {name} with a {self.personality_type} playing style.

Your personality traits:
- Aggression: {self.personality["aggression"]:.2f} (0-1 scale)
- Bluff tendency: {self.personality["bluff_tendency"]:.2f} (0-1 scale)
- Risk tolerance: {self.personality["risk_tolerance"]:.2f} (0-1 scale)
- Adaptability: {self.personality["adaptability"]:.2f} (0-1 scale)
- Tilt proneness: {self.personality["tilt_prone"]:.2f} (0-1 scale)
- Patience: {self.personality["patience"]:.2f} (0-1 scale)

Play style: {play_style}

Core principles:
1. NEVER reveal your exact hole cards to opponents
2. Your betting decisions are determined by an external GTO solver
3. Your role is to communicate naturally with other players
4. Respond to messages in a way that reflects your personality
5. Comment on the game state and actions in an engaging way

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
        
        # Store verbal tendencies for communication
        self.verbal_tendencies = profile["verbal_tendencies"]


    def generate_reply(self, messages, sender, config):
        """
        Use the LLM to generate a natural response based on the game state and previous messages.
        This method leverages the system prompt and the LLM's capabilities for more natural agent communication.
        """
        import json
        import random
        from src.solver_tool import get_action, evaluate_hand_strength
        from src.personalities import get_game_stage
        
        # Get the current state from the blackboard
        state = self.blackboard.get("state")
        if not state:
            return "No state available in blackboard"
        
        # Get the action - either from the config parameter or from the solver
        if config and "action" in config:
            # Use the action passed from the engine
            action = config["action"]
            # print("DEBUG: Using action from engine")
        else:
            # Fallback to getting the action from the solver
            action = get_action(state, self)
            # print("DEBUG: Using action from solver (fallback)")
        
        # Extract game information for context
        game_stage = get_game_stage(state)
        
        # Get pot size
        pot = getattr(state, "pot", 0)
        
        # Get board information
        board_info = ""
        if hasattr(state, "board") and state.board:
            board_info = f"Board: {state.board}"
        
        # Get hand strength
        hand_strength = evaluate_hand_strength(state, self)
        
        # Since we can't reliably extract the action name from the action object,
        # let's use a simpler approach: just use the action name from the game trace
        
        # Print the raw action for debugging
        # print(f"DEBUG: Raw action: {action}")
        
        # For now, let's use a fixed mapping based on the player and game stage
        # This is a temporary solution until we can find a better way to extract the action name
        
        # Get the current player and game stage
        current_player = state.current_player
        
        # Determine action based on the game trace in engine_autogen.py
        # Looking at the game trace, we can see that:
        # - Player 1 (P1) folds in preflop
        # - Player 0 (P0) calls in preflop
        # - Player 1 (P1) checks in flop, turn, river
        # - Player 0 (P0) raises in flop, turn, river
        
        # Looking at the game trace and chat history, we need to adjust our action names
        # to match what's actually happening in the game
        
        # The game trace shows:
        # - Player 1 (P1) raises in preflop but the chat shows fold
        # - Player 0 (P0) raises in preflop but the chat shows call
        # - Both players raise in post-flop rounds but the pot doesn't increase
        
        # Let's try to extract the action name and amount directly from the action object
        # This is more reliable than using a fixed mapping
        
        # Get the action string representation
        action_str = str(action)
        # print(f"DEBUG: Action string: {action_str}")
        
        # Try to extract the amount from the action object
        action_amount = 0
        if hasattr(action, "amount"):
            action_amount = action.amount
        # print(f"DEBUG: Action amount: {action_amount}")
        
        # Extract the action name based on the game trace
        # The game trace shows the actual actions being taken
        
        action_name = action.action
        
        # print(f"DEBUG: Extracted action name: {action_name}")
        
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
        
        # Create a system message override that explicitly includes the action
        action_system_message = f"""
You are a poker player named {self.name} with a {self.personality_type} playing style.

CRITICAL INSTRUCTION: Your action this round is: {str(action_name).split('.')[-1].upper()}
You MUST use this EXACT action word in your response.

Your personality traits:
- Aggression: {self.personality["aggression"]:.2f} (0-1 scale)
- Bluff tendency: {self.personality["bluff_tendency"]:.2f} (0-1 scale)
- Risk tolerance: {self.personality["risk_tolerance"]:.2f} (0-1 scale)
- Adaptability: {self.personality["adaptability"]:.2f} (0-1 scale)
- Tilt proneness: {self.personality["tilt_prone"]:.2f} (0-1 scale)
- Patience: {self.personality["patience"]:.2f} (0-1 scale)

Core principles:
1. NEVER reveal your exact hole cards to opponents
2. Your betting decisions are determined by an external GTO solver
3. Your role is to communicate naturally with other players
4. Respond to messages in a way that reflects your personality
5. Comment on the game state and actions in an engaging way
6. BE TRUTHFUL about your action - you are {str(action_name).split('.')[-1].upper()}ING, not any other action

As a {self.personality_type} player, speak in character while explicitly stating your {str(action_name).split('.')[-1]} action.

Your verbal tendencies:
- Confidence level: {self.verbal_tendencies["confidence"]}
- Chattiness: {self.verbal_tendencies["chattiness"]}
- Key vocabulary: {', '.join(self.verbal_tendencies["vocabulary"])}
"""

        # Create a context message for the LLM
        # Include the action amount for raise or bet actions
        action_description = str(action_name).split('.')[-1].upper()
        if str(action_name).split('.')[-1].lower() in ["raise", "bet"] and action_amount > 0:
            action_description = f"{str(action_name).split('.')[-1].upper()} {action_amount}"
        
        # Choose a random example phrase
        example_phrase = random.choice(self.verbal_tendencies['example_phrases'])
        
        context_message = {
            "role": "user",
            "content": f"""
Current game state:
- Stage: {game_stage}
- Pot: {pot}
- {board_info}
- YOUR ACTION: {action_description} (This is your actual action, you must use this exact word)
- Your hand strength: {"strong" if hand_strength > 0.7 else "medium" if hand_strength > 0.4 else "weak"}

Recent table messages:
{previous_messages[-3:] if previous_messages else "No previous messages"}

CRITICAL INSTRUCTION: Generate a short poker table chat message (1-2 sentences) that MUST:
1. Include the EXACT word "{str(action_name).split('.')[-1]}" (not "play" or any other substitute)
2. Reflect your {self.personality_type} personality
3. Be appropriate for the current game state
4. NEVER reveal your exact cards
5. Use at least one of your characteristic vocabulary words: {', '.join(self.verbal_tendencies["vocabulary"])}

Your response MUST contain one of these phrases:
- "I {str(action_name).split('.')[-1]}"
- "I'll {str(action_name).split('.')[-1]}"
- "I'm going to {str(action_name).split('.')[-1]}"
- "I will {str(action_name).split('.')[-1]}"
- "{str(action_name).split('.')[-1]}ing"

DO NOT use the word "play" as a substitute for "{str(action_name).split('.')[-1]}".

For inspiration, consider this example phrase in your style:
"{example_phrase}"
"""
        }
        
        # Use the LLM to generate a response
        try:
            # Simplified approach: use the agent's own methods to generate a response
            # This is more reliable than trying to access internal capabilities
            
            # Create a prompt that includes all the context
            # Include the action amount for raise or bet actions
            action_description = str(action_name).split('.')[-1]
            if str(action_name).split('.')[-1].lower() in ["raise", "bet"] and action_amount > 0:
                action_description = f"{str(action_name).split('.')[-1]} {action_amount}"
            
            prompt = f"""
    As a poker player named {self.name} with a {self.personality_type} playing style:
    
    Current game state:
    - Stage: {game_stage}
    - Pot: {pot}
    - {board_info}
    - Your action: {action_description}
    - Your hand strength: {"strong" if hand_strength > 0.7 else "medium" if hand_strength > 0.4 else "weak"}
    
    Recent table messages:
    {previous_messages[-3:] if previous_messages else "No previous messages"}
    
    Generate a short, natural poker table chat message (1-2 sentences) that:
    1. Reflects your {self.personality_type} personality
    2. Mentions your {action_description} action
    3. Uses your characteristic vocabulary: {', '.join(self.verbal_tendencies["vocabulary"])}
    4. NEVER reveals your exact cards
    
    For inspiration, consider this example phrase in your style:
    "{random.choice(self.verbal_tendencies["example_phrases"])}"
    """
            
            # Use a direct approach to generate a response
            import openai
            
            try:
                # Try using the OpenAI API directly
                client = openai.OpenAI()
                
                # Use the action-specific system message we created
                response = client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": action_system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,  # Slightly lower temperature for more consistent responses
                    max_tokens=100
                )
                chat_message = response.choices[0].message.content
                print(f"Generated response using OpenAI API: {chat_message}")
                
            except Exception as api_error:
                print(f"OpenAI API error: {api_error}")
                
                # Fallback to predefined responses
                import random
                
                # Create some varied responses based on the game state and action
                # Create personality-specific fallback responses using verbal tendencies
                fallback_responses = []
                
                # Add responses based on personality type
                if self.personality_type == "tight_aggressive":
                    fallback_responses.extend([
                        f"I'll {str(action_name).split('.')[-1]} here - this is a calculated move.",
                        f"The value in this spot is clear. I {str(action_name).split('.')[-1]}.",
                        f"Position is key in this hand. I {str(action_name).split('.')[-1]}."
                    ])
                elif self.personality_type == "loose_passive":
                    fallback_responses.extend([
                        f"I'll {str(action_name).split('.')[-1]} and see what happens. Poker should be fun!",
                        f"Maybe I'll get lucky. I {str(action_name).split('.')[-1]}.",
                        f"I'm just here to call and enjoy the game. {str(action_name).split('.')[-1].capitalize()}ing now."
                    ])
                elif self.personality_type == "maniac":
                    fallback_responses.extend([
                        f"I'm raising- oh wait, I mean I {str(action_name).split('.')[-1]}! I love the pressure!",
                        f"More aggressive action! I {str(action_name).split('.')[-1]}!",
                        f"Time for some action! I'm {str(action_name).split('.')[-1]}ing!"
                    ])
                elif self.personality_type == "rock":
                    fallback_responses.extend([
                        f"I'll carefully {str(action_name).split('.')[-1]} here.",
                        f"The premium hands are worth waiting for. I {str(action_name).split('.')[-1]}.",
                        f"I'll {str(action_name).split('.')[-1]}. Patience is key in poker."
                    ])
                elif self.personality_type == "tricky":
                    fallback_responses.extend([
                        f"This is an interesting spot. I'll {str(action_name).split('.')[-1]}.",
                        f"Perhaps my {str(action_name).split('.')[-1]} will surprise you.",
                        f"I'm {str(action_name).split('.')[-1]}ing. Balance is important in this situation."
                    ])
                elif self.personality_type == "calling_station":
                    fallback_responses.extend([
                        f"I'm curious to see what happens. I {str(action_name).split('.')[-1]}.",
                        f"I'll {str(action_name).split('.')[-1]} and see what you have.",
                        f"I've come this far, so I'll {str(action_name).split('.')[-1]}."
                    ])
                else:
                    # Generic fallbacks if personality type isn't recognized
                    fallback_responses.extend([
                        f"I'm thinking about my {str(action_name).split('.')[-1]} here. The {game_stage} is interesting.",
                        f"Let's see how this {game_stage} plays out. I'm {str(action_name).split('.')[-1]}ing for now.",
                        f"I've made my decision to {str(action_name).split('.')[-1]}. This {game_stage} requires careful play."
                    ])
                
                chat_message = random.choice(fallback_responses)
                print(f"Using fallback response: {chat_message}")
                
        except Exception as e:
            # Final fallback if there's an error
            chat_message = f"I'm going to {str(action_name).split('.')[-1]}. Let's see what happens next."
            print(f"Error in generate_reply: {e}")
        
        # Post-process the response to ensure it mentions the actual action
        # This is a last resort to make sure the chat message matches the action
        # print(f"DEBUG: Action name: {str(action_name).split('.')[-1]}, Message: {chat_message}")
        # print(f"DEBUG: Action name in message: {str(action_name).split('.')[-1].lower() in chat_message.lower()}")
        
        if str(action_name).split('.')[-1].lower() not in chat_message.lower():
            print(f"DEBUG: Action name not in message, applying post-processing")
            # If the action name is not in the message, add it explicitly
            if "PLAY" in chat_message:
                # Replace "PLAY" with the actual action
                # print(f"DEBUG: Replacing PLAY with {str(action_name).split('.')[-1].upper()}")
                chat_message = chat_message.replace("PLAY", str(action_name).split('.')[-1].upper())
            elif "play" in chat_message.lower():
                # Replace "play" with the actual action
                # print(f"DEBUG: Replacing play with {str(action_name).split('.')[-1].lower()}")
                chat_message = chat_message.lower().replace("play", str(action_name).split('.')[-1].lower())
                # Restore the first letter capitalization if it was capitalized
                if chat_message[0].islower() and len(chat_message) > 0:
                    chat_message = chat_message[0].upper() + chat_message[1:]
            else:
                # If we can't replace "play", add the action at the beginning
                # print(f"DEBUG: Adding action at the beginning")
                chat_message = f"I'll {str(action_name).split('.')[-1]} here. " + chat_message
            
            # print(f"DEBUG: Post-processed message: {chat_message}")
        
        # Store this message in the agent's memory
        self.message_history.append(chat_message)
        
        # Combine action and chat into a response
        response = {
            "action": str(action),
            "chat": chat_message
        }
        
        return json.dumps(response)
    
