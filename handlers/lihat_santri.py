from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime
from utils.gsheet import get_sheet
from lib.navigation import tombol_navigasi

def get_tanggal_hari_ini():
    bulan_dict = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    hari_dict = {
        0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
        4: "Jumat", 5: "Sabtu", 6: "Ahad"
    }

    now = datetime.now()
    hari = hari_dict[now.weekday()]
    tanggal = now.day
    bulan = bulan_dict[now.month]
    tahun = now.year

    return f"{hari}, {tanggal} {bulan} {tahun}"

# Fungsi utama
async def mulai_lihat_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.answer()
        sheet = get_sheet("Santri")
        values = sheet.get_all_values()

        # Ambil nama-nama halaqah setiap 16 baris (bukan 14)
        daftar_halaqah = []
        for i in range(len(values)):
          baris = values[i]
          if baris and "Halaqah" in baris[0]:
             nama_halaqah = baris[0].strip()
             daftar_halaqah.append((nama_halaqah, i))
        if not daftar_halaqah:
            await update.callback_query.message.reply_text("Tidak ada data halaqah ditemukan.")
            return
        # Buat tombol
        tombol = [
            [InlineKeyboardButton(text=nama, callback_data=f"lihat_santri:{index}")]
            for nama, index in daftar_halaqah
        ]
        reply_markup = InlineKeyboardMarkup(tombol)

        await update.callback_query.edit_message_text(
            "📚 Silakan pilih halaqah untuk melihat daftar santri:",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.callback_query.message.reply_text(f"Gagal mengambil data: {e}")

# Callback ketika tombol halaqah diklik
async def detail_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        data = query.data.split(":")
        if len(data) != 2:
            await update.callback_query.message.reply_text("Format data tidak valid.")
            return

        baris_awal = int(data[1])
        sheet = get_sheet("Santri")
        values = sheet.get_all_values()

        nama_halaqah = values[baris_awal][0].strip()
        nama_ustadz = values[baris_awal][1].strip() if len(values[baris_awal]) > 1 and values[baris_awal][1].strip() else "Belum terisi"
        tanggal_hari_ini = get_tanggal_hari_ini()
        jumlah_santri = 0

        pesan = (
            f"👥 *{nama_halaqah}*\n"
            f"Ustadz: {nama_ustadz}\n"
            f"📌 Jumlah Santri: {{JML}} orang\n"
            f"🗓️ {tanggal_hari_ini}\n\n"
        )

        # Data santri mulai dari baris_awal + 3 (setelah header)
        baris_santri = baris_awal + 2
        for i in range(baris_santri, baris_awal + 15):  # 13 santri maks
            if i >= len(values):
                break
            row = values[i]
            if not row[0].strip():
                continue
            nama_santri = row[0]
            hafalan = row[1] if len(row) > 1 else "-"
            juz = row[2] if len(row) > 2 else "-"
            pesan += f"👤 *{nama_santri}*\n  Hafalan: {hafalan}\n  Juz: {juz}\n\n"
            jumlah_santri += 1

        # Masukkan jumlah santri aktual ke template
        pesan = pesan.replace("{JML}", str(jumlah_santri))

        await query.edit_message_text(
            pesan,
            parse_mode="Markdown",
            reply_markup=tombol_navigasi("portal")
        )

    except Exception as e:
        await update.callback_query.edit_message_text(
            text=f"⚠️ Terjadi kesalahan saat mengambil data halaqah:\n`{e}`",
            parse_mode="Markdown",
            reply_markup=tombol_navigasi("portal")
    )
