from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_navigasi
from utils.gsheet import get_sheet

async def daftar_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = get_sheet("Daftar Halaqah")
        daftar_halaqah = sheet.col_values(1)[2:]  # Mulai dari baris ke-3
        daftar_ustadz = sheet.col_values(2)[2:]

        if not daftar_halaqah or not daftar_ustadz:
            await update.message.reply_text("Data halaqah atau ustadz belum tersedia.")
            return

        pesan = "📋 *Daftar Halaqah PPTQ AL-ITQON GOWA*\n\n"

        for halaqah, ustadz in zip(daftar_halaqah, daftar_ustadz):
            if not halaqah.strip():
                continue
            pesan += f"*{halaqah}*\n👤 Ustadz: _{ustadz}_\n\n"

        if update.message:
           await update.message.reply_text(pesan, parse_mode="Markdown")
        elif update.callback_query:
           await update.callback_query.answer()
           await update.callback_query.edit_message_text(
                text=pesan,
                parse_mode="Markdown",
                reply_markup=tombol_navigasi("portal")
            )
    except Exception as e:
        error_msg = f"Terjadi kesalahan saat mengambil data halaqah:\n`{e}`"
        if update.message:
           await update.message.reply_text(error_msg, parse_mode="Markdown")
        elif update.callback_query:
           await update.callback_query.answer()
           await update.callback_query.edit_message_text(
                text=error_msg,
                parse_mode="Markdown"
            )
            
