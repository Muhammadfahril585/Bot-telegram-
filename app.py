from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)
from handlers.callbacks import handle_callback
from handlers.start import start
from handlers.tentang_kami import handle_tentang_kami
from handlers.profil_pondok import handle_profil_pondok
from handlers.visi_misi import handle_visi_misi   
from handlers.struktur_organisasi import handle_struktur_organisasi
from handlers.program_pendidikan import handle_program_pendidikan
from handlers.psb import handle_psb
from handlers.unduh import handle_unduh
from handlers.galeri import handle_galeri
from handlers.layanan import handle_layanan
from handlers.portal import handle_portal
from handlers.daftar_halaqah import daftar_halaqah
from handlers.lihat_santri import mulai_lihat_santri, handle_pilihan, tampilkan_santri_halaqah, PILIH_HALAQAH, TAMPIL_HALAQAH
from handlers.tambah_santri import tambah_santri_handler
from handlers.data_santri import detail_santri_handler
from handlers.pendidikan import pendidikan_conv
from handlers.kelas import kelas_handler
from handlers.wali import wali_conv
from handlers.tampilkan_data import lihat_data_handler
from handlers.tampilkan_data import proses_nama
from handlers.tampilkan_data import callback_nama
from handlers.tampilkan_data import callback_lanjut_nama
from handlers.angkatan import angkatan_handler
from handlers.edit_hafalan import edit_hafalan_handler
from handlers.edit_data import get_handler as get_edit_handler
from handlers.edit_data_santri import get_edit_data_santri_handler
from handlers.edit_pendidikan_santri import get_edit_pendidikan_santri_handler
from handlers.edit_wali_santri import get_edit_wali_santri_handler
from handlers.edit_kelas_santri import get_edit_kelas_santri_handler
from handlers.edit_angkatan_santri import get_edit_angkatan_santri_handler
from handlers.tandai_alumni import tandai_alumni, simpan_alumni
from handlers.lihat_alumni import tampilkan_tahun_alumni, tampilkan_daftar_alumni_per_tahun
from handlers.lapor_pekanan import lapor_handler
from handlers.upload_foto import upload_foto_handler
from handlers.compress import get_compress_handler
from handlers.remove_bg import get_remove_bg_handler
from handlers.rekapbulanan import (
    handle_rekapbulanan_dinamis,
    handle_pilih_bulan,
    handle_pilih_halaqah
)
import os
import threading
from flask import Flask

TOKEN = "7776046370:AAEZaKCCpy288MclyE9OzSBrSqVSn1Rex90"
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

    lihat_santri_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(mulai_lihat_santri, pattern="^lihat_santri$")],
    states={
        PILIH_HALAQAH: [
            CallbackQueryHandler(handle_pilihan, pattern="^(lanjutkan_santri|pilih_halaqah)$"),
        ],
        TAMPIL_HALAQAH: [
            CallbackQueryHandler(tampilkan_santri_halaqah, pattern="^show_"),
        ],
    },
    fallbacks=[],
)
# Simpan Alumni
    alumni_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(tandai_alumni, pattern=r"^tandai_alumni_\d+$")],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_alumni)]
    },
    fallbacks=[],
    allow_reentry=True
)
    application.add_handler(lihat_santri_conv)
    application.add_handler(pendidikan_conv)
    application.add_handler(wali_conv)
    application.add_handler(CommandHandler("rekapbulanan", handle_rekapbulanan_dinamis))
    application.add_handler(CallbackQueryHandler(handle_pilih_bulan, pattern="^bulan_"))
    application.add_handler(CallbackQueryHandler(handle_pilih_halaqah, pattern="^halaqah_"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_tentang_kami, pattern="^tentang$"))
    application.add_handler(CallbackQueryHandler(handle_profil_pondok, pattern="^profil_pondok$"))
    application.add_handler(CallbackQueryHandler(handle_visi_misi, pattern="^visi_misi$"))
    application.add_handler(CallbackQueryHandler(handle_struktur_organisasi, pattern="^struktur$"))
    application.add_handler(CallbackQueryHandler(handle_program_pendidikan, pattern="^program_pendidikan$"))
    application.add_handler(CallbackQueryHandler(handle_psb, pattern="^psb$"))
    application.add_handler(CallbackQueryHandler(handle_unduh, pattern="^unduh$"))
    application.add_handler(CallbackQueryHandler(handle_galeri, pattern="^galeri$"))
    application.add_handler(CallbackQueryHandler(handle_layanan, pattern="^layanan$"))
    application.add_handler(CallbackQueryHandler(handle_portal, pattern="^portal$"))
    application.add_handler(CallbackQueryHandler(proses_nama, pattern="^lihat_nama$"))
    application.add_handler(CallbackQueryHandler(callback_nama, pattern="^lihat_santri_\\d+$"))
    application.add_handler(CallbackQueryHandler(daftar_halaqah, pattern="^daftar_halaqah$"))
    application.add_handler(CallbackQueryHandler(tampilkan_tahun_alumni, pattern=r"^lihat_daftar_alumni$"))
    application.add_handler(CallbackQueryHandler(tampilkan_daftar_alumni_per_tahun, pattern=r"^lihat_alumni_\d{4}$"))
    application.add_handler(CallbackQueryHandler(callback_lanjut_nama, pattern=r"^lanjut_nama_\d+$"))
    application.add_handler(tambah_santri_handler)
    application.add_handler(lapor_handler)
    application.add_handler(edit_hafalan_handler)
    application.add_handler(upload_foto_handler)
    application.add_handler(kelas_handler)
    application.add_handler(angkatan_handler)
    application.add_handler(alumni_handler)
    application.add_handler(detail_santri_handler)
    application.add_handler(lihat_data_handler)
    application.add_handler(get_edit_handler())
    application.add_handler(get_edit_data_santri_handler())
    application.add_handler(get_edit_pendidikan_santri_handler())
    application.add_handler(get_edit_wali_santri_handler())
    application.add_handler(get_edit_kelas_santri_handler())
    application.add_handler(get_edit_angkatan_santri_handler())
    application.add_handler(get_compress_handler())
    application.add_handler(get_remove_bg_handler())

    application.add_handler(CallbackQueryHandler(handle_callback))
    
    
    application.run_webhook(
      listen="0.0.0.0",
      port=int(os.environ.get('PORT', 10000)),  # render akan otomatis pakai ini
      url_path=TOKEN,
      webhook_url=f"https://bot-telegram-02rg.onrender.com/{TOKEN}",
)

if __name__ == "__main__":
    main()
