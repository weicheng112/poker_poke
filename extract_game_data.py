"""
Extract Game Data Script

This script plays multiple poker games with different player personalities,
extracts the game data, and saves it to JSON files for later use in a RAG system.
"""

import os
import time
import random
from src.game_data_extractor import extract_and_save_game
from src.engine_autogen import play_hand
from src.player import PlayerAgent

def main():
    """
    Play multiple games with different personality combinations and extract the data.
    """
    # Create output directory if it doesn't exist
    output_dir = "data/game_records"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Extracting game data to {output_dir}...")
    
    # Define personality combinations to test
    personality_combinations = [
        # Default combination (tight_aggressive vs loose_passive)
        ("tight_aggressive", "loose_passive"),
        
        # Aggressive vs Conservative
        ("maniac", "rock"),
        
        # Tricky vs Calling Station
        ("tricky", "calling_station"),
        
        # Similar styles
        ("tight_aggressive", "tight_aggressive"),
        
        # Random combinations
        (random.choice(["tight_aggressive", "loose_passive", "maniac", "rock", "tricky", "calling_station"]),
         random.choice(["tight_aggressive", "loose_passive", "maniac", "rock", "tricky", "calling_station"]))
    ]
    
    # Play games with each personality combination
    for i, (p0_type, p1_type) in enumerate(personality_combinations):
        print(f"\n\n{'='*80}")
        print(f"Game {i+1}: {p0_type} vs {p1_type}")
        print(f"{'='*80}\n")
        
        # Use a different seed for each game
        seed = 1000 + i
        
        # Extract and save the game data
        filepath = extract_and_save_game(seed=seed, output_dir=output_dir)
        
        print(f"Game {i+1} data saved to {filepath}")
        
        # Small delay between games for readability
        time.sleep(1)
    
    print("\nAll game data extracted and saved successfully!")
    print(f"Data files are located in: {os.path.abspath(output_dir)}")
    print("\nYou can now use this data to build your RAG system for player personality analysis.")

if __name__ == "__main__":
    main()