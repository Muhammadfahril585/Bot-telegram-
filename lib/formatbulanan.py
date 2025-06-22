import re

def format_rekap_bulanan(db, bulan, halaqah):
    cursor = db.cursor()
    cursor.execute("""
        SELECT pekan, halaqah, isi_laporan
        FROM rekap_format_awal
        WHERE bulan = %s
        ORDER BY pekan ASC
    """, (bulan,))
    semua_data = cursor.fetchall()

    if not semua_data:
        cursor.close()
        return f"Tidak ditemukan laporan pada bulan ke-{bulan}."

    nama_bulan = convert_bulan(bulan)
    laporan_santri = {}

    for pekan, nama_halaqah_laporan, isi_laporan in semua_data:
        baris = isi_laporan.split("\n")

        for i in range(len(baris)):
            line = baris[i].strip()
            match_nama = re.match(r"^\d+[\️⃣.]*\s+\*(.+?)\*", line)
            if match_nama:
                nama_santri = match_nama.group(1).strip()
                halaman = 0
                status = "-"

                for j in range(1, 4):
                  if i + j < len(baris):
                     next_line = baris[i + j].strip()
                     if 'hafalan baru' in next_line.lower():
                         match_hal = re.search(r"(\d+)\s*Halaman", next_line, re.IGNORECASE)
                         if match_hal:
                            halaman = int(match_hal.group(1))
                     if 'status' in next_line.lower():
                         match_status = re.search(r"status\s*:\s*(.+)", next_line, re.IGNORECASE)
                         if match_status:
                            status = match_status.group(1).strip()

                if nama_santri not in laporan_santri:
                    laporan_santri[nama_santri] = {
                        "halaqah_terakhir": nama_halaqah_laporan,
                        "per_pekan": {},
                        "total_halaman": 0,
                        "total_juz": "-"
                    }

                laporan_santri[nama_santri]["halaqah_terakhir"] = nama_halaqah_laporan
                laporan_santri[nama_santri]["per_pekan"][f"Pekan {pekan}"] = {
                   "halaman": halaman,
                   "status": status
                }
                laporan_santri[nama_santri]["total_halaman"] += halaman

    hasil_laporan = {
        nama: data for nama, data in laporan_santri.items()
        if data["halaqah_terakhir"].lower() == halaqah.lower()
    }

    if not hasil_laporan:
        cursor.close()
        return f"Tidak ada santri tercatat di halaqah *{halaqah}* pada bulan {nama_bulan}."

    # Ambil halaqah_id dan ustadz
    cursor.execute("SELECT id, ustadz FROM halaqah WHERE LOWER(nama) = LOWER(%s)", (halaqah,))
    row = cursor.fetchone()
    halaqah_id, ustadz = row if row else (None, "Tidak diketahui")

    if halaqah_id:
        for nama, data in hasil_laporan.items():
            cursor.execute(
                "SELECT hafalan FROM santri WHERE nama = %s AND halaqah_id = %s",
                (nama, halaqah_id)
            )
            row = cursor.fetchone()
            if row:
                hafalan = float(row[0])
                data["total_juz"] = f"{int(hafalan) if hafalan % 1 == 0 else hafalan} Juz"

    cursor.close()

    # Format hasil teks
    if not re.match(r'(?i)ust(adz)?\.?\s', ustadz):
        ustadz = f"Ustadz {ustadz}"

    hasil = f"*📚 Rekap Hafalan Bulan {nama_bulan}*\n👥 *Halaqah: {halaqah}*\n👤 *{ustadz}*\n\n"
    for idx, (nama, data) in enumerate(hasil_laporan.items(), 1):
        hasil += "────────────────────\n"
        hasil += f"{idx}. *{nama}*\n"
        for pekan in sorted(data["per_pekan"].keys(), key=lambda x: int(x.split(" ")[1])):
          info = data["per_pekan"][pekan]
          hasil += f"🗓️ {pekan}: {info['halaman']} Halaman | Status: {info['status']}\n"
        hasil += f"📝 Total Hafalan Baru Bulan Ini: {data['total_halaman']} Halaman\n"
        hasil += f"📖 Total Hafalan: {data['total_juz']}\n"

    hasil += "────────────────────\n"
    hasil += "\n*📌 Keterangan:*\nJika tidak ada tambahan hafalan, tetap semangat! Setiap usaha dicatat oleh Allah.\n\n"
    hasil += "_Barakallahu fiikum, terus jaga semangat dan istiqamah!_"
    return hasil.strip()

def convert_bulan(bulan):
    nama = ['Januari','Februari','Maret','April','Mei','Juni',
            'Juli','Agustus','September','Oktober','November','Desember']
    return nama[bulan - 1] if 1 <= bulan <= 12 else "Bulan Tidak Valid"
