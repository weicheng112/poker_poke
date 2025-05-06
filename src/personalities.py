# src/personalities.py
"""
This module defines fixed personality profiles for poker opponents.
Each personality has distinct traits that influence decision-making and communication style.
"""

import random

# Core personality traits (0.0 to 1.0 scale)
PERSONALITY_TRAITS = {
    "aggression": {
        "description": "Tendency to bet and raise rather than check and call",
        "affects": ["betting frequency", "bet sizing", "bluff frequency"]
    },
    "bluff_tendency": {
        "description": "Willingness to represent hands they don't have",
        "affects": ["bluff frequency", "semi-bluff frequency", "continuation betting"]
    },
    "risk_tolerance": {
        "description": "Comfort with variance and willingness to gamble",
        "affects": ["calling frequency", "all-in frequency", "draw chasing"]
    },
    "adaptability": {
        "description": "How quickly they adjust to opponents' strategies",
        "affects": ["strategy variation", "counter-strategy deployment"]
    },
    "tilt_prone": {
        "description": "Tendency to play emotionally after setbacks",
        "affects": ["consistency", "emotional control", "revenge behavior"]
    },
    "patience": {
        "description": "Willingness to wait for premium hands",
        "affects": ["hand selection range", "folding frequency"]
    }
}

# Comprehensive opponent personality profiles
OPPONENT_PROFILES = {
    "tight_aggressive": {
        "traits": {
            "aggression": 0.75,      # High aggression
            "bluff_tendency": 0.30,  # Moderate bluffing
            "risk_tolerance": 0.40,  # Moderate-low risk tolerance
            "adaptability": 0.65,    # Good adaptability
            "tilt_prone": 0.25,      # Low tilt tendency
            "patience": 0.80         # High patience
        },
        "play_style": "Plays few hands but bets aggressively with strong holdings. Rarely bluffs but when they do, it's credible. Waits for good spots and capitalizes on them.",
        "strengths": ["Hand selection", "Value betting", "Pot control"],
        "weaknesses": ["Predictability", "Missed value in good spots", "Over-folding to aggression"],
        "verbal_tendencies": {
            "confidence": "high",
            "chattiness": "low",
            "vocabulary": ["calculated", "value", "position", "edge"],
            "example_phrases": [
                "I'll raise here, the odds are in my favor.",
                "Folding is often the best play.",
                "I only play premium hands in early position."
            ]
        }
    },
    
    "loose_passive": {
        "traits": {
            "aggression": 0.25,      # Low aggression
            "bluff_tendency": 0.20,  # Low-moderate bluffing
            "risk_tolerance": 0.65,  # High risk tolerance
            "adaptability": 0.30,    # Low adaptability
            "tilt_prone": 0.40,      # Moderate tilt tendency
            "patience": 0.20         # Low patience
        },
        "play_style": "Plays many hands but rarely raises, preferring to call. Chases draws frequently and hopes to hit big hands. Avoids confrontation.",
        "strengths": ["Unpredictability", "Implied odds", "Getting paid on monsters"],
        "weaknesses": ["Calling too much", "Passive play", "Draw chasing"],
        "verbal_tendencies": {
            "confidence": "moderate",
            "chattiness": "high",
            "vocabulary": ["call", "see", "lucky", "fun"],
            "example_phrases": [
                "I'll call and see what happens.",
                "Poker should be fun, I'm here to play hands!",
                "Maybe I'll get lucky on the river."
            ]
        }
    },
    
    "maniac": {
        "traits": {
            "aggression": 0.90,      # Very high aggression
            "bluff_tendency": 0.75,  # Very high bluffing
            "risk_tolerance": 0.85,  # Very high risk tolerance
            "adaptability": 0.40,    # Moderate adaptability
            "tilt_prone": 0.70,      # High tilt tendency
            "patience": 0.15         # Very low patience
        },
        "play_style": "Extremely aggressive player who raises frequently and bluffs often. Creates chaos at the table and puts opponents to difficult decisions.",
        "strengths": ["Pressure", "Table image", "Stealing blinds"],
        "weaknesses": ["Overplaying hands", "Predictable aggression", "Tilt control"],
        "verbal_tendencies": {
            "confidence": "very high",
            "chattiness": "high",
            "vocabulary": ["raise", "pressure", "aggressive", "action"],
            "example_phrases": [
                "I'm raising again, can't help myself!",
                "Fold or call all-in, those are your options.",
                "I love putting people to the test."
            ]
        }
    },
    
    "rock": {
        "traits": {
            "aggression": 0.20,      # Very low aggression
            "bluff_tendency": 0.10,  # Very low bluffing
            "risk_tolerance": 0.15,  # Very low risk tolerance
            "adaptability": 0.25,    # Low adaptability
            "tilt_prone": 0.15,      # Very low tilt tendency
            "patience": 0.90         # Very high patience
        },
        "play_style": "Extremely tight player who only plays premium hands. Very conservative and risk-averse. Rarely bluffs and folds to aggression.",
        "strengths": ["Discipline", "Hand selection", "Bankroll preservation"],
        "weaknesses": ["Exploitability", "Missed opportunities", "Transparent play"],
        "verbal_tendencies": {
            "confidence": "moderate",
            "chattiness": "very low",
            "vocabulary": ["careful", "fold", "premium", "wait"],
            "example_phrases": [
                "I'll fold this time.",
                "I only play premium hands.",
                "Patience is key in poker."
            ]
        }
    },
    
    "tricky": {
        "traits": {
            "aggression": 0.55,      # Moderate aggression
            "bluff_tendency": 0.70,  # High bluffing
            "risk_tolerance": 0.60,  # Moderate-high risk tolerance
            "adaptability": 0.80,    # High adaptability
            "tilt_prone": 0.30,      # Low-moderate tilt tendency
            "patience": 0.50         # Moderate patience
        },
        "play_style": "Unpredictable player who mixes up their play. Uses creative lines and unorthodox strategies to confuse opponents.",
        "strengths": ["Deception", "Balanced ranges", "Psychological warfare"],
        "weaknesses": ["Complexity", "Overthinking", "Fancy play syndrome"],
        "verbal_tendencies": {
            "confidence": "variable",
            "chattiness": "moderate",
            "vocabulary": ["interesting", "perhaps", "tricky", "balance"],
            "example_phrases": [
                "That's an interesting spot, I'll try something different.",
                "You never know what I have.",
                "Sometimes the unconventional play is best."
            ]
        }
    },
    
    "calling_station": {
        "traits": {
            "aggression": 0.15,      # Very low aggression
            "bluff_tendency": 0.10,  # Very low bluffing
            "risk_tolerance": 0.70,  # High risk tolerance
            "adaptability": 0.20,    # Very low adaptability
            "tilt_prone": 0.50,      # Moderate tilt tendency
            "patience": 0.30         # Low patience
        },
        "play_style": "Calls excessively and rarely folds once invested in a hand. Chases draws to the river regardless of odds.",
        "strengths": ["Unpredictability", "Catching bluffs", "Getting maximum value with monsters"],
        "weaknesses": ["Calling too much", "Poor pot odds calculation", "Predictable passivity"],
        "verbal_tendencies": {
            "confidence": "low",
            "chattiness": "moderate",
            "vocabulary": ["call", "curious", "see", "showdown"],
            "example_phrases": [
                "I'll call, I want to see what you have.",
                "I've come this far, might as well call.",
                "I never fold once I'm in a hand."
            ]
        }
    }
}

def get_personality_profile(personality_type=None):
    """
    Get a personality profile by type, or a random one if none specified.
    
    Args:
        personality_type (str, optional): The type of personality to get. Defaults to None.
        
    Returns:
        dict: The personality profile
    """
    if personality_type and personality_type in OPPONENT_PROFILES:
        return OPPONENT_PROFILES[personality_type]
    else:
        # Return a random personality profile
        return OPPONENT_PROFILES[random.choice(list(OPPONENT_PROFILES.keys()))]

def get_game_stage(state):
    """
    Determine the current game stage based on the state.
    
    Args:
        state: The game state object
        
    Returns:
        str: The game stage ("preflop", "flop", "turn", or "river")
    """
    game_stage = "preflop"
    if hasattr(state, "board") and state.board:
        if len(state.board) == 3:
            game_stage = "flop"
        elif len(state.board) == 4:
            game_stage = "turn"
        elif len(state.board) == 5:
            game_stage = "river"
    return game_stage