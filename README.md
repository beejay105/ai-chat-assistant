# AI Chat Assistant

A simple Python-based AI chat assistant using the Hugging Face API for free AI text generation.

## Features

- Free AI text generation using Hugging Face's models
- Content moderation for both input and output
- Simple and easy-to-use interface
- No API key required (uses demo key)
- Built-in content filtering

## Setup Instructions

1. **Install Required Packages**

   ```bash
   pip install requests python-dotenv
   ```

2. **Configure Environment Variables**

   - Copy the `.env.example` file to `.env`
   - Edit the `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```
   - You can get your API key from: https://platform.openai.com/api-keys

3. **Customize Settings (Optional)**
   In the `.env` file, you can customize:
   - `AI_MODEL`: Choose between "gpt-3.5-turbo" or "gpt-4" (if you have access)
   - `BANNED_KEYWORDS`: Add or remove keywords for content moderation

## Usage

Run the script:

```bash
python app.py
```

The script will:

1. Prompt you for input
2. Check for banned content
3. Send safe requests to the AI
4. Moderate the AI's response
5. Display the result

## Features

- Input content moderation
- Output content moderation
- Configurable banned keywords
- Error handling for API issues
- Environment-based configuration
- Support for different AI models

## Security Notes

- Never commit your `.env` file to version control
- Regularly update your banned keywords list
- Monitor API usage to control costs
- Keep your API key secure
