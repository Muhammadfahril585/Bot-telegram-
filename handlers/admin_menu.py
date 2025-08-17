# handlers/admin_menu.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

ADMIN_MENU_CB = "admin_menu"

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Data Santri", callback_data="admin:data_santri")],
        [InlineKeyboardButton("📄 Lihat Semua Santri", callback_data="admin:lihat_semua")],
        [InlineKeyboardButton("🗓️ Lapor Pekanan", callback_data="admin:lapor")],
        [InlineKeyboardButton("☎️ Hubungi Admin", url="https://t.me/Laodefahril")],
    ])
    await q.edit_message_text(
        "🛡️ <b>Menu Admin</b>\nPilih salah satu fitur.\nSetiap fitur akan meminta <b>kata sandi</b> dahulu.",
        parse_mode="HTML",
        reply_markup=kb,
    )

def build_admin_menu_handlers():
    # Hanya satu handler: memunculkan submenu admin.
    # (Tiga tombol di submenu langsung ditangani oleh ConversationHandler masing-masing
    #  lewat entry point callback patterns: admin:data_santri, admin:lihat_semua, admin:lapor)
    return CallbackQueryHandler(show_admin_menu, pattern=r"^admin_menu$")
