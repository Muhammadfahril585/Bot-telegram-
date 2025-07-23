from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, JobQueue, filters
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
from handlers.edit_hafalan import edit_hafalan_massal_handler
from handlers.daftar_halaqah import daftar_halaqah
from handlers.tambah_santri import tambah_santri_handler
from handlers.edit_laporan import get_conv_handler
from handlers.galeri import handle_galeri
from handlers.lapor_pekanan2 import handle_reset_callback 
from handlers.rekap_bulanan import handle_buat_pdf_rekap
from handlers.tambah_halaqah import tambah_halaqah_handler
from handlers.rekap_bulanan import rekap_bulanan_handlers
from handlers.start import cek_mode
from handlers.layanan import handle_layanan
from handlers.lapor_pekanan2 import laporan_pekanan_conv  
from handlers.portal import handle_portal
from handlers.ai_handler import handle_ai_mode
from handlers.lihat_santri import mulai_lihat_santri, detail_santri
from handlers.pindah_santri import pindah_handler
from handlers.edit_halaqah import edit_nama_halaqah_handler
from handlers.start import set_mode
from handlers.rubah_nama import rubah_nama_handler
from handlers.admin import handle_admin
from handlers.hapus_santri import hapus_handler

# Menjalankan bot
if __name__ == '__main__':
    from config import BOT_TOKEN

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_tentang_kami, pattern="^tentang$"))
    app.add_handler(CallbackQueryHandler(handle_profil_pondok, pattern="^profil_pondok$"))
    app.add_handler(CallbackQueryHandler(handle_visi_misi, pattern="^visi_misi$"))
    app.add_handler(CallbackQueryHandler(handle_struktur_organisasi, pattern="^struktur$"))
    app.add_handler(CallbackQueryHandler(handle_program_pendidikan, pattern="^program_pendidikan$"))
    app.add_handler(CallbackQueryHandler(handle_psb, pattern="^psb$"))
    app.add_handler(CallbackQueryHandler(set_mode, pattern="^mode_"))
    app.add_handler(CallbackQueryHandler(handle_reset_callback, pattern="^reset_"))
    app.add_handler(CallbackQueryHandler(handle_unduh, pattern="^unduh$"))
    app.add_handler(CallbackQueryHandler(handle_galeri, pattern="^galeri$"))
    app.add_handler(CallbackQueryHandler(handle_layanan, pattern="^layanan$"))
    app.add_handler(CallbackQueryHandler(handle_buat_pdf_rekap, pattern="^buat_pdf_rekap$"))
    app.add_handler(CallbackQueryHandler(handle_portal, pattern="^portal$"))
    app.add_handler(CallbackQueryHandler(daftar_halaqah, pattern="^daftar_halaqah$"))
    app.add_handler(CallbackQueryHandler(mulai_lihat_santri, pattern="^lihat_santri$"))
    app.add_handler(CallbackQueryHandler(detail_santri, pattern=r"^lihat_santri:\d+$"))
    for handler in rekap_bulanan_handlers:
      app.add_handler(handler)
    app.add_handler(tambah_santri_handler)
    app.add_handler(laporan_pekanan_conv)
    app.add_handler(edit_nama_halaqah_handler)
    app.add_handler(edit_hafalan_massal_handler)
    app.add_handler(tambah_halaqah_handler)
    app.add_handler(rubah_nama_handler)
    app.add_handler(CommandHandler("lihat_santri", mulai_lihat_santri))
    app.add_handler(CommandHandler("daftar_halaqah", daftar_halaqah))
    app.add_handler(CommandHandler("admin", handle_admin))
    app.add_handler(get_conv_handler())
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_ai_mode))
    app.add_handler(CommandHandler("mode", cek_mode))
    app.add_handler(pindah_handler)
    app.add_handler(hapus_handler)

    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot sedang berjalan...")
    app.run_polling()
