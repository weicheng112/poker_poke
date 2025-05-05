import pokers as pk
from src.engine import play_hand
import random
import time

def play_with_seed(seed):
    """Play a hand with a specific seed"""
    # Set the random seed for this hand
    random.seed(seed)
    
    print(f"\n\n{'='*80}")
    print(f"Running poker game with seed: {seed}")
    print(f"{'='*80}\n")
    
    # Run the poker hand
    result = play_hand(seed=seed)
    
    # Display chat history
    print("\n=== AGENT CHAT HISTORY ===")
    for chat in result["chat_history"]:
        print(chat)
    
    # Display game trace
    print("\n=== GAME TRACE ===")
    trace_viz = pk.visualize_trace(result["trace"])
    print(trace_viz)
    
    return result

def main():
    print("Running multiple poker games with AutoGen agents...\n")
    
    # Run 3 different hands with different seeds
    seeds = [1234, 5678, 9012]
    
    for seed in seeds:
        play_with_seed(seed)
        # Small delay between hands for readability
        time.sleep(1)
    
    print("\nAll poker games completed successfully!")

if __name__ == "__main__":
    main()