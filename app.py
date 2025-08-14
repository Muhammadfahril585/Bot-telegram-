from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, JobQueue, filters
)
from handlers.callbacks import handle_callback
from handlers.start import start, handle_start_callback
from handlers.admin_menu import build_admin_menu_handlers
from handlers.tentang_kami import handle_tentang_kami
from handlers.profil_pondok import handle_profil_pondok
from handlers.jadwal_sholat import jadwal_sholat_legacy_handler, callback_handler
from handlers.visi_misi import handle_visi_misi
from handlers.struktur_organisasi import handle_struktur_organisasi
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
from handlers.data_santri import build_data_santri_handler
from handlers.lihat_semua import build_lihat_semua_handler
from handlers.upload_foto import (
    upload_foto, proses_upload_nik, simpan_foto, UPLOAD_NIK, UPLOAD_FOTO
)
import os
import threading
import requests
from flask import Flask, request, Response

TOKEN = os.environ.get("BOT_TOKEN")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return 'Bot Telegram aktif.'

@flask_app.route('/ping')
def ping():
    return 'pong'


def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

def main():
    threading.Thread(target=run_flask).start()
    
    application = ApplicationBuilder().token(TOKEN).build()

    upload_foto_conv = ConversationHandler(
        entry_points=[CommandHandler("upload_foto", upload_foto)],
        states={
            UPLOAD_NIK: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_upload_nik)],
            UPLOAD_FOTO: [MessageHandler(filters.PHOTO, simpan_foto)],
        },
        fallbacks=[],
    )

    application.add_handler(upload_foto_conv)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(build_admin_menu_handlers())
    application.add_handler(build_data_santri_handler())   # /data_santri → minta password → mode/cari
    application.add_handler(build_lihat_semua_handler())
    application.add_handler(laporan_pekanan_conv)
    application.add_handler(CallbackQueryHandler(handle_tentang_kami, pattern="^tentang$"))
    application.add_handler(CallbackQueryHandler(handle_profil_pondok, pattern="^profil_pondok$"))
    application.add_handler(CallbackQueryHandler(handle_visi_misi, pattern="^visi_misi$"))
    application.add_handler(CallbackQueryHandler(handle_struktur_organisasi, pattern="^struktur$"))
    application.add_handler(CallbackQueryHandler(handle_program_pendidikan, pattern="^program_pendidikan$"))
    application.add_handler(CallbackQueryHandler(handle_psb, pattern="^psb$"))
    application.add_handler(CallbackQueryHandler(handle_start_callback, pattern="^(mode_|jadwal_shalat)"))
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
    
    for handler in rekap_bulanan_handlers
        application.add_handler(handler)
    
    application.add_handler(CommandHandler("lihat_santri", mulai_lihat_santri))
    application.add_handler(CommandHandler("jadwal", jadwal_sholat_legacy_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(CommandHandler("quran", handle_quran))
    application.add_handler(CommandHandler("pdf", handle_pdfbot))
    application.add_handler(CommandHandler("daftar_halaqah", daftar_halaqah))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_mode))
    application.add_handler(CommandHandler("mode", cek_mode))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 10000)),
        url_path=TOKEN,
        webhook_url=f"https://bot-telegram-02rg.onrender.com/{TOKEN}",
    )

if __name__ == "__main__":
    main()
