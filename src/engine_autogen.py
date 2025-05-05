import pokers as pk
import autogen
from src.solver_tool import get_action
from src.player import PlayerAgent

def play_hand(seed=1234):
    """
    Play a poker hand using AutoGen agents for communication.
    This implementation leverages AutoGen's built-in communication mechanisms.
    """
    # Initialize the poker state
    state = pk.State.from_seed(n_players=2, button=0, sb=5, bb=10, stake=1000, seed=seed)
    
    # Create the agents
    player0 = PlayerAgent("P0")
    player1 = PlayerAgent("P1")
    
    # Create a group chat for the agents
    groupchat = autogen.GroupChat(
        agents=[player0, player1],
        messages=[],
        max_round=20  # Limit the number of conversation rounds
    )
    
    # Create a manager to facilitate the conversation
    manager = autogen.GroupChatManager(groupchat=groupchat)
    
    # Initialize game state
    trace = [state]
    chat_history = []
    
    # Play the hand
    while not trace[-1].final_state:
        state = trace[-1]
        p = state.current_player
        current_agent = player0 if p == 0 else player1
        opponent_agent = player1 if p == 0 else player0
        
        # Update the agent's blackboard with the current state
        current_agent.blackboard["state"] = state
        
        # Determine the game stage
        game_stage = "preflop"
        if hasattr(state, "board") and state.board:
            if len(state.board) == 3:
                game_stage = "flop"
            elif len(state.board) == 4:
                game_stage = "turn"
            elif len(state.board) == 5:
                game_stage = "river"
        
        # Get information about the board
        board_info = ""
        if hasattr(state, "board") and state.board:
            board_info = f"Board: {state.board}. "
        
        # Get information about the betting
        betting_info = ""
        if hasattr(state, "bets") and state.bets:
            betting_info = f"Current bets: {state.bets}. "
        
        # Create a message for the current player
        message = (
            f"It's {current_agent.name}'s turn in the {game_stage} round. "
            f"Current pot: {state.pot}. "
            f"{board_info}"
            f"{betting_info}"
            f"What's your action?"
        )
        
        # Add the message to the group chat
        groupchat.messages.append({
            "role": "user",
            "content": message,
            "name": "Dealer"
        })
        
        # Get the action from the agent
        act = get_action(state, current_agent)
        
        # Let the current agent respond
        # Pass the action to the generate_reply method to ensure consistency
        response = current_agent.generate_reply(
            messages=[{"role": "user", "content": message}],
            sender=manager,
            config={"action": act}  # Pass the action in the config
        )
        
        try:
            import json
            # Try to parse as JSON first
            try:
                response_obj = json.loads(response)
                chat_message = response_obj.get("chat", response)
            except:
                # If not JSON, use the response as is
                chat_message = response
            
            # Record the chat in history
            chat_entry = f"{current_agent.name}: {chat_message}"
            chat_history.append(chat_entry)
            
            # Add the response to the group chat
            groupchat.messages.append({
                "role": "assistant",
                "content": chat_message,
                "name": current_agent.name
            })
            
            # Print the current exchange
            print(f"{current_agent.name} (to {opponent_agent.name}):\n")
            print(f"Opponent says: {chat_message}")
            print("\n" + "-" * 80 + "\n")
            
        except Exception as e:
            print(f"Error processing response: {e}")
        
        # Apply the action to get the new state
        new_state = state.apply_action(act)
        trace.append(new_state)
    
    # Print the final chat history and game trace
    print("\n=== CHAT HISTORY ===")
    for chat in chat_history:
        print(chat)
    print("\n=== GAME TRACE ===")
    print(pk.visualize_trace(trace))
    
    # Return the trace and chat history
    return {
        "trace": trace,
        "chat_history": chat_history,
        "groupchat": groupchat  # Return the groupchat for further analysis
    }

if __name__ == "__main__":
    play_hand()