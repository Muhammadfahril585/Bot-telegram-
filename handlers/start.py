from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from handlers.tracker import track_user_activity
from datetime import datetime
import pytz


waktu_indonesia = pytz.timezone('Asia/Makassar')
nama_hari = {
    "Monday": "Senin",
    "Tuesday": "Selasa",
    "Wednesday": "Rabu",
    "Thursday": "Kamis",
    "Friday": "Jumat",
    "Saturday": "Sabtu",
    "Sunday": "Ahad"
}

nama_bulan = {
    "January": "Januari",
    "February": "Februari",
    "March": "Maret",
    "April": "April",
    "May": "Mei",
    "June": "Juni",
    "July": "Juli",
    "August": "Agustus",
    "September": "September",
    "October": "Oktober",
    "November": "November",
    "December": "Desember"
}

# Fungsi utama untuk /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Jika kamu ingin tracking pengguna
    await track_user_activity(update, context)

    now = datetime.now(waktu_indonesia) 
    hari = nama_hari.get(now.strftime("%A"), now.strftime("%A"))
    bulan = nama_bulan.get(now.strftime("%B"), now.strftime("%B"))
    tanggal = now.strftime(f"%d {bulan} %Y")
    jam = now.strftime("%H:%M")

    pesan = (
        "<b>Assalamualaikum Warahmatullahi Wabarakatuh...</b>\n"
        f"🕐 <b>{hari}, {tanggal}, {jam}</b>\n\n"
        "📚 <b>Selamat datang di Pondok Pesantren Al-ITQON GOWA</b>\n\n"
        "Silakan pilih menu di bawah ini:"
    )

    keyboard = [
        [InlineKeyboardButton("📌 Tentang Kami", callback_data="tentang")],
        [InlineKeyboardButton("🎓 Program Pendidikan", callback_data="program_pendidikan")],
        [InlineKeyboardButton("📝 Pendaftaran Santri Baru (PSB)", callback_data="psb")],
        [InlineKeyboardButton("📁 Unduh", callback_data="unduh")],
        [InlineKeyboardButton("🖼️ Galeri Foto", callback_data="galeri")],
        [InlineKeyboardButton("🛠️ Layanan", callback_data="layanan")],
        [InlineKeyboardButton("📊 Portal Santri", callback_data="portal")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_html(pesan, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_html(pesan, reply_markup=reply_markup)
