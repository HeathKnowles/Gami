from google import genai
from google.genai import types
from dotenv import dotenv_values
import json
import random

config = dotenv_values(".env")

client = genai.Client(api_key=config.get("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3-flash-preview"

state = {
    "round": 1,
    "user_bomb_used": False,
    "user_score": 0,
    "bot_score": 0
}

with open("judge_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()


def judge_move(user_input: str):
    bot_move = random.choice([
        "rock",
        "paper",
        "scissors",
        "bomb"
    ])

    contents = [
       types.Content(role="system",
                    parts=types.Part.from_text(SYSTEM_PROMPT)),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    f"""
Round Number: {state['round']}
User bomb already used: {state['user_bomb_used']}
Bot move: {bot_move}

User input:
\"{user_input}\"
"""
                )
            ],
        ),
   ]
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents
    )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        raise ValueError("Model didn't return valid JSON")


    if result.get("bomb_consumed"):
        state["user_bomb_used"] = True
    
    if result.get("round_winner") == "user":
        state["user_score"] += 1
    elif result.get("round_winner") == "bot":
        state["bot_score"] += 1
    
    state["round"] += 1

    return result



def main():
    print("Rock-Paper-Scissors Plus - AI Judge (type 'quit' to exit)\n")

    while True:
        user_input = input("Your move: ").strip()
        if user_input.lower() == "quit":
            break

        result = judge_move(user_input)

        print("\n-----ROUND RESULT-----")
        print(json.dumps(result, indent=2))
        print("----------------------\n")
    
    print("Final Score: ")
    print(f"User: {state['user_score']} | Bot: {state['bot_score']}")


if __name__ == "__main__":
    main()
