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
