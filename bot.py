from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters, CallbackContext
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Flask app
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# YouTube Setup
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# YDL Options
YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True
}

# Message Handler
def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    chat_id = update.effective_chat.id

    context.bot.send_message(chat_id, text="🔍 Searching...")

    search_response = youtube.search().list(
        q=query, part="snippet", maxResults=1, type="video"
    ).execute()

    if not search_response["items"]:
        context.bot.send_message(chat_id, text="❌ No results found.")
        return

    video_id = search_response["items"][0]["id"]["videoId"]
    title = search_response["items"][0]["snippet"]["title"]
    url = f"https://www.youtube.com/watch?v={video_id}"

    with YoutubeDL(YDL_OPTS) as ydl:
