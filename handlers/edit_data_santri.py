from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import sqlite3

DB_PATH = "itqon.db"  # Sesuaikan path database kamu

EDIT_FIELD, MASUKKAN_NILAI = range(2)

async def edit_data_santri(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    user_data['edit_santri_id'] = int(query.data.split("_")[-1])

    keyboard = [
        [InlineKeyboardButton("Nama Lengkap", callback_data="edit_nama")],
        [InlineKeyboardButton("NIS", callback_data="edit_nis")],
        [InlineKeyboardButton("NIK", callback_data="edit_nik")],
        [InlineKeyboardButton("Nomor KK", callback_data="edit_nomor_kk")], 
        [InlineKeyboardButton("TTL", callback_data="edit_ttl")],
        [InlineKeyboardButton("Jenis Kelamin", callback_data="edit_jk")],
        [InlineKeyboardButton("Agama", callback_data="edit_agama")],
        [InlineKeyboardButton("Anak ke", callback_data="edit_anak_ke")],
        [InlineKeyboardButton("Alamat", callback_data="edit_alamat")],
        [InlineKeyboardButton("Kecamatan", callback_data="edit_kecamatan")],
        [InlineKeyboardButton("Kabupaten", callback_data="edit_kabupaten")],
        [InlineKeyboardButton("Provinsi", callback_data="edit_provinsi")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Pilih data yang ingin diedit:", reply_markup=reply_markup)
    return EDIT_FIELD

async def pilih_field_edit(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    field = query.data.replace("edit_", "")
    context.user_data['field'] = field

    field_names = {
        "nama": "Nama Lengkap",
        "nis": "NIS",
        "nik": "NIK",
        "nomor_kk": "Nomor KK",
        "ttl": "Tempat Tanggal Lahir",
        "jk": "Jenis Kelamin",
        "agama": "Agama",
        "anak_ke": "Anak Ke",
        "alamat": "Alamat",
        "kecamatan": "Kecamatan",
        "kabupaten": "Kabupaten",
        "provinsi": "Provinsi"
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

    if field == "nama":
       c.execute("UPDATE santri_nama SET nama_lengkap = ? WHERE id = ?", (value, santri_id))
    elif field == "ttl":
    # Pisahkan value menjadi tempat dan tanggal
      if "," in value:
          tempat, tanggal = map(str.strip, value.split(",", 1))
          c.execute("UPDATE santri SET tempat_lahir = ?, tanggal_lahir = ? WHERE santri_nama_id = ?", (tempat, tanggal, santri_id))
      else:
        await update.message.reply_text("❗ Format TTL salah. Gunakan format: Tempat, Tanggal\nContoh: *Makassar, 2010-10-08*", parse_mode="Markdown")
        return MASUKKAN_NILAI
    else:
      c.execute(f"UPDATE santri SET {field} = ? WHERE santri_nama_id = ?", (value, santri_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Data *{field}* berhasil diperbarui!", parse_mode="Markdown")
    return ConversationHandler.END

def get_edit_data_santri_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_data_santri, pattern=r"^edit_data_santri_\d+$")
        ],
        states={
            EDIT_FIELD: [CallbackQueryHandler(pilih_field_edit, pattern=r"^edit_")],
            MASUKKAN_NILAI: [MessageHandler(filters.TEXT & ~filters.COMMAND, simpan_edit)],
        },
        fallbacks=[],
        allow_reentry=True,
    )
