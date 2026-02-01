
# Gami

**Gami** is a prompt-driven AI Judge for **Rock-Paper-Scissors Plus (RPS+)**.

The system evaluates free-text user inputs, enforces game rules, maintains minimal state, and produces structured, explainable decisions on a round-by-round basis.  
The focus is on **prompt design, agent reasoning, state handling, and explainability**, not on building a full game engine or UI.

---

## What the System Does

- Interprets user moves written in free text
- Classifies moves as **VALID**, **INVALID**, or **UNCLEAR**
- Enforces constraints (e.g., bomb can only be used once)
- Handles ambiguity conservatively without guessing intent
- Produces structured JSON output with clear explanations
- Maintains minimal state across rounds

The system uses **Google Gemini (free tier)** and relies on **prompt-driven decision-making**, not hardcoded game logic.

---

## Core Judge Prompt

The primary logic lives in the judge prompt:

→ **[judge_prompt.txt](judge_prompt.txt)**

The prompt defines:
- Game rules
- Intent interpretation criteria
- Rule application logic
- Edge-case handling
- Output schema and explainability requirements

The Python code only orchestrates input, state injection, and output parsing.

---

## Design Approach

### LLM as a Judge

Because user input is free text, the system treats the LLM as a **judge**, not a player.  
The model is responsible for:
1. Interpreting intent
2. Validating the move
3. Applying rules
4. Explaining the outcome

This approach prioritizes correctness and clarity over creative generation.

---

## Architecture Overview

The design enforces clear separation of concerns:

### Intent Understanding (LLM)
- Maps free-text input to one of: `rock`, `paper`, `scissors`, `bomb`
- Handles case variation, synonyms, and ambiguity
- Defaults to **UNCLEAR** when intent is not unambiguous

### Game Logic (LLM)
- Applies rules strictly:
  - Bomb beats everything
  - Bomb usable only once by the user
  - Bomb vs bomb → draw
  - Invalid or unclear moves waste the turn
- Uses explicit state injected into each prompt

### Response Generation (LLM)
- Produces deterministic, structured JSON output
- Includes round number, moves played, winner, reasoning, and state updates

### Glue Code (Python)
- Passes state into the prompt
- Parses JSON output
- Updates minimal state (round number, bomb usage, score)
- Contains no game logic

---

## Prompt Design Decisions

- **Structured sections** (rules, process, output) reduce instruction ambiguity and rule drift.
- **Reasoning appears before verdict fields** in the JSON schema to improve logical consistency in autoregressive generation.
- **Abstention bias** is enforced: when intent is unclear, the model must choose `UNCLEAR` instead of guessing.
- **State is injected explicitly** every round to avoid hidden memory or drift.

These choices align with observed reasoning behavior of Gemini in constrained, stateful tasks.

---

## State Modeling

Only minimal state is tracked externally:
- `round_number`
- `user_bomb_used`
- `user_score`
- `bot_score`

The judge reads state from the prompt and explicitly returns state updates, keeping behavior transparent and auditable.

---

## Edge Cases Handled

- Empty input → UNCLEAR
- Multiple moves in one input → UNCLEAR
- Non-game text → INVALID
- Bomb reuse → INVALID
- Ambiguous slang or emojis → UNCLEAR

Invalid or unclear moves waste the turn, resulting in a bot win as specified by the rules.

---

## Summary

Gami demonstrates how careful prompt architecture can turn an LLM into a **deterministic, explainable, state-aware judge**.

The key takeaway is that **prompt structure and constraints**, rather than complex code or tooling, are the primary drivers of correctness and reliability in LLM-based adjudication systems.