import streamlit as st, subprocess, json, pokers as pk
from src.engine import play_hand, pk

if st.button("Play hand"):
    trace = play_hand()      # modify engine.play_hand to return full trace
    st.text(pk.visualize_trace(trace))
