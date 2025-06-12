from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)
from handlers.start import start
from handlers.tentang_kami import handle_tentang_kami
from handlers.profil_pondok import handle_profil_pondok

TOKEN = "7776046370:AAEZaKCCpy288MclyE9OzSBrSqVSn1Rex90"

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    application.add_handler(CallbackQueryHandler(handle_tentang_kami, pattern="^tentang$"))
    application.add_handler(CallbackQueryHandler(handle_profil_pondok, pattern="^profil_pondok$"))
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=TOKEN,
        webhook_url=f"https://bot-telegram-02rg.onrender.com/{TOKEN}",
    )

if __name__ == "__main__":
    main()
