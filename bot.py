import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

logging.basicConfig(level=logging.INFO)

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

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("🎵 Searching and downloading... Please wait.")

    search_response = youtube.search().list(
        q=query, part="snippet", maxResults=1, type="video"
    ).execute()

    if not search_response["items"]:
        await update.message.reply_text("❌ No results found.")
        return

    video = search_response["items"][0]
    video_id = video["id"]["videoId"]
    title = video["snippet"]["title"]
    url = f"https://www.youtube.com/watch?v={video_id}"

    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

    await update.message.reply_audio(audio=open(file_path, 'rb'), title=title)
    os.remove(file_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()