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
TOKEN = "7776046370:AAEZaKCCpy288MclyE9OzSBrSqVSn1Rex90"

def main():
    application = ApplicationBuilder().token(TOKEN).build()

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
    application.add_handler(CallbackQueryHandler(daftar_halaqah, pattern="^daftar_halaqah$"))
    application.add_handler(CallbackQueryHandler(callback_nama, pattern="^lihat_santri_\\d+$"))
    application.add_handler(CommandHandler("rekapbulanan", handle_rekapbulanan_dinamis))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=TOKEN,
        webhook_url=f"https://bot-telegram-02rg.onrender.com/{TOKEN}",
    )

if __name__ == "__main__":
    main()
