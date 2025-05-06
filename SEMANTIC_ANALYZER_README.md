# Semantic Poker Player Personality Analyzer

This system uses ChromaDB and OpenAI embeddings to analyze poker player personalities based on their actions and chat messages during games, leveraging semantic search capabilities.

## Overview

The Semantic Poker Player Personality Analyzer uses a Retrieval-Augmented Generation (RAG) approach with semantic search to analyze player personalities:

1. **Data Collection**: Game data is collected from poker games, including actions, chat messages, and hand summaries.
2. **Embedding Generation**: OpenAI's embedding model is used to convert text data into vector embeddings.
3. **Vector Database**: ChromaDB stores these embeddings for efficient similarity search.
4. **Semantic Search**: The system uses semantic queries to find examples of specific personality traits.
5. **Archetype Comparison**: Players are compared to common poker personality archetypes.
6. **Analysis**: When querying for a player's personality, relevant data is retrieved and analyzed using OpenAI's GPT model.

## Advantages of Semantic Search

Unlike the basic personality analyzer, the semantic version leverages the power of vector embeddings to:

1. **Find Examples of Specific Traits**: Instead of analyzing all actions, it searches for specific examples of traits like "aggressive play" or "bluffing behavior".

2. **Compare to Archetypes**: It compares a player's behavior to known poker personality archetypes like "tight-aggressive" or "loose-passive".

3. **Understand Context**: It understands the semantic meaning of actions and chat messages, not just keywords.

4. **Scale Efficiently**: As the dataset grows, semantic search remains efficient for finding relevant examples.

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- ChromaDB
- Required Python packages (see below)

### Installation

1. Install required packages:

   ```
   pip install chromadb openai python-dotenv numpy
   ```

2. Set your OpenAI API key as an environment variable in a `.env` file:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Generating Game Data

Before analyzing personalities, you need to generate game data:

1. Run poker games using the `run_single_game.py` script:

   ```
   python run_single_game.py
   ```

2. This will generate game data in JSON format in the `data/test_game` directory.

### Analyzing Player Personalities

Use the `analyze_semantic_personality.py` script to analyze player personalities:

```
python analyze_semantic_personality.py [player_id]
```

Where `[player_id]` is the ID of the player to analyze (e.g., "P0", "P1"). If not provided, it defaults to "P1".

### Example Output

```
SEMANTIC PERSONALITY ANALYSIS FOR PLAYER P1
==============================================================
Player P1 exhibits a loose-aggressive playing style, characterized by frequent raising and a willingness to put significant chips into the pot. Their actions show a high risk tolerance, as evidenced by their multiple raises during the preflop and flop stages.

Communication style is notably friendly and enthusiastic, with frequent use of phrases like "feeling lucky" and "let's have some fun." This suggests a recreational player who values enjoyment over strict strategic play.

The player demonstrates moderate emotional control, maintaining a positive attitude even when folding. Their decision-making appears to be more intuition-based than calculated, often citing "feeling lucky" as motivation for actions rather than pot odds or hand strength considerations.

Based on the semantic analysis, P1 most closely matches the "loose-aggressive" archetype, with some elements of the "maniac" archetype in their betting patterns.
==============================================================

Personality Trait Examples:
AGGRESSIVE TRAIT:
  Actions:
  1. P1 raised to 35.0 in unknown position during preflop (Similarity: 0.82)
  Chat messages:
  1. "I'll raise to 35.0 and see where this goes—could be a fun hand if I'm lucky!" (Similarity: 0.78)

LOOSE TRAIT:
  Actions:
  1. P1 called in unknown position during preflop (Similarity: 0.75)
  Chat messages:
  1. "I'll call and see where this fun hand takes us. Feeling a bit lucky today!" (Similarity: 0.80)

Best archetype match: loose_aggressive (Score: 0.85)

All archetype similarities:
- loose_aggressive: 0.85
- maniac: 0.72
- tight_aggressive: 0.65
- loose_passive: 0.58
- calling_station: 0.52
- tight_passive: 0.45
- rock: 0.38
- nit: 0.32
```

## System Components

### `src/semantic_personality_analyzer.py`

The main class that handles:

- Loading game data from JSON files
- Generating embeddings using OpenAI
- Indexing data in ChromaDB
- Performing semantic searches for personality traits
- Comparing players to poker archetypes
- Analyzing player personalities

### `analyze_semantic_personality.py`

A command-line script to run the semantic personality analyzer and display results.

## Personality Traits and Archetypes

The system analyzes the following personality traits:

- **Aggressive**: Betting or raising with large amounts
- **Passive**: Calling or checking frequently
- **Tight**: Folding frequently, playing few hands
- **Loose**: Playing many hands, rarely folding
- **Bluffing**: Betting with weak hands
- **Emotional**: Showing frustration or excitement in chat
- **Calculated**: Making strategic decisions
- **Risk-averse**: Avoiding risks, folding to big bets
- **Risk-taking**: Taking risks, calling or raising with marginal hands

And compares players to these archetypes:

- **Tight-Aggressive (TAG)**: Plays few hands but bets aggressively with strong hands
- **Loose-Aggressive (LAG)**: Plays many hands and bets aggressively, often bluffing
- **Tight-Passive (Rock)**: Plays few hands and tends to call rather than raise
- **Loose-Passive (Calling Station)**: Plays many hands but rarely raises
- **Maniac**: Extremely aggressive, raises frequently with large bets
- **Nit**: Extremely risk-averse, folds to any significant bet

## Customization

You can customize the analyzer by modifying:

- The trait queries (`trait_queries` in `SemanticPokerPersonalityAnalyzer`)
- The archetypes (`archetypes` in `compare_to_archetypes` method)
- The analysis prompt (in the `_generate_semantic_analysis_prompt` method)
- The OpenAI models used for embeddings and analysis

## Limitations

- The quality of analysis depends on the amount and quality of game data available.
- OpenAI API calls incur costs based on token usage.
- The system requires an internet connection to generate embeddings and analyses.

## Future Improvements

- Add support for more poker variants
- Implement more sophisticated personality models
- Add visualization of player tendencies
- Integrate with live poker games for real-time analysis
- Implement clustering to discover new personality archetypes
