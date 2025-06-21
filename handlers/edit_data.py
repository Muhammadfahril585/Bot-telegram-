from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import get_db
import re

PILIH_SANTRI, PILIH_BIDANG = range(2)

ITEMS_PER_PAGE = 10  # Jumlah nama per halaman

async def mulai_edit(update: Update, context: ContextTypes.DEFAULT_TYPE, offset=0):
    conn = get_db()
    cursor = conn.cursor()

    # Hitung total santri
    cursor.execute("SELECT COUNT(*) FROM santri_nama")
    total_santri = cursor.fetchone()[0]

    # Ambil 10 santri berdasarkan offset
    cursor.execute("""
        SELECT id, nama_lengkap FROM santri_nama
        ORDER BY nama_lengkap
        LIMIT %s OFFSET %s
    """, (ITEMS_PER_PAGE, offset))
    santri_list = cursor.fetchall()
    conn.close()

    if not santri_list:
        await update.message.reply_text("Belum ada data santri yang tersimpan.")
        return ConversationHandler.END

    # Buat daftar tombol nama santri
    keyboard = [
        [InlineKeyboardButton(nama, callback_data=f"edit_santri_{santri_id}")]
        for santri_id, nama in santri_list
    ]

    # Tombol navigasi
    nav_buttons = []
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Sebelumnya", callback_data=f"edit_prev_{offset - ITEMS_PER_PAGE}"))
    if offset + ITEMS_PER_PAGE < total_santri:
        nav_buttons.append(InlineKeyboardButton("➡️ Selanjutnya", callback_data=f"edit_next_{offset + ITEMS_PER_PAGE}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
       await update.message.reply_text(
        "📋 Pilih santri yang ingin diedit:",
        reply_markup=reply_markup
       )
    else:
       await update.callback_query.edit_message_text(
        "📋 Pilih santri yang ingin diedit:",
        reply_markup=reply_markup
       )

    return PILIH_SANTRI

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

async def paginate_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    offset = int(query.data.split("_")[-1])
    await mulai_edit(update, context, offset)

def get_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("edit_santri", mulai_edit)],
        states={
            PILIH_SANTRI: [CallbackQueryHandler(pilih_santri, pattern=r"^edit_santri_\d+$"),CallbackQueryHandler(paginate_edit, pattern=r"^edit_(next|prev)_\d+$")],
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
