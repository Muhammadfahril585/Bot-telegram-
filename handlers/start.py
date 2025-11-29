from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from handlers.tracker import track_user_activity
import asyncio
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


# =========================
#   /start
# =========================
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
        "👋 <b>Selamat datang di Pondok Pesantren Al-ITQON GOWA</b>\n\n"
        "Silakan pilih layanan yang ingin Anda gunakan.\n\n"
        "🧠 <i>Catatan:</i>\n"
        "Anda juga bisa langsung mengetik pertanyaan apa saja di kolom chat.\n"
        "Saya akan menjawab sebagai asisten virtual PPTQ AL-ITQON GOWA 😊"
    )

    keyboard = [
        [InlineKeyboardButton("🕌 PPTQ AL-ITQON (Menu Utama)", callback_data="menu_utama")],
        [InlineKeyboardButton("🕋 Jadwal Shalat Wahdah Islamiyah", callback_data="jadwal_shalat")],
        [InlineKeyboardButton("📖 Baca Qur'an", url="https://t.me/qidbot")],
        [InlineKeyboardButton("🛡️ Menu Admin", callback_data="admin_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_html(pesan, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_html(pesan, reply_markup=reply_markup)


# =========================
#   Handler tombol dari /start
# =========================
async def handle_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1) Jadwal shalat
    if data == "jadwal_shalat":
        # Import handler jadwal shalat di dalam fungsi untuk menghindari circular import
        from handlers.jadwal_sholat import buat_keyboard_huruf

        keyboard = buat_keyboard_huruf()

        await query.edit_message_text(
            "🕌 <b>JADWAL SHALAT BULANAN</b> 🕌\n"
            "<i>Wahdah Islamiyah</i>\n\n"
            "Silakan pilih huruf pertama dari nama wilayah yang Anda cari:",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    # 2) Menu utama PPTQ (mode_manual lama diganti jadi menu_utama)
    if data in ("menu_utama", "mode_manual"):
        teks = (
            "✅ <b>Selamat Datang di PPTQ AL-ITQON GOWA!</b>\n\n"
            "Silakan gunakan menu utama ini.\n\n"
            "🧠 Catatan: Anda tetap dapat menulis pertanyaan bebas di kolom chat, "
            "dan saya akan menjawab sebagai asisten virtual pondok."
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
        await query.edit_message_text(teks, reply_markup=reply_markup, parse_mode='HTML')
        return

    # 3) Kalau ada callback lain yang lama (misal mode_ai yang sudah dihapus tombolnya),
    #    kita jawab singkat saja untuk menghindari error ketika user klik pesan lama.
    if data == "mode_ai":
        await query.edit_message_text(
            "ℹ️ Saat ini bot selalu aktif sebagai asisten AI.\n"
            "Cukup kirimkan pertanyaan apa saja di kolom chat, "
            "dan saya akan menjawab sebisa mungkin.",
            parse_mode="HTML"
        )


# =========================
#   Fungsi lama untuk kompatibilitas
# =========================

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fungsi lama - sekarang tidak mengubah mode apa pun.
    Hanya memberi info bahwa bot selalu dalam mode AI.
    """
    await update.message.reply_text(
        "ℹ️ Pengaturan mode tidak diperlukan lagi.\n"
        "Bot ini selalu aktif sebagai asisten AI, dan menu manual tetap bisa digunakan lewat /start.",
    )


def get_user_mode(user_id):
    """
    Untuk kompatibilitas kode lama.
    Sekarang selalu mengembalikan 'ai' agar handler lain tidak bingung.
    """
    return "ai"


async def cek_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command /mode - hanya untuk memberi tahu user bahwa mode AI selalu aktif.
    """
    await update.message.reply_text(
        "🔘 Bot ini selalu dalam mode: AI + Menu Manual.\n"
        "Anda bisa memakai menu dengan /start, dan juga bebas bertanya di kolom chat.",
    )
