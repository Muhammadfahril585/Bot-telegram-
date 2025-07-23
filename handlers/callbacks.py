from telegram import Update
from telegram.ext import ContextTypes
from handlers.daftar_halaqah import daftar_halaqah
#from handlers.rekapbulanan import handle_rekapbulanan_dinamis
from handlers.start import start

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data

    if callback_data == 'daftar_halaqah':
        await query.answer()
        await query.edit_message_text("Menampilkan daftar halaqah...")
        await daftar_halaqah(update, context)

    #elif callback_data == 'rekap_bulanan':
        #await query.answer()
       # await handle_rekapbulanan_dinamis(update, context)

    elif callback_data == 'lihat_santri':
        await query.answer()
        return

    elif callback_data == 'start':
        await query.answer()
        await query.delete_message()
        await start(update, context)
