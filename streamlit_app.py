import streamlit as st
import pokers as pk
import random
from src.engine import play_hand

st.title("Poker Agents with AutoGen")

# Add a seed input with a random default value
seed = st.number_input("Seed for randomization", value=random.randint(1000, 9999), step=1)

if st.button("Play Hand"):
    try:
        # Run the poker hand with the specified seed
        result = play_hand(seed=seed)
        
        # Display chat history
        st.subheader("Agent Chat")
        for chat in result["chat_history"]:
            st.text(chat)
        
        # Display game trace
        st.subheader("Game Trace")
        trace_viz = pk.visualize_trace(result["trace"])
        st.text(trace_viz)
        
        # Display final state summary if available
        if result["trace"] and len(result["trace"]) > 0:
            final_state = result["trace"][-1]
            st.subheader("Game Result")
            
            # Show winners if available
            if hasattr(final_state, 'payouts'):
                winners = [f"Player {i}" for i, payout in enumerate(final_state.payouts) if payout > 0]
                if winners:
                    st.write(f"Winner(s): {', '.join(winners)}")
                for i, payout in enumerate(final_state.payouts):
                    st.write(f"Player {i} payout: {payout}")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    if hasattr(final_state, 'payouts'):
        winners = [f"Player {i}" for i, payout in enumerate(final_state.payouts) if payout > 0]
        st.write(f"Winner(s): {', '.join(winners)}")
        for i, payout in enumerate(final_state.payouts):
            st.write(f"Player {i} payout: {payout}")
