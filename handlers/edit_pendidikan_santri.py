from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import sqlite3

DB_PATH = "itqon.db"

EDIT_FIELD, MASUKKAN_NILAI = range(2)

async def edit_pendidikan_santri(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    user_data['edit_santri_id'] = int(query.data.split("_")[-1])

    keyboard = [
        [InlineKeyboardButton("Nama Lembaga", callback_data="edit_nama_lembaga")],
        [InlineKeyboardButton("NPNS", callback_data="edit_npns")],
        [InlineKeyboardButton("Jenis Pendidikan", callback_data="edit_jenis_pendidikan")],
        [InlineKeyboardButton("Lokasi Lembaga", callback_data="edit_lokasi_lembaga")],
        [InlineKeyboardButton("Provinsi", callback_data="edit_provinsi")],
        [InlineKeyboardButton("Kabupaten", callback_data="edit_kabupaten")],
        [InlineKeyboardButton("Kecamatan", callback_data="edit_kecamatan")],
        [InlineKeyboardButton("Alamat", callback_data="edit_alamat")],
        [InlineKeyboardButton("Tahun Lulus", callback_data="edit_tahun_lulus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Pilih data pendidikan yang ingin diedit:", reply_markup=reply_markup)
    return EDIT_FIELD

async def pilih_field_edit(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    field = query.data.replace("edit_", "")
    context.user_data['field'] = field

    field_names = {
        "nama_lembaga": "Nama Lembaga",
        "npns": "NPNS",
        "jenis_pendidikan": "Jenis Pendidikan",
        "lokasi_lembaga": "Lokasi Lembaga",
        "provinsi": "Provinsi",
        "kabupaten": "Kabupaten",
        "kecamatan": "Kecamatan",
        "alamat": "Alamat",
        "tahun_lulus": "Tahun Lulus"
    }

    await query.edit_message_text(f"Kirim nilai baru untuk *{field_names.get(field, field)}*:", parse_mode="Markdown")
    return MASUKKAN_NILAI

async def simpan_edit(update: Update, context: CallbackContext):
    user_data = context.user_data
    field = user_data.get("field")
    santri_id = user_data.get("edit_santri_id")
    value = update.message.text.strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Cek apakah sudah ada entri pendidikan untuk santri ini
    c.execute("SELECT id FROM pendidikan WHERE santri_nama_id = ?", (santri_id,))
    row = c.fetchone()

    if not row:
        # Jika belum ada, buat dulu entri kosong
        c.execute("INSERT INTO pendidikan (santri_nama_id) VALUES (?)", (santri_id,))
        conn.commit()

    # Update data
    c.execute(f"UPDATE pendidikan SET {field} = ? WHERE santri_nama_id = ?", (value, santri_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Data *{field.replace('_', ' ').title()}* berhasil diperbarui!", parse_mode="Markdown")
    return ConversationHandler.END

def get_edit_pendidikan_santri_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_pendidikan_santri, pattern=r"^edit_pendidikan_santri_\d+$")
        ],
        states={
            EDIT_FIELD: [CallbackQueryHandler(pilih_field_edit, pattern=r"^edit_")],
            MASUKKAN_NILAI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_edit)],
        },
        fallbacks=[],
        allow_reentry=True,
    )
