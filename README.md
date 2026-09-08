# Sehirli video ysash — Telegram bot integration with OpenAI

This repository contains a Telegram bot "Sehirli video ysash" that generates images using the OpenAI Images API and can turn them into short videos.

Setup

1. Create repository secrets (or environment variables) for the bot tokens:
   - TELEGRAM_BOT_TOKEN — your Telegram Bot token from BotFather
   - OPENAI_API_KEY — your OpenAI API key

2. Install dependencies (recommended inside a virtualenv):

pip install python-telegram-bot==20.3 openai moviepy python-dotenv requests

3. Ensure ffmpeg is installed on the host (required by moviepy):

Ubuntu/Debian:

sudo apt update && sudo apt install -y ffmpeg

macOS (Homebrew):

brew install ffmpeg

4. Run the bot:

export TELEGRAM_BOT_TOKEN="<your-telegram-bot-token>"
export OPENAI_API_KEY="<your-openai-api-key>"
python bot.py

Usage

- Send a plain text message: the bot will generate an image from the text and reply with the image.
- /image <prompt> — explicitly generate an image from <prompt>.
- /video <prompt> — generate an image from <prompt> and return a short MP4 video made from that image.

Notes

- Do NOT commit your API keys to the repository. Use GitHub Secrets or environment variables.
- The bot saves temporary files in the system temp directory and deletes them after sending. Monitor disk usage if you use this at scale.
- OpenAI API usage incurs cost. Monitor your usage in the OpenAI dashboard.
