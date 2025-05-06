"""
Generate a large dataset of poker game history records.
This script runs multiple poker games with different seeds and saves the data.
"""

import os
import json
import random
import time
import argparse
from tqdm.auto import tqdm
from src.engine_autogen import play_hand
from src.game_data_extractor import GameDataExtractor

def generate_game_history(start_seed=1000, end_seed=1999, output_dir="data/game_history"):
    """
    Generate multiple poker game history records with seeds in the specified range.
    
    Args:
        start_seed (int): Starting seed value
        end_seed (int): Ending seed value (inclusive)
        output_dir (str): Directory to save the output files
        
    Returns:
        list: Paths to the saved files
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"\n{'='*80}")
    print(f"Generating {end_seed - start_seed + 1} poker game history records")
    print(f"Seeds: {start_seed} to {end_seed}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")
    
    # Initialize the extractor
    extractor = GameDataExtractor(output_dir=output_dir)
    
    # Track successful and failed games
    successful_games = []
    failed_games = []
    
    # Use tqdm for progress bar
    for seed in tqdm(range(start_seed, end_seed + 1), desc="Generating games"):
        try:
            # Set the random seed
            random.seed(seed)
            
            # Play a hand
            game_result = play_hand(seed=seed)
            
            # Extract game data
            game_doc = extractor.extract_from_game(game_result)
            
            # Remove personality information from the game document
            modified_doc = remove_personality_info(game_doc)
            
            # Save to a JSON file with a descriptive name
            filename = f"game_seed_{seed}.json"
            filepath = extractor.save_to_json(modified_doc, filename=filename)
            
            # Add to successful games
            successful_games.append(filepath)
            
        except Exception as e:
            print(f"\nError generating game with seed {seed}: {str(e)}")
            failed_games.append(seed)
            
        # Small delay to prevent system overload
        time.sleep(0.1)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Generation complete!")
    print(f"Successfully generated: {len(successful_games)} games")
    if failed_games:
        print(f"Failed to generate: {len(failed_games)} games")
        print(f"Failed seeds: {failed_games}")
    print(f"{'='*80}\n")
    
    return successful_games

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

def analyze_generated_data(data_dir="data/game_history"):
    """
    Analyze the generated data to provide statistics.
    
    Args:
        data_dir (str): Directory containing the generated data
        
    Returns:
        dict: Statistics about the generated data
    """
    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return {}
    
    # Initialize statistics
    stats = {
        "total_games": len(json_files),
        "action_counts": {},
        "chat_sentiment_counts": {},
        "game_stages_reached": {
            "preflop": 0,
            "flop": 0,
            "turn": 0,
            "river": 0
        },
        "showdown_reached": 0,
        "player_win_counts": {}
    }
    
    # Process each file
    for filename in tqdm(json_files, desc="Analyzing data"):
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                game_data = json.load(f)
            
            # Count actions
            for action in game_data.get("actions", []):
                action_type = action.get("action", "unknown")
                if action_type not in stats["action_counts"]:
                    stats["action_counts"][action_type] = 0
                stats["action_counts"][action_type] += 1
            
            # Count chat sentiments
            for chat in game_data.get("chat_messages", []):
                sentiment = chat.get("sentiment", "unknown")
                if sentiment not in stats["chat_sentiment_counts"]:
                    stats["chat_sentiment_counts"][sentiment] = 0
                stats["chat_sentiment_counts"][sentiment] += 1
            
            # Check game stages reached
            board_cards = game_data.get("hand_summary", {}).get("final_board", "")
            if board_cards:
                cards = board_cards.split()
                if len(cards) >= 3:
                    stats["game_stages_reached"]["flop"] += 1
                if len(cards) >= 4:
                    stats["game_stages_reached"]["turn"] += 1
                if len(cards) >= 5:
                    stats["game_stages_reached"]["river"] += 1
            else:
                stats["game_stages_reached"]["preflop"] += 1
            
            # Check if showdown was reached
            if game_data.get("hand_summary", {}).get("showdown_reached", False):
                stats["showdown_reached"] += 1
            
            # Count player wins
            winner = game_data.get("hand_summary", {}).get("winner", "unknown")
            if winner not in stats["player_win_counts"]:
                stats["player_win_counts"][winner] = 0
            stats["player_win_counts"][winner] += 1
            
        except Exception as e:
            print(f"Error analyzing {filename}: {str(e)}")
    
    return stats

def main():
    """
    Generate game history and analyze the data.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate poker game history records.')
    parser.add_argument('--start-seed', type=int, default=1000, help='Starting seed value (default: 1000)')
    parser.add_argument('--end-seed', type=int, default=1999, help='Ending seed value (default: 1999)')
    parser.add_argument('--output-dir', type=str, default='data/game_history', help='Output directory (default: data/game_history)')
    parser.add_argument('--skip-analysis', action='store_true', help='Skip data analysis after generation')
    args = parser.parse_args()
    
    # Generate the game history
    generated_files = generate_game_history(
        start_seed=args.start_seed,
        end_seed=args.end_seed,
        output_dir=args.output_dir
    )
    
    print(f"Generated {len(generated_files)} game history files in {args.output_dir}")
    
    # Analyze the generated data if not skipped
    if not args.skip_analysis:
        print("\nAnalyzing generated data...")
        stats = analyze_generated_data(args.output_dir)
        
        # Print statistics
        print("\nGenerated Data Statistics:")
        print(f"Total games: {stats.get('total_games', 0)}")
        
        print("\nAction counts:")
        for action, count in stats.get("action_counts", {}).items():
            print(f"  {action}: {count}")
        
        print("\nChat sentiment counts:")
        for sentiment, count in stats.get("chat_sentiment_counts", {}).items():
            print(f"  {sentiment}: {count}")
        
        print("\nGame stages reached:")
        for stage, count in stats.get("game_stages_reached", {}).items():
            print(f"  {stage}: {count}")
        
        print(f"\nShowdown reached: {stats.get('showdown_reached', 0)}")
        
        print("\nPlayer win counts:")
        for player, count in stats.get("player_win_counts", {}).items():
            print(f"  {player}: {count}")
    else:
        print("\nSkipping data analysis as requested.")
    


if __name__ == "__main__":
    # Check if tqdm is installed
    try:
        from tqdm.auto import tqdm
    except ImportError:
        print("The tqdm package is required for progress bars.")
        print("Please install it using: pip install tqdm")
        exit(1)
    
    main()