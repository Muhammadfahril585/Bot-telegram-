from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)
from handlers.callbacks import handle_callback
from handlers.menu import start_menu
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
from handlers.angkatan import angkatan_handler
from handlers.edit_data import get_handler as get_edit_handler
from handlers.edit_data_santri import get_edit_data_santri_handler
from handlers.edit_pendidikan_santri import get_edit_pendidikan_santri_handler
from handlers.edit_wali_santri import get_edit_wali_santri_handler
from handlers.edit_kelas_santri import get_edit_kelas_santri_handler
from handlers.edit_angkatan_santri import get_edit_angkatan_santri_handler
from handlers.tandai_alumni import tandai_alumni, simpan_alumni
from handlers.lihat_alumni import tampilkan_tahun_alumni, tampilkan_daftar_alumni_per_tahun
from handlers.lapor_pekanan import lapor_handler
from handlers.rekapbulanan import (
    handle_rekapbulanan_dinamis,
    handle_pilih_bulan,
    handle_pilih_halaqah
)

# Handler untuk /lihatsantri
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
#Simpan Alumni
alumni_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(tandai_alumni, pattern=r"^tandai_alumni_\d+$")],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_alumni)]
    },
    fallbacks=[],
    allow_reentry=True,
)
# Menjalankan bot
if __name__ == '__main__':
    from config import BOT_TOKEN

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Tambahkan semua handler
    app.add_handler(pendidikan_conv)
    app.add_handler(wali_conv)
    app.add_handler(lihat_santri_conv)
    app.add_handler(CommandHandler("rekapbulanan", handle_rekapbulanan_dinamis))
    app.add_handler(CallbackQueryHandler(handle_pilih_bulan, pattern="^bulan_"))
    app.add_handler(CallbackQueryHandler(handle_pilih_halaqah, pattern="^halaqah_"))
    app.add_handler(CommandHandler("start", start_menu))
    app.add_handler(CallbackQueryHandler(handle_tentang_kami, pattern="^tentang$"))    
    app.add_handler(CallbackQueryHandler(handle_profil_pondok, pattern="^profil_pondok$"))
    app.add_handler(CallbackQueryHandler(handle_visi_misi, pattern="^visi_misi$"))
    app.add_handler(CallbackQueryHandler(handle_struktur_organisasi, pattern="^struktur$")) 
    app.add_handler(CallbackQueryHandler(handle_program_pendidikan, pattern="^program_pendidikan$"))
    app.add_handler(CallbackQueryHandler(handle_psb, pattern="^psb$"))
    app.add_handler(CallbackQueryHandler(handle_unduh, pattern="^unduh$"))
    app.add_handler(CallbackQueryHandler(handle_galeri, pattern="^galeri$"))
    app.add_handler(CallbackQueryHandler(handle_layanan, pattern="^layanan$"))  
    app.add_handler(CallbackQueryHandler(handle_portal, pattern="^portal$"))
    app.add_handler(CallbackQueryHandler(proses_nama, pattern="^lihat_nama$"))
    app.add_handler(CallbackQueryHandler(callback_nama, pattern="^lihat_santri_\\d+$"))
    app.add_handler(CallbackQueryHandler(daftar_halaqah, pattern="^daftar_halaqah$"))
    app.add_handler(CallbackQueryHandler(tampilkan_tahun_alumni, pattern=r"^lihat_daftar_alumni$"))
    app.add_handler(CallbackQueryHandler(tampilkan_daftar_alumni_per_tahun, pattern=r"^lihat_alumni_\d{4}$"))
    app.add_handler(tambah_santri_handler)
    app.add_handler(lapor_handler)
    app.add_handler(kelas_handler)
    app.add_handler(angkatan_handler)
    app.add_handler(alumni_handler)
    app.add_handler(detail_santri_handler)
    app.add_handler(lihat_data_handler)
    app.add_handler(get_edit_handler())
    app.add_handler(get_edit_data_santri_handler())
    app.add_handler(get_edit_pendidikan_santri_handler())
    app.add_handler(get_edit_wali_santri_handler())
    app.add_handler(get_edit_kelas_santri_handler())
    app.add_handler(get_edit_angkatan_santri_handler())

    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot sedang berjalan...")
    app.run_polling()
