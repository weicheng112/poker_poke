# poker_poke

```
┌────────────────────────────────────────────────── Dealer / UI ──────────────────────────────────────────────────┐
│  • Keeps official game state (pots, stacks, board)                                                             │
│  • Sends **public** state to the seat whose turn it is                                                         │
│  • Receives a strict JSON action + chat line                                                                   │
└───────────────────────────────▲─────────────────────────────────────────────────────────────────────────────────┘
                                │   public state
                                │
                                ▼
                    ┌───────────────────────────── LLM wrapper (“PlayerAgent”) ───────────────────────────────┐
                    │  • AutoGen agent that owns private memory slots (hole cards, stack, logger stats)       │
                    │  • Calls the **Solver Core** tool with *only* the info it needs                         │
                    │  • Gets back a probability vector, samples an action,                                   │
                    │    → returns `{action, amount, chat}` JSON to Dealer                                    │
                    │                                                                                         │
                    │                                                                                         │
                    └───────────────▲──────────────────────▲───────────────────────────────────────────────────┘
                                    │chat                  │  JSON action
                                    │                      │
                                    │    query (private cards, board, stacks …)
                                    ▼                      │
                       ┌────────────────────────── Solver Core (CFR+, NN, TexasSolver) ─────────────────────────┐
                       │                                                                                       │
                       │  Input  → current sub-game description                                                │
                       │  Output → probability vector: {fold: 0.22, call: 0.38, raise 75: 0.40}                │
                       └────────────────────────────────────────────────────────────────────────────────────────┘

```
