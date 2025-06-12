
# handlers/edit_data.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
#from handlers.edit_data_santri import edit_data_santri
#from handlers.edit_pendidikan_santri import edit_pendidikan_santri
#from handlers.edit_wali_santri import edit_wali_santri
#from handlers.edit_kelas_santri import edit_kelas_santri
#from handlers.edit_angkatan_santri import edit_angkatan_santri
import sqlite3

PILIH_SANTRI, PILIH_BIDANG = range(2)

DB_PATH = "itqon.db"  # Ubah sesuai lokasi database kamu

async def mulai_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ambil nama-nama santri
    cursor.execute("SELECT id, nama_lengkap FROM santri_nama ORDER BY nama_lengkap")
    santri_list = cursor.fetchall()
    conn.close()

    if not santri_list:
        await update.message.reply_text("Belum ada data santri yang tersimpan.")
        return ConversationHandler.END

    # Buat daftar tombol nama santri
    keyboard = []
    for santri_id, nama in santri_list:
        keyboard.append([InlineKeyboardButton(nama, callback_data=f"edit_santri_{santri_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Pilih santri yang ingin diedit:",
        reply_markup=reply_markup
    )

    return PILIH_SANTRI  # Ini state lanjutan (harus kamu definisikan di ConversationHandler)

import re

async def pilih_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match = re.match(r"edit_santri_(\d+)", query.data)
    if not match:
        await query.edit_message_text("Terjadi kesalahan dalam pemilihan santri.")
        return ConversationHandler.END

    santri_id = int(match.group(1))
    context.user_data['edit_santri_id'] = santri_id

    keyboard = [
        [InlineKeyboardButton("Edit data santri", callback_data=f"edit_data_santri_{santri_id}")],
        [InlineKeyboardButton("Edit Pendidikan", callback_data=f"edit_pendidikan_santri_{santri_id}")],
        [InlineKeyboardButton("Edit Wali", callback_data=f"edit_wali_santri_{santri_id}")],
        [InlineKeyboardButton("Edit Kelas", callback_data=f"edit_kelas_santri_{santri_id}")],
        [InlineKeyboardButton("Edit Angkatan", callback_data=f"edit_angkatan_santri_{santri_id}")],
        [InlineKeyboardButton("Tandai Alumni", callback_data=f"tandai_alumni_{santri_id}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Pilih bagian data yang ingin diedit:", reply_markup=reply_markup)
    return PILIH_BIDANG

def get_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("edit_santri", mulai_edit)],
        states={
            PILIH_SANTRI: [CallbackQueryHandler(pilih_santri, pattern="^edit_santri_\\d+$")],
            PILIH_BIDANG: [
             # CallbackQueryHandler(edit_data_santri, pattern=r"^edit_data_santri_\d+$"),
              #CallbackQueryHandler(edit_pendidikan_santri, pattern=r"^edit_pendidikan_santri_\d+$"),
              #CallbackQueryHandler(edit_wali_santri, pattern=r"^edit_wali_santri_\d+$"),
              #CallbackQueryHandler(edit_kelas_santri, pattern=r"^edit_kelas_santri_\d+$"),
              #CallbackQueryHandler(edit_angkatan_santri, pattern=r"^edit_angkatan_santri_\d+$"),
            ],
          },
          fallbacks=[CommandHandler("edit_santri", mulai_edit)],
          )


