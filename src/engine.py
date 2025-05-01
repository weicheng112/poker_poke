import pokers as pk
# from solver_tool import get_action   # <- we stub this next
# from player import PlayerAgent       # <- AutoGen wrapper
from src.solver_tool import get_action
from src.player import PlayerAgent

def play_hand():
    state = pk.State.from_seed(n_players=2, button=0, sb=5, bb=10, stake=1000, seed=1234)
    agents = [PlayerAgent("P0"), PlayerAgent("P1")]
    trace = [state]

    while not trace[-1].final_state:
        state = trace[-1]  
        p = state.current_player
        act = get_action(state, agents[p])     # ask the agent for a move
        new_state = state.apply_action(act)
        trace.append(new_state)                # add to the history
    
    print(pk.visualize_trace(trace))
    return trace

if __name__ == "__main__":
    play_hand()