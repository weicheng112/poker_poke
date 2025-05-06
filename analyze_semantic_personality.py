import os
import sys
from dotenv import load_dotenv
from src.semantic_personality_analyzer import SemanticPokerPersonalityAnalyzer

# Load environment variables from .env file
load_dotenv()

def main():
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please add it to your .env file:")
        print("  OPENAI_API_KEY=your_api_key")
        return 1
    
    # Create the analyzer
    print("Initializing SemanticPokerPersonalityAnalyzer...")
    analyzer = SemanticPokerPersonalityAnalyzer()
    
    # Index the game data
    # print("Indexing game data...")
    # analyzer.index_game_data()
    
    # Get player ID from command line or use default
    player_id = sys.argv[1] if len(sys.argv) > 1 else "P1"
    
    # Analyze player personality
    print(f"\nAnalyzing personality for player {player_id} using semantic search...")
    analysis = analyzer.analyze_player_personality(player_id)
    
    # Print the analysis
    print("\n" + "="*80)
    print(f"SEMANTIC PERSONALITY ANALYSIS FOR PLAYER {player_id}")
    print("="*80)
    print(analysis["analysis"])
    print("="*80)
    
    # Print trait examples
    # print("\nPersonality Trait Examples:")
    # for trait, examples in analysis["trait_examples"].items():
    #     print(f"\n{trait.upper()} TRAIT:")
        
    #     # Print actions for this trait
    #     actions = examples["actions"]
    #     if actions:
    #         print("  Actions:")
    #         for i, action in enumerate(actions):
    #             print(f"  {i+1}. {action['document']} (Similarity: {1 - action['distance']:.2f})")
    #     else:
    #         print("  No actions found for this trait.")
        
    #     # Print chat messages for this trait
    #     chat = examples["chat"]
    #     if chat:
    #         print("  Chat messages:")
    #         for i, message in enumerate(chat):
    #             print(f"  {i+1}. {message['document']} (Similarity: {1 - message['distance']:.2f})")
    #     else:
    #         print("  No chat messages found for this trait.")
    
    # Compare to archetypes
    print("\nComparing to poker archetypes...")
    archetypes = analyzer.compare_to_archetypes(player_id)
    
    if "error" in archetypes:
        print(f"Error: {archetypes['error']}")
    else:
        print(f"\nBest archetype match: {archetypes['best_match']} (Score: {archetypes['best_match_score']:.2f})")
        print("\nAll archetype similarities:")
        for archetype, score in archetypes["archetype_similarities"].items():
            print(f"- {archetype}: {score:.2f}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())