from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from lib.formatbulanan import format_rekap_bulanan
from database import get_db

# State untuk proses nama halaqah
REKAP_BULAN = 100  # Sama dengan yang didefinisikan di bot.py

async def proses_nama_halaqah(update: Update, context_: ContextTypes.DEFAULT_TYPE):
    bulan = context_.user_data.get("bulan")

    if not bulan:
        await update.message.reply_text("Bulan belum ditemukan. Silakan mulai ulang dengan perintah /rekapbulanan.")
        return ConversationHandler.END

    nama_halaqah = update.message.text.strip()
    db = get_db()

    try:
        hasil = format_rekap_bulanan(db=db, bulan=bulan, halaqah=nama_halaqah)
        await update.message.reply_text(hasil, parse_mode='Markdown')
    except Exception as e:
        print("Error proses_nama_halaqah:", e)
        await update.message.reply_text("Terjadi kesalahan saat mengambil data rekap halaqah.")

    context_.user_data.pop("bulan", None)
    return ConversationHandler.END
