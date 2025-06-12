# handlers/struktur_organisasi.py

from telegram import Update
from telegram.ext import ContextTypes
from lib.navigation import tombol_navigasi

async def handle_struktur_organisasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pesan = (
        "🏢 *STRUKTUR ORGANISASI PONDOK PESANTREN AL-ITQON GOWA*\n\n"
        "*1. Ketua Yayasan*\n⬇️ H. Mansur Taswin, Lc., M.Ag\n\n"
        "*2. Penasehat Yayasan*\n⬇️ Ir. H. Idris Dg Nompo\n\n"
        "*3. Pimpinan Pondok*\n⬇️ H. Mansur Taswin, Lc., M.Ag\n\n"
        "*4. Kepala Sekolah TK*\n⬇️ Jumrianti, A.Md\n\n"
        "*5. Administrasi*\n"
        "   ├─ *Administrator* ⬇️ Hariansyah, S.Ip\n"
        "   └─ *Musyrif Umum* ⬇️ Syuaib Abd.Halim,Lc M.Phil\n\n"
        "*6. Divisi-Divisi*\n"
        "   ├─ *Divisi Kesatrian* ⬇️ Sumardi Asaf, S.pd.i\n"
        "   ├─ *Divisi Bahasa* ⬇️ Muhammad Rafli Hi Taher, S.H\n"
        "   ├─ *Divisi Tahfidz* ⬇️ Laode Muh. Fahril, S.H\n"
        "   ├─ *Divisi Ibadah* ⬇️ Muhammad Irwan, S.H\n"
        "   ├─ *Divisi Keamanan* ⬇️ Sumardi Asaf, S.pd.i\n"
        "   └─ *Divisi Kebersihan* ⬇️ Agus Salim\n\n"
        "*7. Tenaga Pengajar*\n"
        "   ├─ Suhartono, S.pd.i\n"
        "   ├─ Muhammad Tahir, S.H\n"
        "   ├─ Agus Salim\n"
        "   ├─ Syuaib Abdul Halim, Lc.,M.Phil\n"
        "   ├─ H. Ahmad Nasing, Lc\n"
        "   ├─ H. Ramli Sudar, Lc\n"
        "   ├─ Jihadi Sawaty, A.Md.Kep\n"
        "   ├─ Muhammad Irwan, S.H\n"
        "   ├─ Muhammad Rafli Hi Taher, S.H\n"
        "   ├─ Laode Muhammad Fahril, S.H\n"
        "   └─ Syakur Abbas, Lc\n\n"
        "_Semoga Allah memberkahi seluruh jajaran pengurus._\n\n"
        "_Barakallahu fiikum._"
    )

    await query.edit_message_text(
        text=pesan,
        parse_mode="Markdown",
        reply_markup=tombol_navigasi("tentang")
    )
