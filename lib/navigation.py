from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def tombol_menu_utama():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="start")],
    ])
