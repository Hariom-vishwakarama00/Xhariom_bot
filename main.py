import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.environ['BOT_TAKEN']

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 YouTube link bhejein aur chunein ki aapko kya download karna hai!")

# Link Handler (Buttons dikhane ke liye)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ Galat link! Kripya YouTube link bhejein.")
        return

    # Buttons create karna
    keyboard = [
        [
            InlineKeyboardButton("🎥 Video (MP4)", callback_data=f"vid|{url}"),
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"aud|{url}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Aap kya download karna chahte hain?", reply_markup=reply_markup)

# Button Click Handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice, url = query.data.split("|")
    await query.edit_message_text(text="⏳ Processing... Please wait.")

    try:
                if choice == "vid":
            ydl_opts = {
                # Sabse best format dhoondo jo 50MB se chota ho
                'format': 'best[filesize<500M]/bestvideo[height<=480]+bestaudio/best[height<=480]/worst',
                'outtmpl': 'downloaded_file.mp4',
                'merge_output_format': 'mp4',
            }
            file_name = 'downloaded_file.mp4'
            is_video = True
    

        # File bhejna
        if is_video:
            await query.message.reply_video(video=open(file_name, 'rb'))
        else:
            await query.message.reply_audio(audio=open(file_name, 'rb'))

        os.remove(file_name)
        await query.delete_message()

    except Exception as e:
        await query.edit_message_text(text=f"❌ Error: File size bahut badi ho sakti hai.")
        if os.path.exists(file_name): os.remove(file_name)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
      
