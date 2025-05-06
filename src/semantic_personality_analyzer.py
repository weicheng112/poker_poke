import os
import json
import chromadb
import openai
from typing import List, Dict, Any, Optional
import glob
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

class SemanticPokerPersonalityAnalyzer:
    def __init__(self, data_dir: str = "data/game_history", db_dir: str = "data/chroma_db"):
        """
        Initialize the SemanticPokerPersonalityAnalyzer.
        
        Args:
            data_dir: Directory containing game data JSON files
            db_dir: Directory to store ChromaDB database
        """
        self.data_dir = data_dir
        self.db_dir = db_dir
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_dir)
        
        # Create collections for different types of data
        self.actions_collection = self.client.get_or_create_collection("poker_actions")
        self.chat_collection = self.client.get_or_create_collection("poker_chat")
        self.summary_collection = self.client.get_or_create_collection("poker_summaries")
        
        # Define personality trait queries based on personalities.py
        self.trait_queries = {
            "aggression": "tendency to bet and raise rather than check and call, aggressive betting with large amounts",
            "bluff_tendency": "willingness to represent hands they don't have, bluffing behavior, betting with weak hands",
            "risk_tolerance": "comfort with variance and willingness to gamble, taking risks with marginal hands",
            "adaptability": "how quickly they adjust to opponents' strategies, changing play style based on opponents",
            "tilt_prone": "tendency to play emotionally after setbacks, emotional reactions in chat",
            "patience": "willingness to wait for premium hands, tight play, folding frequently"
        }
        
        # Load and process game data
        self.game_data = []
        self.load_game_data()
    
    def load_game_data(self):
        """Load all game data from JSON files in the data directory."""
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    game_data = json.load(f)
                    self.game_data.append(game_data)
                    print(f"Loaded game data from {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text using OpenAI API."""
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def index_game_data(self):
        """Index all game data in ChromaDB."""
        # We'll skip clearing existing data and just add new data
        # ChromaDB will overwrite entries with the same IDs
        
        for game in self.game_data:
            game_id = game.get("game_id", "unknown")
            
            # Index actions
            for i, action in enumerate(game.get("actions", [])):
                action_id = f"{game_id}_action_{i}"
                action_text = action.get("text_description", "")
                player_id = action.get("player_id", "unknown")
                
                if action_text:
                    self.actions_collection.add(
                        ids=[action_id],
                        embeddings=[self.generate_embedding(action_text)],
                        metadatas=[{
                            "game_id": game_id,
                            "player_id": player_id,
                            "action": action.get("action", ""),
                            "game_stage": action.get("game_stage", ""),
                            "amount": action.get("amount", 0),
                        }],
                        documents=[action_text]
                    )
            
            # Index chat messages
            for i, message in enumerate(game.get("chat_messages", [])):
                message_id = f"{game_id}_message_{i}"
                message_text = message.get("message", "")
                player_id = message.get("player_id", "unknown")
                
                if message_text:
                    self.chat_collection.add(
                        ids=[message_id],
                        embeddings=[self.generate_embedding(message_text)],
                        metadatas=[{
                            "game_id": game_id,
                            "player_id": player_id,
                            "sentiment": message.get("sentiment", ""),
                            "associated_action": message.get("associated_action", ""),
                        }],
                        documents=[message_text]
                    )
            
            # Index hand summary
            if "hand_summary" in game:
                summary = game["hand_summary"]
                summary_id = f"{game_id}_summary"
                summary_text = summary.get("text_description", "")
                
                if summary_text:
                    self.summary_collection.add(
                        ids=[summary_id],
                        embeddings=[self.generate_embedding(summary_text)],
                        metadatas=[{
                            "game_id": game_id,
                            "winner": summary.get("winner", ""),
                            "pot_amount": summary.get("pot_amount", 0),
                            "showdown_reached": summary.get("showdown_reached", False),
                        }],
                        documents=[summary_text]
                    )
    
    def analyze_player_personality(self, player_id: str) -> Dict[str, Any]:
        """
        Analyze a player's personality using semantic search to find relevant actions and chat messages.
        
        Args:
            player_id: The ID of the player to analyze (e.g., "P0", "P1")
            
        Returns:
            A dictionary containing the player's personality traits
        """
        # Find examples of each personality trait
        trait_examples = {}
        
        for trait, query in self.trait_queries.items():
            # Search for actions that match this trait
            trait_actions = self.query_player_actions_by_trait(player_id, query, n_results=3)
            
            # Search for chat messages that match this trait
            trait_chat = self.query_player_chat_by_trait(player_id, query, n_results=3)
            
            trait_examples[trait] = {
                "actions": trait_actions,
                "chat": trait_chat
            }
        
        # Get basic player statistics
        player_stats = self.get_player_statistics(player_id)
        
        # Generate a prompt for OpenAI to analyze the player's personality
        prompt = self._generate_semantic_analysis_prompt(player_id, trait_examples, player_stats)
        
        # Get the analysis from OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert poker player and psychologist specializing in analyzing poker player personalities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and return the analysis
        analysis = response.choices[0].message.content
        
        return {
            "player_id": player_id,
            "analysis": analysis,
            "trait_examples": trait_examples,
            "statistics": player_stats
        }
    
    def query_player_actions_by_trait(self, player_id: str, trait_query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query for player actions that match a specific personality trait.
        
        Args:
            player_id: The ID of the player
            trait_query: The query describing the personality trait
            n_results: Number of results to return
            
        Returns:
            A list of actions matching the trait
        """
        query_embedding = self.generate_embedding(trait_query)
        
        results = self.actions_collection.query(
            query_embeddings=[query_embedding],
            where={"player_id": player_id},
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        
        return [
            {
                "document": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results.get("documents", [[]])[0],
                results.get("metadatas", [[]])[0],
                results.get("distances", [[]])[0]
            )
        ]
    
    def query_player_chat_by_trait(self, player_id: str, trait_query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query for player chat messages that match a specific personality trait.
        
        Args:
            player_id: The ID of the player
            trait_query: The query describing the personality trait
            n_results: Number of results to return
            
        Returns:
            A list of chat messages matching the trait
        """
        query_embedding = self.generate_embedding(trait_query)
        
        results = self.chat_collection.query(
            query_embeddings=[query_embedding],
            where={"player_id": player_id},
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        
        return [
            {
                "document": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results.get("documents", [[]])[0],
                results.get("metadatas", [[]])[0],
                results.get("distances", [[]])[0]
            )
        ]
    
    def get_player_statistics(self, player_id: str) -> Dict[str, Any]:
        """Get basic statistics for a player."""
        # Get all actions for this player
        player_actions = self.actions_collection.get(
            where={"player_id": player_id},
            include=["metadatas"]
        )
        
        # Get all chat messages for this player
        player_chat = self.chat_collection.get(
            where={"player_id": player_id},
            include=["metadatas"]
        )
        
        # Count action types
        action_counts = {}
        total_actions = len(player_actions.get("metadatas", []))
        
        for action in player_actions.get("metadatas", []):
            action_type = action.get("action", "unknown")
            if action_type not in action_counts:
                action_counts[action_type] = 0
            action_counts[action_type] += 1
        
        # Calculate action percentages
        action_percentages = {
            action: (count / total_actions) * 100 if total_actions > 0 else 0
            for action, count in action_counts.items()
        }
        
        # Count sentiment types
        sentiment_counts = {}
        total_messages = len(player_chat.get("metadatas", []))
        
        for message in player_chat.get("metadatas", []):
            sentiment = message.get("sentiment", "unknown")
            if sentiment not in sentiment_counts:
                sentiment_counts[sentiment] = 0
            sentiment_counts[sentiment] += 1
        
        # Calculate sentiment percentages
        sentiment_percentages = {
            sentiment: (count / total_messages) * 100 if total_messages > 0 else 0
            for sentiment, count in sentiment_counts.items()
        }
        
        return {
            "total_actions": total_actions,
            "action_counts": action_counts,
            "action_percentages": action_percentages,
            "total_messages": total_messages,
            "sentiment_counts": sentiment_counts,
            "sentiment_percentages": sentiment_percentages
        }
    
    def _generate_semantic_analysis_prompt(self, player_id: str, trait_examples: Dict[str, Any], player_stats: Dict[str, Any]) -> str:
        """Generate a prompt for OpenAI to analyze the player's personality using semantic search results."""
        prompt = f"Analyze the poker personality of player {player_id} based on the following data:\n\n"
        
        # Add basic statistics
        prompt += "PLAYER STATISTICS:\n"
        prompt += f"Total actions: {player_stats['total_actions']}\n"
        
        if player_stats['action_percentages']:
            prompt += "Action percentages:\n"
            for action, percentage in player_stats['action_percentages'].items():
                prompt += f"- {action}: {percentage:.1f}%\n"
        
        prompt += f"\nTotal chat messages: {player_stats['total_messages']}\n"
        
        if player_stats['sentiment_percentages']:
            prompt += "Sentiment percentages:\n"
            for sentiment, percentage in player_stats['sentiment_percentages'].items():
                prompt += f"- {sentiment}: {percentage:.1f}%\n"
        
        # Add trait examples
        prompt += "\nPERSONALITY TRAIT EXAMPLES:\n"
        
        for trait, examples in trait_examples.items():
            prompt += f"\n{trait.upper()} TRAIT:\n"
            
            # Add actions for this trait
            actions = examples["actions"]
            if actions:
                prompt += "Actions:\n"
                for i, action in enumerate(actions):
                    prompt += f"{i+1}. {action['document']} (Game stage: {action['metadata'].get('game_stage', 'unknown')}, Action: {action['metadata'].get('action', 'unknown')}, Amount: {action['metadata'].get('amount', 0)}, Similarity: {1 - action['distance']:.2f})\n"
            else:
                prompt += "No actions found for this trait.\n"
            
            # Add chat messages for this trait
            chat = examples["chat"]
            if chat:
                prompt += "Chat messages:\n"
                for i, message in enumerate(chat):
                    prompt += f"{i+1}. {message['document']} (Sentiment: {message['metadata'].get('sentiment', 'unknown')}, Associated action: {message['metadata'].get('associated_action', 'unknown')}, Similarity: {1 - message['distance']:.2f})\n"
            else:
                prompt += "No chat messages found for this trait.\n"
        
        # Add instructions based on personalities.py traits
        prompt += "\nBased on the above data, analyze the player's poker personality. Consider the following aspects:\n"
        prompt += "1. Aggression: Tendency to bet and raise rather than check and call\n"
        prompt += "2. Bluff tendency: Willingness to represent hands they don't have\n"
        prompt += "3. Risk tolerance: Comfort with variance and willingness to gamble\n"
        prompt += "4. Adaptability: How quickly they adjust to opponents' strategies\n"
        prompt += "5. Tilt prone: Tendency to play emotionally after setbacks\n"
        prompt += "6. Patience: Willingness to wait for premium hands\n\n"
        prompt += "Finally, identify which poker archetype (tight_aggressive, loose_passive, maniac, rock, tricky, or calling_station) best matches this player's style."
        
        return prompt
    
    def compare_to_archetypes(self, player_id: str) -> Dict[str, Any]:
        """
        Compare a player's behavior to common poker personality archetypes.
        
        Args:
            player_id: The ID of the player to analyze
            
        Returns:
            A dictionary containing similarity scores to different archetypes
        """
        # Define poker archetypes based on personalities.py
        archetypes = {
            "tight_aggressive": "Plays few hands but bets aggressively with strong holdings. Rarely bluffs but when they do, it's credible. Waits for good spots and capitalizes on them.",
            "loose_passive": "Plays many hands but rarely raises, preferring to call. Chases draws frequently and hopes to hit big hands. Avoids confrontation.",
            "maniac": "Extremely aggressive player who raises frequently and bluffs often. Creates chaos at the table and puts opponents to difficult decisions.",
            "rock": "Extremely tight player who only plays premium hands. Very conservative and risk-averse. Rarely bluffs and folds to aggression.",
            "tricky": "Unpredictable player who mixes up their play. Uses creative lines and unorthodox strategies to confuse opponents.",
            "calling_station": "Calls excessively and rarely folds once invested in a hand. Chases draws to the river regardless of odds."
        }
        
        # Get all actions for this player
        player_actions = self.actions_collection.get(
            where={"player_id": player_id},
            include=["documents"]
        )
        
        # Get all chat messages for this player
        player_chat = self.chat_collection.get(
            where={"player_id": player_id},
            include=["documents"]
        )
        
        # Get all player text
        all_player_texts = player_actions.get("documents", []) + player_chat.get("documents", [])
        
        if not all_player_texts:
            return {"error": "No data available for this player"}
        
        # Generate embedding for player text using chunking to handle large text
        player_embedding = self._generate_chunked_embedding(all_player_texts)
        
        # Calculate similarity to each archetype
        archetype_similarities = {}
        
        for archetype, description in archetypes.items():
            # Generate embedding for archetype description
            # Archetype descriptions are short, but using the same method for consistency
            archetype_embedding = self._generate_chunked_embedding([description])
            
            # Calculate cosine similarity
            similarity = self._calculate_similarity(player_embedding, archetype_embedding)
            
            archetype_similarities[archetype] = similarity
        
        # Sort archetypes by similarity
        sorted_archetypes = sorted(
            archetype_similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "player_id": player_id,
            "archetype_similarities": dict(sorted_archetypes),
            "best_match": sorted_archetypes[0][0] if sorted_archetypes else None,
            "best_match_score": sorted_archetypes[0][1] if sorted_archetypes else 0
        }
    
    def _generate_chunked_embedding(self, texts: List[str], max_tokens_per_chunk: int = 4000) -> List[float]:
        """
        Generate embeddings for large text by chunking and averaging.
        
        Args:
            texts: List of text documents to embed
            max_tokens_per_chunk: Maximum tokens per chunk (default: 4000 to be safe)
            
        Returns:
            List[float]: The averaged embedding vector
        """
        import numpy as np
        
        # If no texts, return error
        if not texts:
            raise ValueError("No texts provided for embedding")
        
        # Estimate tokens (rough approximation: 4 chars ≈ 1 token)
        def estimate_tokens(text):
            return len(text) // 4
        
        # Create chunks that fit within token limit
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for text in texts:
            text_tokens = estimate_tokens(text)
            
            # If this text alone exceeds the limit, split it further
            if text_tokens > max_tokens_per_chunk:
                # Split long text into smaller pieces (rough approximation)
                words = text.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = estimate_tokens(word + " ")
                    if temp_tokens + word_tokens > max_tokens_per_chunk:
                        chunks.append(" ".join(temp_chunk))
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    chunks.append(" ".join(temp_chunk))
            
            # If adding this text would exceed the limit, finalize current chunk and start a new one
            elif current_tokens + text_tokens > max_tokens_per_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [text]
                current_tokens = text_tokens
            # Otherwise, add to current chunk
            else:
                current_chunk.append(text)
                current_tokens += text_tokens
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        print(f"Split player text into {len(chunks)} chunks for embedding")
        
        # Generate embeddings for each chunk
        chunk_embeddings = []
        for i, chunk in enumerate(chunks):
            try:
                print(f"Generating embedding for chunk {i+1}/{len(chunks)} (approx. {estimate_tokens(chunk)} tokens)")
                embedding = self.generate_embedding(chunk)
                chunk_embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding for chunk {i+1}: {e}")
                # Continue with other chunks if one fails
        
        if not chunk_embeddings:
            raise ValueError("Failed to generate any embeddings from the text chunks")
        
        # Average the embeddings
        avg_embedding = np.mean(chunk_embeddings, axis=0).tolist()
        
        return avg_embedding
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        import numpy as np
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        return dot_product / (norm1 * norm2)

# Example usage
if __name__ == "__main__":
    analyzer = SemanticPokerPersonalityAnalyzer()
    analyzer.index_game_data()
    
    # Analyze player P1's personality
    p1_analysis = analyzer.analyze_player_personality("P1")
    print("\nPlayer P1 Personality Analysis:")
    print(p1_analysis["analysis"])
    
    # Compare player P1 to archetypes
    # p1_archetypes = analyzer.compare_to_archetypes("P1")
    # print("\nPlayer P1 Archetype Comparison:")
    # print(f"Best match: {p1_archetypes['best_match']} (Score: {p1_archetypes['best_match_score']:.2f})")
    # print("All archetype similarities:")
    # for archetype, score in p1_archetypes["archetype_similarities"].items():
    #     print(f"- {archetype}: {score:.2f}")