from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def tombol_navigasi(sebelumnya_callback: str):
    keyboard = [
        [
            InlineKeyboardButton("◀️ Menu Sebelumnya", callback_data=sebelumnya_callback),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="start")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def tombol_menu_utama():
    keyboard = [
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def tombol_rekap_bulanan():
    keyboard = [
        [
            InlineKeyboardButton("⬅️ Kembali", callback_data="portal"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="start")
        ],
        [
            InlineKeyboardButton("📄 Jadikan PDF", callback_data="buat_pdf_rekap")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
