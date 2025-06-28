from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext

# Replace with your bot token
BOT_TOKEN = "7687456631:AAEFC7gsM4XKmREugWbsWlUJD0MvO3JMy5g"
# Replace with the link to your Flask app (public EC2 IP or domain)
VIDEO_APP_LINK = "https://t.me/stream_one_bot/StreamOne"

async def start(update: Update, context: CallbackContext):
    # Send a message with a button linking to the video streaming app
    keyboard = [[InlineKeyboardButton("Watch Movie", url=VIDEO_APP_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the button below to stream the video:", reply_markup=reply_markup)

def main():
    # Create the Application and pass your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
