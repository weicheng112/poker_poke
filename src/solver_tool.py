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
    if agent is None:
        return random_valid_action(state)
    
    # Get the agent's hole cards and evaluate hand strength
    hand_strength = evaluate_hand_strength(state, agent)
    
    # Get the agent's personality traits
    personality = get_agent_personality(agent)
    
    # Determine action based on hand strength and personality
    return determine_action(state, hand_strength, personality)

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
    """
    # Use the agent's name to deterministically set personality traits
    # This ensures consistent behavior across hands
    random.seed(hash(agent.name))
    
    return {
        "aggression": random.uniform(0.3, 0.8),  # How aggressive the agent is
        "bluff_tendency": random.uniform(0.1, 0.5),  # How likely to bluff
        "risk_tolerance": random.uniform(0.2, 0.7),  # How much risk they'll take
    }

def determine_action(state, hand_strength, personality):
    """
    Determine the action based on hand strength and personality.
    This implementation encourages more interesting gameplay by reducing early folds.
    """
    legals = state.legal_actions
    
    # Extract the action types from the legal actions
    legal_types = [str(pk.Action(action)).lower() for action in legals]
    
    # Get the current game stage
    game_stage = "preflop"
    if hasattr(state, "board") and state.board:
        if len(state.board) == 3:
            game_stage = "flop"
        elif len(state.board) == 4:
            game_stage = "turn"
        elif len(state.board) == 5:
            game_stage = "river"
    
    # Adjust hand strength based on personality and game stage
    effective_strength = hand_strength
    
    # In preflop, be more aggressive to encourage longer games
    if game_stage == "preflop":
        effective_strength = max(0.4, hand_strength)  # Minimum 0.4 strength in preflop
        
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
        effective_strength = min(1.0, effective_strength + 0.3)
    
    # Choose a random action with preference for more interesting actions
    weights = []
    for action_str in legal_types:
        if "raise" in action_str or "bet" in action_str:
            # Prefer raising/betting
            weights.append(3.0)
        elif "call" in action_str:
            # Next prefer calling
            weights.append(2.0)
        elif "check" in action_str:
            # Then checking
            weights.append(1.5)
        else:
            # Folding least preferred
            weights.append(1.0)
    
    # Adjust weights based on effective strength
    for i, action_str in enumerate(legal_types):
        if effective_strength > 0.7:
            # Strong hand: prefer aggressive actions
            if "raise" in action_str or "bet" in action_str:
                weights[i] *= 2.0
        elif effective_strength < 0.3:
            # Weak hand: prefer passive actions
            if "check" in action_str or "fold" in action_str:
                weights[i] *= 1.5
    
    # Choose an action based on weights
    if weights:
        chosen_idx = random.choices(range(len(legals)), weights=weights, k=1)[0]
        return pk.Action(legals[chosen_idx])
    
    # Fallback to random action
    return random_valid_action(state)
    
    
