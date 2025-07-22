from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from handlers.tracker import track_user_activity
from datetime import datetime
import pytz

# Global dict untuk menyimpan mode per pengguna
user_mode = {}

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
        "Silakan pilih mode penggunaan bot ini:"
    )

    keyboard = [
        [InlineKeyboardButton("🧠 Mode AI Cerdas", callback_data="mode_ai")],
        [InlineKeyboardButton("🔘 Mode Manual", callback_data="mode_manual")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_html(pesan, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_html(pesan, reply_markup=reply_markup)

# Fungsi untuk menangani pilihan mode
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    mode = query.data.replace("mode_", "")
    user_mode[user_id] = mode

    if mode == "ai":
        teks = (
            "✅ <b>Mode AI Cerdas diaktifkan!</b>\n\n"
            "Sekarang Anda bisa bertanya bebas, misalnya:\n"
            "- Siapa santri hafalan terbanyak?\n"
            "- Tampilkan rekap bulan\n"
            "- Halaqah Umar bin Khattab isinya siapa saja?\n\n"
            "_ Membantu dalam hal lain seperti menterjemah,menjawab soal, mencari artikel,dll.\n"
            "Saya akan bantu menjawab dengan cerdas tapi kadang tidak akurat, jika ini membingungkan silahkan gunakan Mode Manual 🤖"
        )
    else:
        teks = (
            "✅ <b>Mode Manual diaktifkan!</b>\n\n"
            "Silakan gunakan menu utama seperti biasa."
        )
        # Tampilkan menu lama seperti sebelumnya
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
        await query.edit_message_text(teks, reply_markup=reply_markup, parse_mode='HTML')
        return

    await query.edit_message_text(teks, parse_mode='HTML')

def get_user_mode(user_id):
    return user_mode.get(user_id, 'manual')

async def cek_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = get_user_mode(user_id)
    await update.message.reply_text(f"🔘 Mode aktif Anda saat ini adalah: {mode.upper()}")
            
