"""
Game Data Extractor for Poker RAG System

This module extracts data from poker games and structures it for use in a vector database.
It captures game actions, chat messages, and game state information, then saves it to a JSON file.
"""

import json
import uuid
import datetime
import os
import pokers as pk
from src.engine_autogen import play_hand
from src.personalities import get_game_stage

class GameDataExtractor:
    """
    Extracts and structures poker game data for use in a vector database.
    """
    
    def __init__(self, output_dir="data"):
        """
        Initialize the GameDataExtractor.
        
        Args:
            output_dir (str): Directory to save JSON output files
        """
        self.output_dir = output_dir
        
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def extract_from_game(self, game_result):
        """
        Extract structured data from a game result.
        
        Args:
            game_result (dict): The result from play_hand()
            
        Returns:
            dict: Structured game data
        """
        # Generate a unique game ID
        game_id = f"game_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.datetime.now().isoformat()
        
        # Extract game trace information
        trace = game_result["trace"]
        
        # Extract chat history
        chat_history = game_result["chat_history"]
        
        # Extract player information
        players_info = game_result.get("players", {})
        
        # Create the structured game document
        game_doc = {
            "document_type": "game",
            "game_id": game_id,
            "timestamp": timestamp,
            "players": self._extract_players_data(players_info),
            "actions": self._extract_actions_data(trace, game_id),
            "chat_messages": self._extract_chat_data(chat_history, game_id),
            "hand_summary": self._create_hand_summary(trace, game_id)
        }
        
        return game_doc
    
    def _extract_players_data(self, players_info):
        """
        Extract player information.
        
        Args:
            players_info (dict): Player information from game result
            
        Returns:
            dict: Structured player data
        """
        players_data = {}
        
        for player_id, info in players_info.items():
            players_data[player_id] = {
                "personality_type": info.get("personality_type", "unknown"),
                "personality_traits": info.get("personality_traits", {})
            }
        
        return players_data
    
    def _extract_actions_data(self, trace, game_id):
        """
        Extract action data from the game trace.
        
        Args:
            trace (list): List of game states
            game_id (str): Unique game identifier
            
        Returns:
            list: List of action documents
        """
        actions = []
        
        # Process each state in the trace, including the final state
        for i in range(len(trace)):
            current_state = trace[i]
            
            # Check if the current state has from_action
            if hasattr(current_state, "from_action") and current_state.from_action:
                action_record = current_state.from_action
                
                # Get the player who made this action
                player_idx = action_record.player
                player_id = f"P{player_idx}"
                
                # Get the action type from the ActionEnum
                action_enum = action_record.action.action
                # Convert ActionEnum to string
                if action_enum == pk.ActionEnum.Fold:
                    action_type = "fold"
                elif action_enum == pk.ActionEnum.Check:
                    action_type = "check"
                elif action_enum == pk.ActionEnum.Call:
                    action_type = "call"
                elif action_enum == pk.ActionEnum.Raise:
                    action_type = "raise"
                else:
                    action_type = "unknown"
                
                # Get the action amount if applicable
                amount = action_record.action.amount if hasattr(action_record.action, "amount") else 0
                
                # Get the game stage
                stage_enum = action_record.stage
                # Convert Stage enum to string
                if stage_enum == pk.Stage.Preflop:
                    game_stage = "preflop"
                elif stage_enum == pk.Stage.Flop:
                    game_stage = "flop"
                elif stage_enum == pk.Stage.Turn:
                    game_stage = "turn"
                elif stage_enum == pk.Stage.River:
                    game_stage = "river"
                elif stage_enum == pk.Stage.Showdown:
                    game_stage = "showdown"
                else:
                    game_stage = "unknown"
                
                # Get pot size
                pot_size = getattr(current_state, "pot", 0)
                
                # Get board cards if available
                board_cards = ""
                if hasattr(current_state, "public_cards") and current_state.public_cards:
                    try:
                        # Try to format cards properly
                        card_strs = []
                        for card in current_state.public_cards:
                            # Try to extract rank and suit
                            if hasattr(card, "rank") and hasattr(card, "suit"):
                                rank_map = {
                                    0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8",
                                    7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"
                                }
                                suit_map = {0: "c", 1: "d", 2: "h", 3: "s"}
                                
                                rank_str = rank_map.get(int(card.rank), str(card.rank))
                                suit_str = suit_map.get(int(card.suit), str(card.suit))
                                
                                card_strs.append(f"{rank_str}{suit_str}")
                            else:
                                card_strs.append(str(card))
                        
                        board_cards = " ".join(card_strs)
                    except Exception as e:
                        # Fallback to default string representation
                        board_cards = " ".join(str(card) for card in current_state.public_cards)
                
                # Get player position
                position = self._determine_position(current_state, player_idx)
                
                # Create text description
                text_description = f"{player_id} {action_type}{'ed' if not action_type.endswith('e') else 'd'}"
                if amount > 0:
                    text_description += f" to {amount}"
                text_description += f" in {position} position during {game_stage}"
                if board_cards:
                    text_description += f" with board {board_cards}"
                
                # Create action document
                action_doc = {
                    "document_type": "game_action",
                    "game_id": game_id,
                    "player_id": player_id,
                    "action_id": f"action_{game_id}_{i}",
                    "game_stage": game_stage,
                    "action": action_type,
                    "amount": amount,
                    "pot_size": pot_size,
                    "position": position,
                    "board_cards": board_cards,
                    "text_description": text_description
                }
                
                actions.append(action_doc)
        
        return actions
        
        return actions
    
    def _extract_chat_data(self, chat_history, game_id):
        """
        Extract chat message data.
        
        Args:
            chat_history (list): List of chat messages
            game_id (str): Unique game identifier
            
        Returns:
            list: List of chat message documents
        """
        chat_docs = []
        
        for i, chat_entry in enumerate(chat_history):
            # Parse the chat entry
            parts = chat_entry.split(":", 1)
            if len(parts) != 2:
                continue
                
            player_id = parts[0].strip()
            message = parts[1].strip()
            
            # Extract sentiment (simple keyword-based approach)
            sentiment = self._analyze_sentiment(message)
            
            # Extract associated action if mentioned
            associated_action = self._extract_action_from_message(message)
            
            # Create text description
            text_description = f"{player_id} said: '{message}', expressing {sentiment} sentiment"
            if associated_action:
                text_description += f" while {associated_action}ing"
            
            # Create chat document
            chat_doc = {
                "document_type": "chat_message",
                "game_id": game_id,
                "player_id": player_id,
                "message_id": f"message_{game_id}_{i}",
                "message": message,
                "sentiment": sentiment,
                "associated_action": associated_action,
                "text_description": text_description
            }
            
            chat_docs.append(chat_doc)
        
        return chat_docs
    
    def _create_hand_summary(self, trace, game_id):
        """
        Create a summary of the hand.
        
        Args:
            trace (list): List of game states
            game_id (str): Unique game identifier
            
        Returns:
            dict: Hand summary document
        """
        # Get initial and final states
        initial_state = trace[0]
        final_state = trace[-1]
        
        # Extract player hole cards if available
        hole_cards = {}
        # Determine number of players
        n_players = 2  # Default to 2 players
        if hasattr(initial_state, "n_players"):
            n_players = initial_state.n_players
        elif hasattr(initial_state, "players_state") and isinstance(initial_state.players_state, list):
            n_players = len(initial_state.players_state)
            
        for i in range(n_players):
            if hasattr(initial_state, f"hole_{i}"):
                cards = getattr(initial_state, f"hole_{i}")
                if isinstance(cards, tuple) and len(cards) == 2:
                    try:
                        # Try to format cards properly
                        card_strs = []
                        for card in cards:
                            # Try to extract rank and suit
                            if hasattr(card, "rank") and hasattr(card, "suit"):
                                rank_map = {
                                    0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8",
                                    7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"
                                }
                                suit_map = {0: "c", 1: "d", 2: "h", 3: "s"}
                                
                                rank_str = rank_map.get(int(card.rank), str(card.rank))
                                suit_str = suit_map.get(int(card.suit), str(card.suit))
                                
                                card_strs.append(f"{rank_str}{suit_str}")
                            else:
                                card_strs.append(str(card))
                        
                        hole_cards[f"P{i}"] = " ".join(card_strs)
                    except Exception as e:
                        # Fallback to default string representation
                        hole_cards[f"P{i}"] = " ".join(str(card) for card in cards)
            elif hasattr(initial_state, "players_state") and i < len(initial_state.players_state):
                if hasattr(initial_state.players_state[i], "hand"):
                    cards = initial_state.players_state[i].hand
                    if isinstance(cards, tuple) and len(cards) == 2:
                        try:
                            # Try to format cards properly
                            card_strs = []
                            for card in cards:
                                # Try to extract rank and suit
                                if hasattr(card, "rank") and hasattr(card, "suit"):
                                    rank_map = {
                                        0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8",
                                        7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"
                                    }
                                    suit_map = {0: "c", 1: "d", 2: "h", 3: "s"}
                                    
                                    rank_str = rank_map.get(int(card.rank), str(card.rank))
                                    suit_str = suit_map.get(int(card.suit), str(card.suit))
                                    
                                    card_strs.append(f"{rank_str}{suit_str}")
                                else:
                                    card_strs.append(str(card))
                            
                            hole_cards[f"P{i}"] = " ".join(card_strs)
                        except Exception as e:
                            # Fallback to default string representation
                            hole_cards[f"P{i}"] = " ".join(str(card) for card in cards)
        
        # Determine winner
        winner = None
        if hasattr(final_state, "winners") and final_state.winners:
            winner = f"P{final_state.winners[0]}"
        else:
            # If no explicit winner, determine based on the last action
            if hasattr(final_state, "from_action") and final_state.from_action:
                action_record = final_state.from_action
                if action_record.action.action == pk.ActionEnum.Fold:
                    # If the last action was a fold, the other player won
                    folding_player = action_record.player
                    winner = f"P{1 - folding_player}"  # Assuming 2 players (0 and 1)
        
        # Calculate profit/loss for each player
        profit_loss = {}
        
        # In a two-player game, the winner's profit equals the loser's loss
        if n_players == 2 and winner:
            winner_idx = int(winner[1])  # Extract the player index from "P0" or "P1"
            loser_idx = 1 - winner_idx   # In a 2-player game, if one is 0, the other is 1
            
            # For simplicity, we'll use the big blind (10) as the standard profit/loss
            # This is a simplification but works for most basic poker scenarios
            profit_loss[winner] = 10.0
            profit_loss[f"P{loser_idx}"] = -10.0
        else:
            # If no winner or more than 2 players, set profit/loss to 0
            for i in range(n_players):
                profit_loss[f"P{i}"] = 0.0
                
        print("-----------------------")
        print(f"Profit/Loss: {profit_loss}")
        print("-----------------------")
        
        # Determine if showdown was reached
        showdown_reached = False
        if hasattr(final_state, "showdown"):
            showdown_reached = final_state.showdown
        elif hasattr(final_state, "stage") and final_state.stage == pk.Stage.Showdown:
            showdown_reached = True
        
        # Get final board cards
        final_board = ""
        if hasattr(final_state, "public_cards") and final_state.public_cards:
            try:
                # Try to format cards properly
                card_strs = []
                for card in final_state.public_cards:
                    # Try to extract rank and suit
                    if hasattr(card, "rank") and hasattr(card, "suit"):
                        rank_map = {
                            0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8",
                            7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"
                        }
                        suit_map = {0: "c", 1: "d", 2: "h", 3: "s"}
                        
                        rank_str = rank_map.get(int(card.rank), str(card.rank))
                        suit_str = suit_map.get(int(card.suit), str(card.suit))
                        
                        card_strs.append(f"{rank_str}{suit_str}")
                    else:
                        card_strs.append(str(card))
                
                final_board = " ".join(card_strs)
            except Exception as e:
                # Fallback to default string representation
                final_board = " ".join(str(card) for card in final_state.public_cards)
        
        # Get pot amount for the text description
        pot_amount = getattr(final_state, "pot", 0)
        
        # Create text description
        text_description = f"Game {game_id} ended with "
        if winner:
            text_description += f"{winner} winning"
            if pot_amount > 0:
                text_description += f" a pot of {pot_amount}"
        else:
            text_description += "no clear winner"
        
        if showdown_reached:
            text_description += " at showdown"
        else:
            # If not showdown, describe how the hand ended
            if hasattr(final_state, "from_action") and final_state.from_action:
                action_record = final_state.from_action
                if action_record.action.action == pk.ActionEnum.Fold:
                    folding_player = action_record.player
                    text_description += f" when P{folding_player} folded"
        
        if final_board:
            text_description += f" with final board {final_board}"
        
        # Create hand summary document
        hand_summary = {
            "document_type": "hand_summary",
            "game_id": game_id,
            "hole_cards": hole_cards,
            "winner": winner,
            "pot_amount": pot_amount,
            "profit_loss": profit_loss,
            "showdown_reached": showdown_reached,
            "final_board": final_board,
            "text_description": text_description
        }
        
        return hand_summary
    
    def _determine_action_type(self, current_state, previous_state):
        """
        Determine the type of action that led from previous_state to current_state.
        
        Args:
            current_state: The current game state
            previous_state: The previous game state
            
        Returns:
            str: Action type (fold, check, call, bet, raise)
        """
        # Check if the current state has from_action
        if hasattr(current_state, "from_action") and current_state.from_action:
            action_enum = current_state.from_action.action.action
            return action_enum.name.lower()
        
        # If from_action is not available, try to infer from state changes
        player_idx = previous_state.current_player if hasattr(previous_state, "current_player") else 0
        
        # Check if player is active in previous state but not in current state (fold)
        if (hasattr(previous_state, "players_state") and hasattr(current_state, "players_state") and
            len(previous_state.players_state) > player_idx and len(current_state.players_state) > player_idx):
            if previous_state.players_state[player_idx].active and not current_state.players_state[player_idx].active:
                return "fold"
        
        # Check for bet/raise/call by comparing bet_chips
        if (hasattr(previous_state, "players_state") and hasattr(current_state, "players_state") and
            len(previous_state.players_state) > player_idx and len(current_state.players_state) > player_idx):
            prev_bet = previous_state.players_state[player_idx].bet_chips
            curr_bet = current_state.players_state[player_idx].bet_chips
            
            if curr_bet > prev_bet:
                # Determine if it's a bet, raise, or call
                max_prev_bet = max(ps.bet_chips for ps in previous_state.players_state)
                
                if prev_bet == 0 and max_prev_bet == 0:
                    return "bet"
                elif prev_bet < max_prev_bet and curr_bet == max_prev_bet:
                    return "call"
                else:
                    return "raise"
            elif curr_bet == prev_bet and prev_bet > 0:
                # Check if this is a call or check
                max_prev_bet = max(ps.bet_chips for ps in previous_state.players_state)
                if prev_bet < max_prev_bet:
                    return "call"
                else:
                    return "check"
        
        # Default to check if no other action was determined
        return "check"
    
    def _determine_position(self, state, player_idx):
        """
        Determine the player's position at the table.
        
        Args:
            state: The game state
            player_idx (int): Player index
            
        Returns:
            str: Position description (button, sb, bb, early, middle, late)
        """
        if not hasattr(state, "n_players"):
            return "unknown"
            
        n_players = state.n_players
        
        # Determine button position
        button = getattr(state, "button", 0)
        
        # Calculate relative position
        relative_pos = (player_idx - button) % n_players
        
        if relative_pos == 0:
            return "button"
        elif relative_pos == 1:
            return "small_blind"
        elif relative_pos == 2:
            return "big_blind"
        elif relative_pos <= n_players // 3:
            return "early"
        elif relative_pos <= 2 * n_players // 3:
            return "middle"
        else:
            return "late"
    
    def _analyze_sentiment(self, message):
        """
        Simple keyword-based sentiment analysis for poker chat messages.
        
        Args:
            message (str): Chat message
            
        Returns:
            str: Sentiment category
        """
        message = message.lower()
        
        # Define keyword lists for different sentiments
        confident_keywords = ["confident", "strong", "value", "edge", "calculated", "odds", "premium"]
        aggressive_keywords = ["raise", "bet", "pressure", "aggressive", "action", "attack"]
        cautious_keywords = ["careful", "fold", "wait", "patient", "risk"]
        friendly_keywords = ["fun", "nice", "good", "luck", "enjoy", "interesting"]
        
        # Count keyword occurrences
        confident_count = sum(1 for word in confident_keywords if word in message)
        aggressive_count = sum(1 for word in aggressive_keywords if word in message)
        cautious_count = sum(1 for word in cautious_keywords if word in message)
        friendly_count = sum(1 for word in friendly_keywords if word in message)
        
        # Determine the dominant sentiment
        counts = {
            "confident": confident_count,
            "aggressive": aggressive_count,
            "cautious": cautious_count,
            "friendly": friendly_count
        }
        
        max_sentiment = max(counts, key=counts.get)
        
        # If no keywords matched, return "neutral"
        if counts[max_sentiment] == 0:
            return "neutral"
            
        return max_sentiment
    
    def _extract_action_from_message(self, message):
        """
        Extract action mentioned in a chat message.
        
        Args:
            message (str): Chat message
            
        Returns:
            str or None: Action mentioned in the message
        """
        message = message.lower()
        
        # Check for action keywords
        if "fold" in message:
            return "fold"
        elif "check" in message:
            return "check"
        elif "call" in message:
            return "call"
        elif "raise" in message:
            return "raise"
        elif "bet" in message:
            return "bet"
            
        return None
    
    def save_to_json(self, game_doc, filename=None):
        """
        Save the game document to a JSON file.
        
        Args:
            game_doc (dict): Game document to save
            filename (str, optional): Custom filename. If None, a filename will be generated.
            
        Returns:
            str: Path to the saved file
        """
        if filename is None:
            filename = f"game_{game_doc['game_id']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(game_doc, f, indent=2)
        
        print(f"Game data saved to {filepath}")
        return filepath


def extract_and_save_game(seed=1234, output_dir="data"):
    """
    Play a poker game, extract the data, and save it to a JSON file.
    
    Args:
        seed (int): Random seed for the game
        output_dir (str): Directory to save the output
        
    Returns:
        str: Path to the saved file
    """
    # Play a hand
    game_result = play_hand(seed=seed)
    
    # Extract and save the data
    extractor = GameDataExtractor(output_dir=output_dir)
    game_doc = extractor.extract_from_game(game_result)
    filepath = extractor.save_to_json(game_doc)
    
    return filepath


if __name__ == "__main__":
    # Extract data from a game and save it to a JSON file
    filepath = extract_and_save_game(seed=1234)
    print(f"Game data extracted and saved to {filepath}")