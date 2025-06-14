from datetime import datetime

def format_laporan_pekan(halaqah, ustadz, santri_data):
    bulan_map = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    now = datetime.now()
    bulan = bulan_map[now.month]
    pekan = (datetime.now().day - 1) // 7 + 1

    lines = [
        "*📖 Rekap Hafalan Pekanan*",
        f"*👥 Halaqah:* {halaqah}",
        f"*🧑‍🏫 Ustadz:* {ustadz}",
        f"*🗓️ Pekan:* {pekan} | *📅 Bulan:* {bulan}",
        "",
        "━━━━━━━━━━━━━━━━━━━━"
    ]

    for i, santri in enumerate(santri_data, 1):
        nama = santri["nama"]
        halaman = santri.get("halaman", 0)
        juz = santri.get("juz", 0)
        total_hafalan = int(santri.get("total_juz", 0))
        status_key = santri.get("status", "")

        # Mapping status
        if status_key == "hafalan_baru":
            status = "✅Tercapai" if halaman >= 3 else "❌Tidak Tercapai"
        elif status_key == "murojaah":
            status = "♻️Muroja'ah"
        elif status_key == "ujian":
            status = "📑Persiapan Ujian"
        elif status_key == "simaan":
            status = "📢Persiapan Sima'an"
        elif status_key == "sakit":
            status = "🤒Sakit"
        elif status_key == "izin":
            status = "📌Izin"
        else:
            status = "❓Tidak Diketahui"

        lines.append(
            f"{i}️⃣ *{nama}*\n"
            f"   📘 Hafalan Baru: {halaman} Halaman (Juz {juz})\n"
            f"   📌 Status: {status}\n"
            f"   📖 Total Hafalan: {total_hafalan} Juz\n"                                       )
        lines.append("━━━━━━━━━━━━━━━━━━━━")

    lines.append("_✨ Barakallahu fiikum. Semangat terus dalam menjaga Al-Qur'an!_")
    return "\n".join(lines)
