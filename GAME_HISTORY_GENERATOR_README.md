# Poker Game History Generator

This tool generates a large dataset of poker game history records for training and testing the poker player personality analyzer.

## Overview

The game history generator:

1. Runs multiple poker games with different random seeds
2. Extracts game data including actions, chat messages, and hand summaries
3. Removes personality information from the data
4. Saves the data to JSON files
5. Analyzes the generated data to provide statistics

## Usage

### Basic Usage

To generate 200 game history records with seeds from 1000 to 1999:

```
python generate_game_history.py
```

### Custom Parameters

You can customize the generation process with command-line arguments:

```
python generate_game_history.py --start-seed 2000 --end-seed 2099 --output-dir data/custom_history
```

### Available Options

- `--start-seed`: Starting seed value (default: 1000)
- `--end-seed`: Ending seed value (default: 1999)
- `--output-dir`: Output directory (default: data/game_history)
- `--skip-analysis`: Skip data analysis after generation

### Examples

Generate 50 games with seeds 5000-5049:

```
python generate_game_history.py --start-seed 5000 --end-seed 5049
```

Generate 100 games and skip analysis (faster for large datasets):

```
python generate_game_history.py --start-seed 1000 --end-seed 1099 --skip-analysis
```

## Output

The generator creates:

1. A directory of JSON files, one for each game
2. Each file contains:
   - Game metadata (ID, timestamp)
   - Player information
   - Actions (raises, calls, folds, etc.)
   - Chat messages with sentiment analysis
   - Hand summary (winner, pot amount, profit/loss)

## Data Analysis

After generation, the tool analyzes the data and provides statistics:

- Total number of games
- Action counts (raises, calls, folds, etc.)
- Chat sentiment counts (friendly, aggressive, etc.)
- Game stages reached (preflop, flop, turn, river)
- Showdown frequency
- Player win counts

## Next Steps

After generating the data:

1. Use the data to train the semantic personality analyzer
2. Test the analyzer's ability to identify player personalities
3. Analyze patterns in player behavior across multiple games

## Performance Considerations

- Generating a large number of games can take significant time
- For very large datasets (1000+ games), use the `--skip-analysis` flag and analyze the data separately
- The generation process includes a small delay between games to prevent system overload
