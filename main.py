import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.environ['BOT_TAKEN']

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 YouTube link bhejein! Main 100MB tak download karne ki koshish karunga (Telegram limit 50MB hai).")

# Link Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Galat link! Kripya YouTube link bhejein.")
        return

    keyboard = [[
        InlineKeyboardButton("🎥 Video", callback_data=f"vid|{url}"),
        InlineKeyboardButton("🎵 Audio", callback_data=f"aud|{url}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Aap kya download karna chahte hain?", reply_markup=reply_markup)

# Button Click Handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice, url = query.data.split("|")
    m = await query.edit_message_text(text="⏳ Processing... Size check kar raha hoon.")

    try:
        # 100MB Limit Logic (Format selection)
        ydl_opts = {
            'outtmpl': 'downloaded_file.%(ext)s',
            'max_filesize': 100 * 1024 * 1024, # 100MB Limit
        }

        if choice == "vid":
            # 50MB ke andar best quality dhoondne ki koshish (Auto-compression)
            ydl_opts['format'] = 'best[filesize<50M]/bestvideo[height<=480]+bestaudio/best'
            ext = 'mp4'
        else:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            ext = 'mp3'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "aud": filename = filename.rsplit('.', 1)[0] + ".mp3"
            
            # File size check before sending
            file_size = os.path.getsize(filename) / (1024 * 1024)
            
            if file_size > 50:
                await m.edit_text(f"⚠️ File size {file_size:.1f}MB hai. Telegram 50MB se badi file allow nahi karta. Kripya choti video try karein.")
                os.remove(filename)
                return

            await m.edit_text("📤 Uploading to Telegram...")
            if choice == "vid":
                await query.message.reply_video(video=open(filename, 'rb'), caption=f"Size: {file_size:.1f}MB")
            else:
                await query.message.reply_audio(audio=open(filename, 'rb'), caption=f"Size: {file_size:.1f}MB")

        os.remove(filename)
        await m.delete()

    except Exception as e:
        await m.edit_text(f"❌ Error: File 100MB se badi ho sakti hai ya server busy hai.")
        if 'filename' in locals() and os.path.exists(filename): os.remove(filename)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
        
