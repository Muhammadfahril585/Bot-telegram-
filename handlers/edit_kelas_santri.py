from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from database import get_db

EDIT_FIELD, MASUKKAN_NILAI = range(2)

async def edit_kelas_santri(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    user_data['edit_santri_id'] = int(query.data.split("_")[-1])

    keyboard = [
        [InlineKeyboardButton("Jenjang", callback_data="edit_jenjang")],
        [InlineKeyboardButton("Tingkat", callback_data="edit_tingkat")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Pilih data kelas yang ingin diedit:", reply_markup=reply_markup)
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

    # Konversi tingkat ke integer jika perlu
    if field == "tingkat":
        try:
            value = int(value)
        except ValueError:
            await update.message.reply_text("❌ Masukkan angka untuk tingkat.")
            return MASUKKAN_NILAI

    conn = get_db()
    c = conn.cursor()

    # Cek apakah sudah ada entri kelas
    c.execute("SELECT id FROM kelas WHERE santri_nama_id = %s", (santri_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO kelas (santri_nama_id) VALUES (%s)", (santri_id,))
        conn.commit()

    # Update data kelas
    c.execute(f"UPDATE kelas SET {field} = %s WHERE santri_nama_id = %s", (value, santri_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Data *{field.title()}* berhasil diperbarui!", parse_mode="Markdown")
    return ConversationHandler.END

def get_edit_kelas_santri_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_kelas_santri, pattern=r"^edit_kelas_santri_\d+$")
        ],
        states={
            EDIT_FIELD: [CallbackQueryHandler(pilih_field_edit, pattern=r"^edit_")],
            MASUKKAN_NILAI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_edit)],
        },
        fallbacks=[],
        allow_reentry=True,
          )
