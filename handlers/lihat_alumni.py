from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import get_db  # pakai get_db dari database.py

async def tampilkan_tahun_alumni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT tahun_lulus FROM alumni ORDER BY tahun_lulus DESC")
    tahun_list = cursor.fetchall()
    conn.close()

    if not tahun_list:
        await query.edit_message_text("Belum ada data alumni.")
        return

    keyboard = [
        [InlineKeyboardButton(f"Alumni {tahun[0]}", callback_data=f"lihat_alumni_{tahun[0]}")]
        for tahun in tahun_list
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Pilih tahun alumni:", reply_markup=reply_markup)

async def tampilkan_daftar_alumni_per_tahun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tahun = query.data.split("_")[-1]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sn.nama_lengkap
        FROM alumni a
        JOIN santri_nama sn ON sn.id = a.santri_nama_id
        WHERE a.tahun_lulus = %s
        ORDER BY sn.nama_lengkap
    """, (tahun,))
    alumni = cursor.fetchall()
    conn.close()

    if not alumni:
        await query.edit_message_text(f"Tidak ada alumni di tahun {tahun}.")
        return

    teks = f"*Daftar Alumni {tahun}:*\n"
    for i, (nama,) in enumerate(alumni, 1):
        teks += f"{i}. {nama}\n"

    await query.edit_message_text(teks, parse_mode="Markdown")
