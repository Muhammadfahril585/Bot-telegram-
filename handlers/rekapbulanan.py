from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import get_db
from lib.formatbulanan import format_rekap_bulanan
from lib.navigation import tombol_navigasi

# Command /rekapbulanan
async def handle_rekapbulanan_dinamis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"bulan_{i}")]
        for i in range(1, 13)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Pilih bulan untuk rekap bulanan:", reply_markup=reply_markup)

# Setelah user klik bulan
async def handle_pilih_bulan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bulan = int(query.data.split("_")[1])
    context.user_data["bulan"] = bulan

    # Ambil daftar halaqah dari database
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
    SELECT DISTINCT h.nama, h.ustadz
    FROM santri s
    JOIN halaqah h ON s.halaqah_id = h.id
    ORDER BY h.nama ASC
""")
    rows = cursor.fetchall()

    if not rows:
        await query.edit_message_text("Belum ada data halaqah.")
        return

    keyboard = [
       [InlineKeyboardButton(f"{h[0]} - {h[1]}", callback_data=f"halaqah_{h[0]}")] for h in rows
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"Bulan dipilih: *{bulan}*\nSekarang pilih halaqah:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Setelah user klik halaqah
async def handle_pilih_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    halaqah = query.data.split("_", 1)[1]
    bulan = context.user_data.get("bulan")

    if not bulan:
        await query.edit_message_text("Bulan belum ditemukan. Silakan ulangi dengan /rekapbulanan.")
        return

    db = get_db()
    try:
        hasil = format_rekap_bulanan(db=db, bulan=bulan, halaqah=halaqah)
        await query.edit_message_text(
          hasil,
          parse_mode='Markdown',
          reply_markup=tombol_navigasi("portal")
        )
    except Exception as e:
        print("Error rekapbulanan:", e)
        await query.edit_message_text("Terjadi kesalahan saat mengambil data rekap halaqah.")

    context.user_data.pop("bulan", None)
