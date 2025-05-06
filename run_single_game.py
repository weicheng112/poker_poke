"""
Run a single poker game and save the data without personality information.
This script is used to test the game data extraction functionality.
"""

import os
import json
import random
from src.engine_autogen import play_hand
from src.game_data_extractor import GameDataExtractor

def run_single_game(seed=12345, output_dir="data/test_game"):
    """
    Run a single poker game and save the data without personality information.
    
    Args:
        seed (int): Random seed for the game
        output_dir (str): Directory to save the output
        
    Returns:
        str: Path to the saved file
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\n\n{'='*80}")
    print(f"Running poker game with seed: {seed}")
    print(f"{'='*80}\n")
    
    # Set the random seed
    random.seed(seed)
    
    # Play a hand
    game_result = play_hand(seed=seed)
    
    # Print debug information about the game trace
    print("\nDEBUG: Game Trace Information")
    trace = game_result["trace"]
    print(f"Number of states in trace: {len(trace)}")
    
    for i, state in enumerate(trace):
        print(f"\nState {i}:")
        print(f"  Current player: {getattr(state, 'current_player', 'N/A')}")
        print(f"  Stage: {getattr(state, 'stage', 'N/A')}")
        print(f"  Pot: {getattr(state, 'pot', 'N/A')}")
        print(f"  Final state: {getattr(state, 'final_state', 'N/A')}")
        
        # Check for from_action
        if hasattr(state, "from_action") and state.from_action:
            print(f"  From action: {state.from_action.action.action}")
            print(f"  Action player: {state.from_action.player}")
            print(f"  Action amount: {getattr(state.from_action.action, 'amount', 0)}")
        else:
            print("  No from_action")
        
        # Check for players_state
        if hasattr(state, "players_state"):
            print("  Players state:")
            for j, ps in enumerate(state.players_state):
                print(f"    Player {j}: active={ps.active}, bet={ps.bet_chips}, stake={ps.stake}")
    
    # Extract and save the data
    extractor = GameDataExtractor(output_dir=output_dir)
    game_doc = extractor.extract_from_game(game_result)
    
    # Remove personality information from the game document
    modified_doc = remove_personality_info(game_doc)
    
    # Save to a JSON file with a descriptive name
    filename = f"game_seed_{seed}.json"
    filepath = extractor.save_to_json(modified_doc, filename=filename)
    
    # Print the game document structure
    print("\nGame Document Structure (without personality information):")
    print_document_structure(modified_doc)
    
    return filepath

def remove_personality_info(game_doc):
    """
    Remove personality information from the game document.
    
    Args:
        game_doc (dict): Game document
        
    Returns:
        dict: Modified game document without personality information
    """
    # Create a deep copy of the game document
    import copy
    modified_doc = copy.deepcopy(game_doc)
    
    # Remove personality information from players
    if "players" in modified_doc:
        for player_id, player_info in modified_doc["players"].items():
            if "personality_type" in player_info:
                del player_info["personality_type"]
            if "personality_traits" in player_info:
                del player_info["personality_traits"]
    
    # Remove personality information from text descriptions
    for action in modified_doc.get("actions", []):
        if "text_description" in action:
            # Remove any mention of personality from text descriptions
            action["text_description"] = remove_personality_mentions(action["text_description"])
    
    for chat in modified_doc.get("chat_messages", []):
        if "text_description" in chat:
            # Remove any mention of personality from text descriptions
            chat["text_description"] = remove_personality_mentions(chat["text_description"])
    
    return modified_doc

def remove_personality_mentions(text):
    """
    Remove mentions of personality types from text.
    
    Args:
        text (str): Text to process
        
    Returns:
        str: Text without personality mentions
    """
    personality_types = [
        "tight_aggressive", "loose_passive", "maniac", 
        "rock", "tricky", "calling_station",
        "aggressive", "bluffer", "conservative"
    ]
    
    for p_type in personality_types:
        text = text.replace(f"({p_type})", "")
        text = text.replace(p_type, "")
    
    return text

def print_document_structure(game_doc, indent=0):
    """
    Print the structure of the game document.
    
    Args:
        game_doc (dict): Game document
        indent (int): Indentation level
    """
    indent_str = "  " * indent
    
    if isinstance(game_doc, dict):
        for key, value in game_doc.items():
            if isinstance(value, (dict, list)) and value:
                print(f"{indent_str}{key}:")
                print_document_structure(value, indent + 1)
            else:
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"{indent_str}{key}: {value}")
    elif isinstance(game_doc, list):
        if game_doc:
            print(f"{indent_str}[{len(game_doc)} items]")
            # Print the first item as an example
            if game_doc:
                print_document_structure(game_doc[0], indent + 1)
                if len(game_doc) > 1:
                    print(f"{indent_str}... ({len(game_doc)-1} more items)")
        else:
            print(f"{indent_str}[]")
    else:
        print(f"{indent_str}{game_doc}")

def main():
    """
    Run a single game and check the output.
    """
    # Run a game
    filepath = run_single_game(
        seed=12345,
        output_dir="data/test_game"
    )
    
    print(f"\nGame data saved to: {filepath}")
    print("\nNext steps:")
    print("1. Examine the JSON file to ensure it's structured correctly")
    print("2. Implement the RAG system to predict player personalities based on actions and chat")
    print("3. Test the RAG system's ability to identify player personalities without prior knowledge")

if __name__ == "__main__":
    main()