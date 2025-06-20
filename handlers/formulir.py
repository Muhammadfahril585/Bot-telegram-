from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from database import get_db
import re

FORMULIR = 0

async def kirim_formulir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👤Nama: \n"
        "NIS: \n"
        "NIK: \n"
        "NO.KK: \n"
        "TTL: , \n"
        "Jenis Kelamin: \n"
        "Agama: \n"
        "Anak ke: \n"
        "Alamat: \n"
        "Kecamatan: \n"
        "Kabupaten: \n"
        "Provinsi: \n"
        "Kelas Saat Ini: \n"
        "Angkatan: \n"
        "\n🏫Sekolah Asal:\n"
        "- Nama: \n"
        "- NPNS: \n"
        "- Lokasi: \n"
        "- Tahun Lulus: \n"
        "- Provinsi: \n"
        "\n🧔Ayah:\n"
        "- Nama: \n"
        "- TTL: , \n"
        "- NIK: \n"
        "- Pendidikan: \n"
        "- Pekerjaan: \n"
        "\n🧕Ibu:\n"
        "- Nama: \n"
        "- TTL: , \n"
        "- NIK: \n"
        "- Pendidikan: \n"
        "- Pekerjaan: \n"
    )
    await update.message.reply_text("Silakan isi formulir berikut, lalu kirim balik setelah diisi:\n\n" + text)
    return FORMULIR

async def proses_formulir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.text

    def extract(pattern):
        match = re.search(pattern, data)
        return match.group(1).strip() if match else ''

    nama = extract(r"👤Nama: (.+)")
    nis = extract(r"NIS: (.+)")
    nik = extract(r"NIK: (.+)")
    kk = extract(r"NO.KK: (.+)")
    ttl = extract(r"TTL: (.+), (\d{2}-\d{2}-\d{4})")
    tempat_lahir, tanggal_lahir = ttl if ttl else ('', '')
    jk = extract(r"Jenis Kelamin: (.+)")
    agama = extract(r"Agama: (.+)")
    anak_ke = extract(r"Anak ke: (.+)")
    alamat = extract(r"Alamat: (.+)")
    kecamatan = extract(r"Kecamatan: (.+)")
    kabupaten = extract(r"Kabupaten: (.+)")
    provinsi = extract(r"Provinsi: (.+)")
    kelas = extract(r"Kelas Saat Ini: (.+)")
    angkatan = extract(r"Angkatan: (.+)")

    ayah_nama = extract(r"Ayah:\n- Nama: (.+)")
    ayah_ttl = extract(r"Ayah:\n.*?- TTL: (.+), (\d{2}-\d{2}-\d{4})")
    ayah_tempat_lahir, ayah_tanggal_lahir = ayah_ttl if ayah_ttl else ('', '')
    ayah_nik = extract(r"- NIK: (.+)")
    ayah_pendidikan = extract(r"- Pendidikan: (.+)")
    ayah_pekerjaan = extract(r"- Pekerjaan: (.+)")

    ibu_nama = extract(r"Ibu:\n- Nama: (.+)")
    ibu_ttl = extract(r"Ibu:\n.*?- TTL: (.+), (\d{2}-\d{2}-\d{4})")
    ibu_tempat_lahir, ibu_tanggal_lahir = ibu_ttl if ibu_ttl else ('', '')
    ibu_nik = extract(r"Ibu:\n.*?- NIK: (.+)")
    ibu_pendidikan = extract(r"Ibu:\n.*?- Pendidikan: (.+)")
    ibu_pekerjaan = extract(r"Ibu:\n.*?- Pekerjaan: (.+)")

    jenjang = kelas.split()[0] if kelas else ''
    tingkat = int(kelas.split()[1]) if len(kelas.split()) > 1 else 0

    conn = get_db()
    cur = conn.cursor()

    # Santri nama
    cur.execute("INSERT INTO santri_nama (nama_lengkap) VALUES (%s) RETURNING id", (nama,))
    santri_id = cur.fetchone()[0]

    # Santri data pribadi
    cur.execute("""
        INSERT INTO santri_data_pribadi (
            santri_nama_id, nis, nik, nomor_kk, tempat_lahir, tanggal_lahir,
            jenis_kelamin, agama, anak_ke, alamat, kecamatan, kabupaten, provinsi
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        santri_id, nis, nik, kk, tempat_lahir, tanggal_lahir, jk, agama,
        anak_ke, alamat, kecamatan, kabupaten, provinsi
    ))

    # Wali
    cur.execute("""
        INSERT INTO wali (
            santri_nama_id,
            ayah_nama, ayah_tempat_lahir, ayah_tanggal_lahir, ayah_nik, ayah_pendidikan, ayah_pekerjaan,
            ibu_nama, ibu_tempat_lahir, ibu_tanggal_lahir, ibu_nik, ibu_pendidikan, ibu_pekerjaan
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        santri_id, ayah_nama, ayah_tempat_lahir, ayah_tanggal_lahir, ayah_nik, ayah_pendidikan, ayah_pekerjaan,
        ibu_nama, ibu_tempat_lahir, ibu_tanggal_lahir, ibu_nik, ibu_pendidikan, ibu_pekerjaan
    ))

    # Kelas
    cur.execute("INSERT INTO kelas (santri_nama_id, jenjang, tingkat) VALUES (%s, %s, %s)",
                (santri_id, jenjang, tingkat))

    # Angkatan
    cur.execute("INSERT INTO angkatan (santri_nama_id, angkatan) VALUES (%s, %s)",
                (santri_id, angkatan))

    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text("✅ Data berhasil disimpan.")
    return ConversationHandler.END

formulir_handler = ConversationHandler(
    entry_points=[CommandHandler('formulir_santri', kirim_formulir)],
    states={
        FORMULIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_formulir)],
    },
    fallbacks=[]
)
