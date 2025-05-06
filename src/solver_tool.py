import random
import pokers as pk


def random_valid_action(state):
    """Return a legal pokers action dict, e.g. {'type':'check'}."""
    legals = state.legal_actions
    enum_action = random.choice(legals)
    return pk.Action(enum_action)

def get_action(state, agent=None):
    """
    Get an action for the agent based on the current state.
    Incorporates basic strategy and agent personality.
    """
    print(f"DEBUG: Agent name: {agent.name if agent else 'None'}")

    if agent is None:
        return random_valid_action(state)
    
    # Get the agent's hole cards and evaluate hand strength
    hand_strength = evaluate_hand_strength(state, agent)
    
    # Get the agent's personality traits directly from the agent
    # The agent now has a personality attribute with all traits
    personality = agent.personality if hasattr(agent, 'personality') else get_agent_personality(agent)
    
    # Determine action based on hand strength and personality
    action = determine_action(state, hand_strength, personality)
    print(f"DEBUG: Action from get_action: {action}, amount: {action.amount if hasattr(action, 'amount') else 'No amount attribute'}")
    return action

def evaluate_hand_strength(state, agent):
    """
    Evaluate the strength of the agent's hand.
    Returns a value between 0 (very weak) and 1 (very strong).
    """
    # In a real implementation, this would use actual poker hand evaluation
    # For now, we'll use a simple random value as a placeholder
    # This simulates the agent's perception of their hand strength
    return random.random()

def get_agent_personality(agent):
    """
    Get the personality traits of the agent.
    Returns a dictionary of traits that influence decision making.
    
    Note: This function is kept for backward compatibility.
    New code should access agent.personality directly.
    """
    # Check if the agent already has a personality attribute
    if hasattr(agent, 'personality'):
        return agent.personality
    
    # For backward compatibility, generate a random personality
    # Use the agent's name to deterministically set personality traits
    random.seed(hash(agent.name))
    
    # Import the personality profiles if available
    try:
        from src.personalities import OPPONENT_PROFILES
        # Choose a random profile
        profile_name = random.choice(list(OPPONENT_PROFILES.keys()))
        return OPPONENT_PROFILES[profile_name]["traits"]
    except ImportError:
        # Fallback to the original implementation
        return {
            "aggression": random.uniform(0.3, 0.8),  # How aggressive the agent is
            "bluff_tendency": random.uniform(0.1, 0.5),  # How likely to bluff
            "risk_tolerance": random.uniform(0.2, 0.7),  # How much risk they'll take
        }

def determine_action(state, hand_strength, personality):
    """
    Determine the action based on hand strength and personality.
    This implementation uses the expanded personality traits to make more nuanced decisions.
    """
    from src.personalities import get_game_stage
    
    legals = state.legal_actions
    
    # Extract the action types from the legal actions
    legal_types = [str(pk.Action(action)).lower() for action in legals]
    
    # Get the current game stage
    game_stage = get_game_stage(state)
    
    # Adjust hand strength based on personality and game stage
    effective_strength = hand_strength
    
    # In preflop, be more aggressive to encourage longer games
    if game_stage == "preflop":
        # Adjust preflop aggression based on patience
        if "patience" in personality:
            # Patient players are more selective preflop
            patience_factor = personality["patience"]
            # If patient, only play strong hands; if impatient, play more hands
            min_strength = 0.6 - (0.3 * (1 - patience_factor))
            effective_strength = max(min_strength, hand_strength)
        else:
            # Default behavior if patience trait is not available
            effective_strength = max(0.6, hand_strength)
        
        # Reduce folding in preflop
        if "fold" in legal_types and len(legals) > 1:
            # Try to avoid folding in preflop by removing it from legal actions
            # unless it's the only option
            fold_indices = [i for i, action_str in enumerate(legal_types) if "fold" in action_str]
            if fold_indices and len(legals) > 1:
                for idx in fold_indices:
                    if len(legals) > 1:  # Make sure we always have at least one action
                        legals.pop(idx)
                        legal_types.pop(idx)
    
    # Adjust based on bluffing tendency
    if random.random() < personality["bluff_tendency"]:
        bluff_boost = 0.3
        # If adaptability is high, make bluffs more sophisticated
        if "adaptability" in personality and personality["adaptability"] > 0.6:
            # More adaptable players bluff in more believable ways
            bluff_boost = 0.2 + (0.2 * personality["adaptability"])
        effective_strength = min(1.0, effective_strength + bluff_boost)
    
    # Adjust for tilt if the trait exists
    if "tilt_prone" in personality and random.random() < personality["tilt_prone"] * 0.5:
        # Tilted players make more erratic decisions
        tilt_adjustment = (random.random() - 0.5) * personality["tilt_prone"]
        effective_strength += tilt_adjustment
        # Ensure effective_strength stays in valid range
        effective_strength = max(0.0, min(1.0, effective_strength))
    
    # Choose a random action with preference for more interesting actions
    weights = []
    for action_str in legal_types:
        if "raise" in action_str or "bet" in action_str:
            # Prefer raising/betting based on aggression
            weight = 3.0 * (1.0 + personality["aggression"])
            weights.append(weight)
        elif "call" in action_str:
            # Next prefer calling, influenced by risk tolerance
            weight = 2.0 * (1.0 + personality.get("risk_tolerance", 0.5))
            weights.append(weight)
        elif "check" in action_str:
            # Then checking, preferred by patient players
            weight = 1.5 * (1.0 + personality.get("patience", 0.5))
            weights.append(weight)
        else:
            # Folding least preferred, but more likely for risk-averse players
            weight = 1.0 * (2.0 - personality.get("risk_tolerance", 0.5))
            weights.append(weight)
    
    # Adjust weights based on effective strength
    for i, action_str in enumerate(legal_types):
        if effective_strength > 0.7:
            # Strong hand: prefer aggressive actions
            if "raise" in action_str or "bet" in action_str:
                weights[i] *= 2.0 * (1.0 + personality["aggression"] * 0.5)
        elif effective_strength < 0.3:
            # Weak hand: prefer passive actions
            if "check" in action_str or "fold" in action_str:
                weights[i] *= 1.5 * (2.0 - personality.get("risk_tolerance", 0.5) * 0.5)
    
    # Choose an action based on weights
    if weights:
        
        chosen_idx = random.choices(range(len(legals)), weights=weights, k=1)[0]
        chosen_action = legals[chosen_idx]
        
        print(f"DEBUG: chosen_action: {chosen_action}, chosen_action name: {chosen_action.name if hasattr(chosen_action, 'name') else str(chosen_action)}")
        
        # Check if the action is a raise based on the enum value
        if chosen_action == pk.ActionEnum.Raise:
            print(f"DEBUG: Action is a raise")
            # Determine the amount based on hand strength and personality
            # The more aggressive the player and the stronger the hand, the higher the amount
            base_amount = 10  # Base amount for raise or bet
            
            # Adjust based on hand strength and aggression
            strength_factor = 1.0 + (effective_strength * 2.0)  # 1.0 to 3.0
            aggression_factor = 1.0 + (personality["aggression"] * 1.5)  # 1.0 to 2.5
            
            # Additional factors based on extended personality traits
            risk_factor = 1.0
            if "risk_tolerance" in personality:
                # Risk-tolerant players make bigger bets
                risk_factor = 0.8 + (personality["risk_tolerance"] * 0.4)  # 0.8 to 1.2
            
            tilt_factor = 1.0
            if "tilt_prone" in personality and random.random() < personality["tilt_prone"] * 0.3:
                # Tilted players occasionally make unusually large or small bets
                tilt_factor = 0.7 + (random.random() * 0.6)  # 0.7 to 1.3
            
            # Calculate the amount with all factors
            amount = base_amount * strength_factor * aggression_factor * risk_factor * tilt_factor
            
            # Round to nearest 5
            amount = round(amount / 5) * 5
            
            # Ensure minimum amount is 5
            amount = max(5, amount)
            
            # Create the action with the amount
            print(f"DEBUG: Creating action with amount: {amount}")
            action = pk.Action(chosen_action, amount)
            print(f"DEBUG: Created action: {action}, amount: {action.amount if hasattr(action, 'amount') else 'No amount attribute'}")
            return action
        else:
            # For other actions, no amount is needed
            return pk.Action(chosen_action)
    
    # Fallback to random action
    return random_valid_action(state)
    
    
