from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_db
from datetime import datetime
from lib.navigation import tombol_navigasi

PILIH_HALAQAH, TAMPIL_HALAQAH = range(2)

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

def bersihkan_strip(teks):
    return teks.replace("–", "-").replace("—", "-")

async def mulai_lihat_santri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Lanjutkan (Semua Halaqah)", callback_data="lanjutkan_santri")],
        [InlineKeyboardButton("🔍 Pilih Halaqah", callback_data="pilih_halaqah")]
    ]
    await update.callback_query.edit_message_text(
        "Silakan pilih salah satu opsi untuk melihat data santri:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PILIH_HALAQAH

async def handle_pilihan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lanjutkan_santri":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama FROM halaqah ORDER BY nama ASC")
        halaqah_list = cursor.fetchall()

        if not halaqah_list:
            await query.message.reply_text("⚠️ Belum ada halaqah yang terdaftar.")
            return ConversationHandler.END

        pesan = f"📋 *Daftar Seluruh Santri per Halaqah:*\n🗓️ _{get_tanggal_hari_ini()}_\n\n"

        for idx, (id_h, nama_h) in enumerate(halaqah_list):
            cursor.execute("SELECT nama, hafalan FROM santri WHERE halaqah_id = %s ORDER BY nama ASC", (id_h,))
            santri = cursor.fetchall()
            if not santri:
                continue

            pesan += f"👥 *{nama_h}* ({len(santri)} Santri)\n"
            for i, (nama, hafalan) in enumerate(santri, start=1):
                if hafalan == 0:
                    hafalan_str = "Tahsin"
                elif float(hafalan).is_integer():
                    hafalan_str = f"{int(hafalan)} juz"
                else:
                    hafalan_str = f"{hafalan:.1f} juz"
                pesan += f"   {i}. *{bersihkan_strip(nama)}* - _{bersihkan_strip(hafalan_str)}_\n"

            pesan += "\n───────✦───────\n\n"

        cursor.close()
        conn.close()

        await query.edit_message_text(
            pesan.strip(),
            parse_mode="Markdown",
            reply_markup=tombol_navigasi("portal")
        )
        return ConversationHandler.END

    elif query.data == "pilih_halaqah":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nama, ustadz FROM halaqah ORDER BY nama ASC")
        hasil = cursor.fetchall()
        cursor.close()
        conn.close()

        if not hasil:
            await query.message.reply_text("⚠️ Belum ada halaqah yang terdaftar.")
            return ConversationHandler.END

        keyboard = []
        for row in hasil:
            nama, ustadz = row
            label_halaqah = nama.replace("Halaqah_", "").replace("_", " ")
            label = f"{label_halaqah} ({ustadz.strip()})"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"show_{nama}")])

        await query.edit_message_text("Pilih halaqah yang ingin ditampilkan:",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        return TAMPIL_HALAQAH

async def tampilkan_santri_halaqah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    halaqah_nama = query.data.replace("show_", "")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.nama, s.hafalan FROM santri s
        JOIN halaqah h ON s.halaqah_id = h.id
        WHERE h.nama = %s
        ORDER BY s.nama ASC
    """, (halaqah_nama,))
    santri = cursor.fetchall()
    cursor.close()
    conn.close()

    if not santri:
        await query.message.reply_text(
            f"❌ Halaqah *{halaqah_nama}* tidak ditemukan atau belum ada santrinya.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    total = len(santri)
    nama_bersih = halaqah_nama.replace("Halaqah_", "").replace("_", " ")
    pesan = f"👥 *Santri Halaqah {nama_bersih}* ({total} Santri):\n🗓️ _{get_tanggal_hari_ini()}_\n\n"
    for i, (nama, hafalan) in enumerate(santri, start=1):
        if hafalan == 0:
            hafalan_str = "Tahsin"
        elif float(hafalan).is_integer():
            hafalan_str = f"{int(hafalan)} juz"
        else:
            hafalan_str = f"{hafalan:.1f} juz"
        pesan += f"   {i}. *{bersihkan_strip(nama)}* - _{bersihkan_strip(hafalan_str)}_\n"

    await query.edit_message_text(
        pesan.strip(),
        parse_mode="Markdown",
        reply_markup=tombol_navigasi("portal")
    )
    return ConversationHandler.END
