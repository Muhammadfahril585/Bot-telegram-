from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import sqlite3

DB_PATH = "itqon.db"

EDIT_FIELD, MASUKKAN_NILAI = range(2)

async def edit_wali_santri(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    user_data['edit_santri_id'] = int(query.data.split("_")[-1])

    keyboard = [
        [InlineKeyboardButton("Ayah - Nama", callback_data="edit_ayah_nama")],
        [InlineKeyboardButton("Ayah - Tempat Lahir", callback_data="edit_ayah_tempat_lahir")],
        [InlineKeyboardButton("Ayah - Tanggal Lahir", callback_data="edit_ayah_tanggal_lahir")],
        [InlineKeyboardButton("Ayah - NIK", callback_data="edit_ayah_nik")],
        [InlineKeyboardButton("Ayah - Pendidikan", callback_data="edit_ayah_pendidikan")],
        [InlineKeyboardButton("Ayah - Pekerjaan", callback_data="edit_ayah_pekerjaan")],
        [InlineKeyboardButton("Ibu - Nama", callback_data="edit_ibu_nama")],
        [InlineKeyboardButton("Ibu - Tempat Lahir", callback_data="edit_ibu_tempat_lahir")],
        [InlineKeyboardButton("Ibu - Tanggal Lahir", callback_data="edit_ibu_tanggal_lahir")],
        [InlineKeyboardButton("Ibu - NIK", callback_data="edit_ibu_nik")],
        [InlineKeyboardButton("Ibu - Pendidikan", callback_data="edit_ibu_pendidikan")],
        [InlineKeyboardButton("Ibu - Pekerjaan", callback_data="edit_ibu_pekerjaan")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Pilih data wali yang ingin diedit:", reply_markup=reply_markup)
    return EDIT_FIELD

async def pilih_field_edit(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    field = query.data.replace("edit_", "")
    context.user_data['field'] = field

    label = field.replace("_", " ").title()
    await query.edit_message_text(f"Kirim nilai baru untuk *{label}*:", parse_mode="Markdown")
    return MASUKKAN_NILAI

async def simpan_edit(update: Update, context: CallbackContext):
    user_data = context.user_data
    field = user_data.get("field")
    santri_id = user_data.get("edit_santri_id")
    value = update.message.text.strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Cek apakah sudah ada entri wali
    c.execute("SELECT id FROM wali WHERE santri_nama_id = ?", (santri_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO wali (santri_nama_id) VALUES (?)", (santri_id,))
        conn.commit()

    # Update data wali
    c.execute(f"UPDATE wali SET {field} = ? WHERE santri_nama_id = ?", (value, santri_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Data *{field.replace('_', ' ').title()}* berhasil diperbarui!", parse_mode="Markdown")
    return ConversationHandler.END

def get_edit_wali_santri_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_wali_santri, pattern=r"^edit_wali_santri_\d+$")
        ],
        states={
            EDIT_FIELD: [CallbackQueryHandler(pilih_field_edit, pattern=r"^edit_(ayah|ibu)_.+")],
            MASUKKAN_NILAI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_edit)],
        },
        fallbacks=[],
        allow_reentry=True,
    )
