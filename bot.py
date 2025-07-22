import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build

# Telegram Bot Token
TOKEN = os.getenv("BOT_TOKEN")

# YouTube API setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Flask app to keep Render alive (optional if needed for webhook)
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

# YouTube downloader options
YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'noplaylist': True,
}

# YouTube search function
def search_youtube(query):
    request = youtube.search().list(
        part='snippet',
        maxResults=1,
        q=query
    )
    response = request.execute()
    video_id = response['items'][0]['id']['videoId']
    title = response['items'][0]['snippet']['title']
    return f'https://www.youtube.com/watch?v={video_id}', title

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /play song name to download audio from YouTube!")

# Command handler: /play <song name>
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Please provide a song name. Example: /play faded")
        return

    url, title = search_youtube(query)
    chat_id = update.effective_chat.id

    await update.message.reply_text(f"Downloading **{title}**...")

    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

        await context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), title=title)
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Main function
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
