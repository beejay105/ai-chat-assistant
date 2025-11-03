import os
import sys
import json
import app.py

# ---- Configuration ----
# Load banned keywords from environment variable or use defaults
default_keywords = "kill,hack,bomb"
env_keywords = os.getenv('BANNED_KEYWORDS', default_keywords)
BANNED_KEYWORDS = {kw.strip() for kw in env_keywords.split(',')}

# System prompt that guides the AI's behavior.
SYSTEM_PROMPT = (
    "You are a helpful, safety-first assistant. Provide clear, concise, and polite answers. "
    "If a user asks for anything illegal, dangerous, or privacy-invading, refuse and provide a "
    "safe alternative.\n"
)

# API configuration for OpenAI
AI_API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")  # Get your API key from: https://platform.openai.com/api-keys
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")

# HTTP headers for API calls
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
}


# ---- Moderation helpers ----
def contains_banned(text: str) -> bool:
    """Return True if text contains any banned keyword (case-insensitive)."""
    if not text:
        return False
    lower = text.lower()
    for kw in BANNED_KEYWORDS:
        if kw in lower:
            return True
    return False


def redact_banned(text: str) -> str:
    """Replace occurrences of banned keywords with [REDACTED], preserving case roughly."""
    if not text:
        return text
    out = text
    for kw in BANNED_KEYWORDS:
        # simple case-insensitive replacement
        out = _case_insensitive_replace(out, kw, "[REDACTED]")
    return out


def _case_insensitive_replace(text: str, old: str, new: str) -> str:
    """Helper: case-insensitive replace of substring 'old' with 'new'."""
    import re

    pattern = re.compile(re.escape(old), re.IGNORECASE)
    return pattern.sub(new, text)


# ---- AI API interaction ----
def call_text_generation_api(system_prompt: str, user_prompt: str, max_tokens: int = 512) -> dict:
    """
    Calls the OpenAI ChatGPT API endpoint.

    Returns the parsed JSON response as a dict.
    """
    if not API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set. Set it to your OpenAI API key.")

    payload = {
        "model": "gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    resp = requests.post(AI_API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ---- Main flow ----
def main():
    try:
        # Collect user prompt (simple CLI input; could be replaced by web form / API)
        print("Enter your prompt (single line). Press Ctrl-D / Ctrl-Z to finish:")
        user_prompt = sys.stdin.read().strip()
        if not user_prompt:
            print("No prompt provided. Exiting.")
            return

        # Input moderation: block if banned keywords found
        if contains_banned(user_prompt):
            print("Your input violated the moderation policy.")
            return

        # Call AI API
        try:
            api_response = call_text_generation_api(SYSTEM_PROMPT, user_prompt)
        except requests.HTTPError as e:
            print(f"AI API request failed: {e} (status {getattr(e.response, 'status_code', 'unknown')})")
            return
        except Exception as e:
            print("Error while calling AI API:", str(e))
            return

        # Parse OpenAI API response
        # Response format: {"choices": [{"message": {"content": "AI response here"}}]}
        ai_text = None
        if isinstance(api_response, dict) and "choices" in api_response:
            if api_response["choices"] and "message" in api_response["choices"][0]:
                ai_text = api_response["choices"][0]["message"]["content"]

        if ai_text is None:
            # Fallback: stringify response
            ai_text = json.dumps(api_response, ensure_ascii=False, indent=2)

        # Output moderation: if banned keywords are present, redact them
        if contains_banned(ai_text):
            redacted = redact_banned(ai_text)
            # If you prefer to block instead of redact, you could print violation message and exit.
            # For this script, we redact and display. If you want blocking behavior, replace the next line.
            print("\n--- Moderated AI response (some content redacted) ---\n")
            print(redacted)
        else:
            print("\n--- AI response ---\n")
            print(ai_text)

    except KeyboardInterrupt:
        print("\nCancelled by user.")


if __name__ == "__main__":
    main()