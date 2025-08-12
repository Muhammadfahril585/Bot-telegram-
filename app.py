from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, JobQueue, filters
)
from handlers.callbacks import handle_callback
from handlers.start import start
from handlers.tentang_kami import handle_tentang_kami
from handlers.profil_pondok import handle_profil_pondok
from handlers.jadwal_sholat import jadwal_sholat_legacy_handler, callback_handler
from handlers.visi_misi import handle_visi_misi
from handlers.struktur_organisasi import handle_struktur_organisasi
from handlers.lihat_semua import lihat_semua
from handlers.program_pendidikan import handle_program_pendidikan
from handlers.psb import handle_psb
from handlers.pdfbot import handle_pdfbot
from handlers.quran import handle_quran
from handlers.rekap_bulanan import handle_buat_pdf_rekap
from handlers.unduh import handle_unduh
from handlers.portal import handle_portal
from handlers.daftar_halaqah import daftar_halaqah
from handlers.galeri import handle_galeri
from handlers.rekap_bulanan import rekap_bulanan_handlers
from handlers.ai_handler import handle_ai_mode, handle_pertanyaan_callback
from handlers.start import cek_mode
from handlers.layanan import handle_layanan
from handlers.lapor_pekanan2 import laporan_pekanan_conv
from handlers.lapor_pekanan2 import handle_reset_callback
from handlers.lihat_santri import mulai_lihat_santri, detail_santri
from handlers.start import set_mode
from handlers.data_santri import (
    data_santri, pilih_mode, proses_cari_nik,
    navigasi_callback, tampilkan_detail_callback,
    PILIH_MODE, CARI_NIK
)
from handlers.upload_foto import (
    upload_foto, proses_upload_nik, simpan_foto, UPLOAD_NIK, UPLOAD_FOTO
)
import os
import threading
import requests
import time
import asyncio
import logging
from flask import Flask, request, Response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
flask_app = Flask(__name__)

# Global application instance
application = None

@flask_app.route('/')
def home():
    return 'Bot Telegram aktif.'

@flask_app.route('/ping')
def ping():
    return 'pong'

@flask_app.route('/debug')
def debug():
    return {
        'app_ready': application is not None,
        'token_set': TOKEN is not None,
        'status': 'debug endpoint working'
    }

# ✅ Fixed webhook endpoint
@flask_app.route(f'/{TOKEN}', methods=['POST'])
def telegram_webhook():
    """Handle incoming Telegram updates via webhook"""
    try:
        logger.info("=== Webhook received ===")
        
        if application is None:
            logger.error("Application not ready!")
            return 'Application not ready', 500
            
        json_data = request.get_json()
        if not json_data:
            logger.warning("No JSON data")
            return 'OK'
            
        logger.info(f"Processing update: {json_data.get('update_id', 'unknown')}")
        
        # Create update object
        update = Update.de_json(json_data, application.bot)
        
        # Process update with proper async handling
        def process_update():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(application.process_update(update))
                logger.info("✅ Update processed successfully")
            except Exception as e:
                logger.error(f"❌ Processing error: {e}")
            finally:
                loop.close()
        
        # Run in background thread to avoid blocking
        threading.Thread(target=process_update, daemon=True).start()
        
        return 'OK'
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return 'OK'  # Always return OK to avoid webhook retries

def create_application():
    """Create and configure the Telegram application"""
    global application
    logger.info("Creating application...")
    application = ApplicationBuilder().token(TOKEN).build()

    # Data santri conversation handler
    data_santri_conv = ConversationHandler(
        entry_points=[CommandHandler("data_santri", data_santri)],
        states={
            PILIH_MODE: [
                CallbackQueryHandler(pilih_mode, pattern="^mode\\|"),
                CallbackQueryHandler(navigasi_callback, pattern="^navi\\|"),
                CallbackQueryHandler(tampilkan_detail_callback, pattern="^lihat\\|"),
            ],
            CARI_NIK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, proses_cari_nik),
            ],
        },
        fallbacks=[],
        per_chat=True
    )

    # Upload foto conversation handler
    upload_foto_conv = ConversationHandler(
        entry_points=[CommandHandler("upload_foto", upload_foto)],
        states={
            UPLOAD_NIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_upload_nik)],
            UPLOAD_FOTO: [MessageHandler(filters.PHOTO, simpan_foto)],
        },
        fallbacks=[],
    )

    # Add all handlers
    logger.info("Adding handlers...")
    application.add_handler(upload_foto_conv)
    application.add_handler(data_santri_conv)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_tentang_kami, pattern="^tentang$"))
    application.add_handler(CallbackQueryHandler(handle_profil_pondok, pattern="^profil_pondok$"))
    application.add_handler(CallbackQueryHandler(handle_visi_misi, pattern="^visi_misi$"))
    application.add_handler(CallbackQueryHandler(handle_struktur_organisasi, pattern="^struktur$"))
    application.add_handler(CallbackQueryHandler(handle_program_pendidikan, pattern="^program_pendidikan$"))
    application.add_handler(CallbackQueryHandler(handle_psb, pattern="^psb$"))
    application.add_handler(CallbackQueryHandler(set_mode, pattern="^mode_"))
    application.add_handler(CallbackQueryHandler(handle_unduh, pattern="^unduh$"))
    application.add_handler(CallbackQueryHandler(handle_galeri, pattern="^galeri$"))
    application.add_handler(CallbackQueryHandler(handle_layanan, pattern="^layanan$"))
    application.add_handler(CallbackQueryHandler(handle_portal, pattern="^portal$"))
    application.add_handler(CallbackQueryHandler(daftar_halaqah, pattern="^daftar_halaqah$"))
    application.add_handler(CallbackQueryHandler(mulai_lihat_santri, pattern="^lihat_santri$"))
    application.add_handler(CallbackQueryHandler(detail_santri, pattern=r"^lihat_santri:\d+$"))
    application.add_handler(CallbackQueryHandler(handle_reset_callback, pattern="^reset_"))
    application.add_handler(CallbackQueryHandler(handle_buat_pdf_rekap, pattern="^buat_pdf_rekap$"))
    application.add_handler(CallbackQueryHandler(handle_pertanyaan_callback, pattern="^pertanyaan_"))
    
    for handler in rekap_bulanan_handlers:
        application.add_handler(handler)
    
    application.add_handler(laporan_pekanan_conv)
    application.add_handler(CommandHandler("lihat_santri", mulai_lihat_santri))
    application.add_handler(CommandHandler("jadwal", jadwal_sholat_legacy_handler))
    
    # ✅ Fixed: Add specific patterns to avoid conflicts
    application.add_handler(CallbackQueryHandler(callback_handler, pattern="^jadwal_"))
    
    application.add_handler(CommandHandler("quran", handle_quran))
    application.add_handler(CommandHandler("pdf", handle_pdfbot))
    application.add_handler(CommandHandler("lihat_semua", lihat_semua))
    application.add_handler(CommandHandler("daftar_halaqah", daftar_halaqah))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_mode))
    application.add_handler(CommandHandler("mode", cek_mode))
    
    # ✅ Keep general callback handler last
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("All handlers added")

async def setup_bot():
    """Setup bot with proper async handling"""
    try:
        logger.info("Initializing bot...")
        await application.initialize()
        await application.start()
        
        webhook_url = f"https://bot-telegram-02rg.onrender.com/{TOKEN}"
        await application.bot.set_webhook(webhook_url)
        
        logger.info(f"✅ Webhook set to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot setup error: {e}")
        return False

def main():
    """Main function to run the application"""
    logger.info("=== Starting Bot Application ===")
    
    # Create application first
    create_application()
    
    # Setup bot in background
    def setup_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(setup_bot())
        if success:
            logger.info("✅ Bot setup completed")
        else:
            logger.error("❌ Bot setup failed")
        loop.close()
    
    setup_thread = threading.Thread(target=setup_async, daemon=True)
    setup_thread.start()
    
    # Wait for setup to complete
    time.sleep(2)
    
    # Run Flask app
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting Flask server on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
