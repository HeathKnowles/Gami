# Gami

**Gami** is a prompt-driven AI Judge for the game **Rock-Paper-Scissors Plus (RPS+)**.

Instead of acting as a player, Gami acts as a **strict, explainable referee** that interprets free-text user inputs, enforces game rules, maintains minimal state, and produces structured, round-by-round decisions.

This project is intentionally scoped to demonstrate **prompt engineering, agent design, state modeling, and explainable reasoning with Large Language Models**, rather than building a full game engine, UI, or complex scoring system.

---

## What Gami Does

- Interprets user moves written in free text
- Classifies moves as **VALID**, **INVALID**, or **UNCLEAR**
- Enforces special rules (e.g., *bomb can only be used once*)
- Handles ambiguity safely without guessing intent
- Explains every decision in a structured JSON response
- Maintains minimal game state across rounds

Gami is powered by **Google Gemini (free tier)** and relies primarily on **prompt instructions**, not hardcoded logic.

---

## Main Judge Prompt

The core logic of Gami lives in the judge prompt:

-> **[JUDGE PROMPT](judge_prompt.txt)**

This prompt defines:
- Game rules
- Adjudication steps
- Edge-case handling
- Output schema
- Explainability requirements

The Python code serves only as orchestration glue.

---

## Problem Framing: LLM as a Judge

Traditional Rock-Paper-Scissors logic can be implemented with simple conditionals.  
However, this assignment introduces **free-text user input**, which requires:

- Intent interpretation  
- Ambiguity handling  
- Rule enforcement under uncertainty  

This makes the problem well-suited for an **LLM-as-a-Judge** architecture, where the model acts as a referee rather than a conversational agent or player.

The judge must:
1. Interpret what the user *intended*
2. Decide whether the move is valid under the rules
3. Apply game logic consistently
4. Explain the decision clearly

---

## Architecture Overview

The system is intentionally minimal and cleanly separated.

### 1. Intent Understanding (LLM via Prompt)
- Maps free-text input to one of:
  - `rock`, `paper`, `scissors`, `bomb`
- Handles:
  - Case variation
  - Synonyms
  - Ambiguous or non-game text
- Defaults to **UNCLEAR** when intent is not unambiguous

### 2. Game Logic (LLM via Prompt)
- Applies rules strictly:
  - Bomb beats everything
  - Bomb usable only once by the user
  - Bomb vs bomb → draw
  - Invalid or unclear moves waste the turn
- Uses **explicit state injected into the prompt**

### 3. Response Generation (LLM → JSON)
- Produces structured, machine-readable output
- Includes:
  - Round number
  - Moves played
  - Round winner
  - Explanation
  - Updated state

### 4. Glue Code (Python)
- Responsible only for:
  - Passing state into the prompt
  - Parsing JSON
  - Updating minimal state (round, bomb usage, score)
- Contains **no game logic**

This ensures that **decision-making is driven by the prompt**, not the code.

---

## Prompt Design and Research Rationale

### Structured Prompt Sections

The judge prompt is divided into explicit sections:
- Game Rules
- Inputs
- Adjudication Process
- Edge Cases
- Output Format

This structure reduces instruction bleed and improves rule adherence.  
Empirically, Gemini follows **sectioned, rubric-like prompts** more reliably than unstructured instructions, especially in stateful tasks.

---

### Reasoning Before Verdict (Within JSON)

The output schema places the `reasoning` field **before** decision fields such as `interpreted_intent` and `round_winner`.

This is based on research showing that **token generation order impacts logical accuracy** in autoregressive models.  
By forcing the model to articulate reasoning first, premature or superficial verdicts are reduced—without exposing hidden chain-of-thought.

---

### Abstention Bias for Ambiguity

The prompt explicitly instructs:

> *When in doubt, choose UNCLEAR over guessing.*

This is a deliberate hallucination-mitigation strategy.  
In adjudication systems, **false certainty is worse than abstention**, particularly when enforcing strict rules.

---

### State Injection Instead of Memory

Gemini is stateless by default.  
To ensure correctness, all relevant state (e.g., whether the user has already used `bomb`) is **explicitly passed into every prompt**.

This avoids:
- Hidden assumptions
- Drift across rounds
- Inconsistent explanations

---

## Gemini-Specific Considerations

Gemini performs well in this setting due to:
- Strong instruction-following behavior
- Reliable structured output when constrained
- Solid handling of short logical rules combined with natural language input

The model is treated strictly as:
- A **deterministic judge**
- Not a conversational assistant
- Not a creative agent

All role enforcement happens inside the prompt.

---

## State Modeling

Minimal state is maintained outside the model:
- `round_number`
- `user_bomb_used`
- `user_score`
- `bot_score`

The judge:
- Reads state from the prompt
- Decides whether state should change
- Returns explicit state updates in JSON

This keeps state handling transparent and auditable.

---

## Edge Cases Considered

The prompt explicitly handles:
- Empty input → UNCLEAR
- Multiple moves mentioned → UNCLEAR
- Non-game text → INVALID
- Bomb reuse → INVALID
- Ambiguous slang or emojis → UNCLEAR

Invalid or unclear moves **waste the turn**, resulting in an automatic bot win, as specified.

---

## Conclusion

Gami demonstrates how careful prompt architecture can transform a Large Language Model into a **reliable, explainable, state-aware judge**.

By aligning instruction structure, output ordering, and state handling with known LLM reasoning behaviors—particularly Gemini’s strengths—the system achieves deterministic adjudication without complex code.

The key takeaway is that **prompt design, not tooling, is the primary driver of correctness and reliability in LLM-based judges**.
