import pokers as pk
# from solver_tool import get_action   # <- we stub this next
# from player import PlayerAgent       # <- AutoGen wrapper
from src.solver_tool import get_action
from src.player import PlayerAgent

def play_hand(seed=1234):
    state = pk.State.from_seed(n_players=2, button=0, sb=5, bb=10, stake=1000, seed=seed)
    agents = [PlayerAgent("P0"), PlayerAgent("P1")]
    trace = [state]
    chat_history = []

    while not trace[-1].final_state:
        state = trace[-1]
        p = state.current_player
        current_agent = agents[p]
        opponent_agent = agents[1-p]  # The other player
        
        # Update the agent's blackboard with the current state
        current_agent.blackboard["state"] = state
        
        # Get the action from the agent
        act = get_action(state, current_agent)
        
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
        
        # Generate a message from the current agent with more context
        message = {
            "role": "user",
            "content": (
                f"It's your turn in the {game_stage} round. "
                f"Current pot: {state.pot}. "
                f"{board_info}"
                f"{betting_info}"
                f"What's your action?"
            )
        }
        
        # Send the message to the agent and get a response
        response = current_agent.generate_reply([message], sender=opponent_agent, config=None)
        
        try:
            import json
            response_obj = json.loads(response)
            chat_message = response_obj.get("chat", "")
            
            # Record the chat in history
            chat_history.append(f"{current_agent.name}: {chat_message}")
            
            # Send the chat to the opponent
            if chat_message:
                opponent_message = {
                    "role": "user",
                    "content": f"Opponent says: {chat_message}"
                }
                opponent_agent.receive(opponent_message, sender=current_agent)
        except:
            # If there's an error parsing the response, just continue
            pass
        
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
        "chat_history": chat_history
    }

if __name__ == "__main__":
    play_hand()