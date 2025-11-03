import sys
import json
import urllib.request
import urllib.parse
import urllib.error

# ---- Configuration ----
# Simple list of banned keywords
BANNED_KEYWORDS = {"kill", "hack", "bomb", "exploit", "steal", "attack"}

# API Configuration
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
# Users should set their own API key in environment variables
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your API key

# Message that guides the AI's behavior
PROMPT_PREFIX = "You are a helpful assistant. Please provide a friendly and informative response: "

def contains_banned(text):
    """Check if text contains any banned keywords."""
    if not text:
        return False
    text = text.lower()
    return any(word in text for word in BANNED_KEYWORDS)

def chat_with_ai(prompt):
    """Send a message to the AI model and get the response."""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare the input with our guiding prefix
        full_prompt = PROMPT_PREFIX + prompt
        
        data = {
            "inputs": full_prompt,
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(data).encode(),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode())
            if isinstance(result, list) and len(result) > 0:
                # Extract the generated text from the response
                return result[0].get('generated_text', '')
            return None
            
    except urllib.error.HTTPError as e:
        if e.code == 503:
            print("The model is loading, please try again in a few seconds...")
        else:
            print(f"API Error: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    print("AI Chat Assistant (Press Ctrl+C to exit)")
    print("---------------------------------------")
    
    print("\nExample questions you can ask:")
    print("1. What's your favorite color?")
    print("2. Tell me about yourself")
    print("3. What do you like to do for fun?")
    
    try:
        while True:
            # Get user input
            prompt = input("\nYou: ").strip()
            if not prompt:
                continue
            
            # Check input for banned content
            if contains_banned(prompt):
                print("Sorry, your message contains inappropriate content.")
                continue
            
            print("\nAI is thinking...")
            
            # Get AI response
            response = chat_with_ai(prompt)
            
            if response:
                # Check response for banned content
                if contains_banned(response):
                    print ("The AI response was filtered due to inappropriate content.")
                else:
                    print ("\nAI:", response)
            else:
                print ("Sorry, I couldn't get a response. Please try again in a few seconds.")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()