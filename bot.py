#!/usr/bin/env python3
import os
import asyncio
import base64
import tempfile
from pathlib import Path

import openai
import requests
from moviepy.editor import ImageClip

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Bot name (for display)
BOT_NAME = "Sehirli video ysash"

# --- Konfiguratsiya ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("TELEGRAM_BOT_TOKEN va OPENAI_API_KEY atrof-muhit o'zgaruvchilari kerak.")

openai.api_key = OPENAI_API_KEY

# --- Yordamchi funksiyalar ---
async def create_image_from_prompt(prompt: str) -> str:
    """
    OpenAI Images API orqali rasm yaratadi va PNG fayl path qaytaradi.
    """
    def call_openai():
        return openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )
    resp = await asyncio.to_thread(call_openai)
    b64 = resp["data"][0]["b64_json"]
    data = base64.b64decode(b64)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(data)
    tmp.close()
    return tmp.name

async def make_video_from_image(image_path: str, duration: float = 4.0) -> str:
    """
    Bir rasmdan MP4 video yaratadi (moviepy + ffmpeg kerak).
    """
    out_path = str(Path(tempfile.gettempdir()) / f"out_{Path(image_path).stem}.mp4")
    def render():
        clip = ImageClip(image_path).set_duration(duration)
        clip.write_videofile(out_path, fps=24, codec="libx264", audio=False, verbose=False, logger=None)
        clip.close()
    await asyncio.to_thread(render)
    return out_path

# --- Telegram handlerlar ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Salom! Men {BOT_NAME}. Rasm uchun prompt yozing yoki /image <prompt> va /video <prompt> ni ishlating.")

async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args) if context.args else "A beautiful scenic landscape"
    msg = await update.message.reply_text("Rasm yaratilmoqda... Iltimos kuting.")
    image_path = None
    try:
        image_path = await create_image_from_prompt(prompt)
        await update.message.reply_photo(photo=open(image_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")
    finally:
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
        await msg.delete()

async def video_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args) if context.args else "A beautiful scenic landscape"
    msg = await update.message.reply_text("Rasm va video yaratilmoqda... Bu biroz vaqt olishi mumkin.")
    image_path = None
    video_path = None
    try:
        image_path = await create_image_from_prompt(prompt)
        video_path = await make_video_from_image(image_path, duration=4.0)
        await update.message.reply_video(video=open(video_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")
    finally:
        for p in (image_path, video_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        await msg.delete()

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # oddiy matnni rasm yaratish uchun prompt sifatida ishlatamiz
    prompt = update.message.text
    await update.message.reply_text("Rasm yaratilmoqda...")
    image_path = None
    try:
        image_path = await create_image_from_prompt(prompt)
        await update.message.reply_photo(photo=open(image_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")
    finally:
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass

# --- App yaratilishi va ishga tushishi ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("image", image_cmd))
    app.add_handler(CommandHandler("video", video_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
