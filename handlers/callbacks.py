from telegram import Update
from telegram.ext import ContextTypes

# Import fungsi handler
from handlers.daftar_halaqah import daftar_halaqah
from handlers.rekapbulanan import handle_rekapbulanan_dinamis
from handlers.menu import start_menu

# Menangani callback dari tombol
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data  # Ambil data dari tombol

    # Tangani tombol "Daftar Halaqah"
    if callback_data == 'daftar_halaqah':
        await query.answer()
        await query.edit_message_text("Menampilkan daftar halaqah...")
        await daftar_halaqah(update, context)

    # Tangani tombol "Rekap Bulanan"
    elif callback_data == 'rekap_bulanan':
        await query.answer()
        await handle_rekapbulanan_dinamis(update, context)

    # Tombol "Lihat Santri" ditangani oleh ConversationHandler di bot.py
    elif callback_data == 'lihat_santri':
        await query.answer()
        # Biarkan ConversationHandler menanganinya, tidak perlu eksekusi di sini
        return

    elif callback_data == 'menu':
        await query.answer()
        await query.delete_message()  # hapus pesan saat ini
        await start_menu(update, context)  # panggil kembali menu /start
