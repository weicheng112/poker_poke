# Semantic Poker Personality Analyzer Workflow

Based on the `semantic_personality_analyzer.py` file, here's how the workflow of the system operates:

## Initialization and Setup

1. **Analyzer Initialization** (`__init__` method):
   - Creates a ChromaDB persistent client
   - Sets up three collections for different data types:
     - `poker_actions`: Stores player actions
     - `poker_chat`: Stores chat messages
     - `poker_summaries`: Stores hand summaries
   - Defines personality trait queries (aggression, bluff tendency, risk tolerance, etc.)
   - Loads game data from JSON files

## Data Loading and Processing

1. **Data Indexing** (`index_game_data` method):
   - For each game in the loaded data:
     - Extracts actions, chat messages, and hand summaries
     - Generates embeddings for each text element using OpenAI's API
     - Stores the embeddings and metadata in the appropriate ChromaDB collections

## Player Analysis Process

1. **Personality Analysis** (`analyze_player_personality` method):

   - For each personality trait (aggression, bluff tendency, etc.):
     - Searches for player actions that match this trait
     - Searches for chat messages that match this trait
     - Collects examples of each trait
   - Gets basic player statistics (action counts, sentiment counts)
   - Generates a prompt for OpenAI to analyze the player's personality
   - Gets the analysis from OpenAI's GPT model
   - Returns the analysis, trait examples, and statistics

2. **Trait Querying** (`query_player_actions_by_trait` and `query_player_chat_by_trait` methods):

   - Searches the ChromaDB collections for actions/messages that match the trait
   - Returns the most similar examples with their metadata and similarity scores

3. **Statistics Collection** (`get_player_statistics` method):
   - Gets all actions and chat messages for the player
   - Counts action types (raise, call, fold, etc.)
   - Calculates action percentages
   - Counts sentiment types in chat messages
   - Calculates sentiment percentages

## Archetype Comparison

1. **Archetype Comparison** (`compare_to_archetypes` method):
   - Defines poker archetypes (tight_aggressive, loose_passive, etc.)
   - Gets all actions and chat messages for the player
   - Generates an embedding for the combined player text using chunking
   - For each archetype:
     - Generates an embedding for the archetype description
     - Calculates similarity between player and archetype
   - Returns the best matching archetype and all similarity scores

## Key Workflow Steps for Analysis

When analyzing a player's personality, the system follows these steps:

1. **Input**: Player ID (e.g., "P0", "P1")
2. **Semantic Search**: Find examples of each personality trait in the player's actions and chat
3. **Statistics**: Calculate action and sentiment percentages
4. **LLM Analysis**: Generate a comprehensive personality analysis using OpenAI's GPT model
5. **Archetype Matching**: Compare the player to common poker archetypes
6. **Output**: Return a detailed personality profile with trait assessments and archetype matches

This workflow combines vector embeddings, semantic search, and large language models to create a sophisticated personality analysis system that can identify player tendencies and match them to established poker archetypes.
