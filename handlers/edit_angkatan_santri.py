from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import sqlite3

DB_PATH = "itqon.db"

EDIT_ANGKATAN = range(1)

async def edit_angkatan_santri(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    santri_id = int(query.data.split("_")[-1])
    context.user_data['edit_santri_id'] = santri_id

    await query.edit_message_text("Kirim tahun *angkatan* baru:", parse_mode="Markdown")
    return EDIT_ANGKATAN

async def simpan_edit_angkatan(update: Update, context: CallbackContext):
    santri_id = context.user_data.get("edit_santri_id")
    value = update.message.text.strip()

    try:
        value = int(value)
    except ValueError:
        await update.message.reply_text("❌ Masukkan angka untuk angkatan.")
        return EDIT_ANGKATAN

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Cek apakah sudah ada entri angkatan
    c.execute("SELECT id FROM angkatan WHERE santri_nama_id = ?", (santri_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO angkatan (santri_nama_id) VALUES (?)", (santri_id,))
        conn.commit()

    # Update nilai angkatan
    c.execute("UPDATE angkatan SET angkatan = ? WHERE santri_nama_id = ?", (value, santri_id))
    conn.commit()
    conn.close()

    await update.message.reply_text("✅ Data *angkatan* berhasil diperbarui!", parse_mode="Markdown")
    return ConversationHandler.END

def get_edit_angkatan_santri_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_angkatan_santri, pattern=r"^edit_angkatan_santri_\d+$")
        ],
        states={
            EDIT_ANGKATAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_edit_angkatan)],
        },
        fallbacks=[],
        allow_reentry=True,
    )
