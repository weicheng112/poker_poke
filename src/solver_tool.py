import random
import pokers as pk


def random_valid_action(state):
    """Return a legal pokers action dict, e.g. {'type':'check'}."""
    legals = state.legal_actions
    enum_action = random.choice(legals)
    return pk.Action(enum_action)

def get_action(state, agent=None):
    """MVP glue.  Later we’ll call a real solver; for now just pick random."""
    return random_valid_action(state)
