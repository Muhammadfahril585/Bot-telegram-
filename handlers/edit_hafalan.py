from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import get_db

PILIH_HALAQAH_EDIT, PILIH_SANTRI_EDIT, INPUT_HAFALAN_EDIT = range(3)

# /edit_hafalan
async def mulai_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT nama FROM halaqah ORDER BY nama ASC")
    hasil = cursor.fetchall()
    if not hasil:
        await update.message.reply_text("❌ Belum ada halaqah.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(h[0], callback_data=f"edit_halaqah|{h[0]}")] for h in hasil]
    await update.message.reply_text("📌 Pilih halaqah:", reply_markup=InlineKeyboardMarkup(keyboard))
    return PILIH_HALAQAH_EDIT

async def pilih_halaqah_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nama_halaqah = query.data.split("|")[1]
    context.user_data["halaqah_edit"] = nama_halaqah

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.nama FROM santri s
        JOIN halaqah h ON s.halaqah_id = h.id
        WHERE h.nama = %s
        ORDER BY s.nama ASC
    """, (nama_halaqah,))
    santri_list = cursor.fetchall()

    if not santri_list:
        await query.edit_message_text("❌ Tidak ada santri dalam halaqah ini.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(n[0], callback_data=f"edit_santri|{n[0]}")] for n in santri_list]
    await query.edit_message_text(
        f"✅ Halaqah: *{nama_halaqah}*\n\n📌 Pilih santri yang ingin diedit:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PILIH_SANTRI_EDIT

async def pilih_santri_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    nama_santri = query.data.split("|")[1]
    context.user_data["santri_edit"] = nama_santri

    await query.edit_message_text(
        f"📝 Masukkan data hafalan baru untuk *{nama_santri}*:\n\nContoh:\n`10/Juz 1-10`",
        parse_mode="Markdown"
    )
    return INPUT_HAFALAN_EDIT

async def input_hafalan_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "/" not in text:
        await update.message.reply_text("❌ Format salah. Gunakan contoh seperti:\n`10/Juz 1-10`", parse_mode="Markdown")
        return INPUT_HAFALAN_EDIT

    try:
        hafalan_str, keterangan = text.split("/", 1)
        hafalan = float(hafalan_str.strip())
        keterangan = keterangan.strip()
    except:
        await update.message.reply_text("⚠️ Format tidak dikenali. Contoh: `5/Juz 28-30`", parse_mode="Markdown")
        return INPUT_HAFALAN_EDIT

    nama = context.user_data["santri_edit"]
    halaqah = context.user_data["halaqah_edit"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE santri
        SET hafalan = %s, keterangan = %s
        WHERE nama = %s AND halaqah_id = (
            SELECT id FROM halaqah WHERE nama = %s
        )
    """, (hafalan, keterangan, nama, halaqah))
    db.commit()

    await update.message.reply_text(f"✅ Data hafalan untuk *{nama}* berhasil diperbarui!", parse_mode="Markdown")
    return ConversationHandler.END

async def batal_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Proses edit dibatalkan.")
    return ConversationHandler.END

edit_hafalan_handler = ConversationHandler(
    entry_points=[CommandHandler("edit_hafalan", mulai_edit)],
    states={
        PILIH_HALAQAH_EDIT: [CallbackQueryHandler(pilih_halaqah_edit, pattern=r"^edit_halaqah\|")],
        PILIH_SANTRI_EDIT: [CallbackQueryHandler(pilih_santri_edit, pattern=r"^edit_santri\|")],
        INPUT_HAFALAN_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_hafalan_edit)],
    },
    fallbacks=[CommandHandler("batal", batal_edit)],
  )
