# handlers/tandai_alumni.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import get_db  # Gunakan koneksi dari database.py

MASUKKAN_TAHUN = range(1)

async def tandai_alumni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    santri_id = int(query.data.split("_")[-1])
    context.user_data["alumni_santri_id"] = santri_id

    await query.edit_message_text("Masukkan tahun lulus santri ini (contoh: 2023):")
    return MASUKKAN_TAHUN

async def simpan_alumni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tahun = update.message.text.strip()
    if not tahun.isdigit():
        await update.message.reply_text("❗ Masukkan tahun dengan benar, contoh: 2023")
        return MASUKKAN_TAHUN

    santri_id = context.user_data.get("alumni_santri_id")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nama_lengkap FROM santri_nama WHERE id = %s", (santri_id,))
    result = cur.fetchone()

    if result:
        nama = result[0]
        cur.execute(
            "INSERT INTO alumni (santri_nama_id, nama_lengkap, tahun_lulus) VALUES (%s, %s, %s)",
            (santri_id, nama, int(tahun))
        )
        conn.commit()
        await update.message.reply_text(
            f"✅ *{nama}* berhasil ditandai sebagai Alumni {tahun}.", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❗ Gagal menemukan data santri.")

    conn.close()
    return ConversationHandler.END
