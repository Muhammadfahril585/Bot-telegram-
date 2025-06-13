from telegram import Update
from telegram.ext import ContextTypes
from database import get_db
from lib.navigation import tombol_navigasi

emoji_angka = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '1️⃣1️⃣', '1️⃣2️⃣']

async def daftar_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT nama FROM halaqah")
    hasil = cursor.fetchall()
    
    cursor.close()
    conn.close()

    if not hasil:
        pesan = "Belum ada halaqah yang terdaftar."
    else:
        daftar = []
        for i, row in enumerate(hasil):
            nama_asli = row[0]
            nama_ustadz = nama_asli.replace("Halaqah_", "").replace("_", " ")
            angka = emoji_angka[i] if i < len(emoji_angka) else f"{i+1}."
            daftar.append(f"{angka} <b>{nama_ustadz}</b>")

        pesan = (
            "<b>📋 Daftar Halaqah yang Terdaftar:</b>\n\n"
            + "\n".join(daftar) +
            "\n\n<i>Semoga setiap halaqah menjadi tempat tumbuhnya para penjaga Al-Qur'an yang istiqamah.</i>"
        )

    if update.message:
        await update.message.reply_text(pesan, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=pesan,
            parse_mode="HTML",
            reply_markup=tombol_navigasi("portal")
          )
