from datetime import datetime

def format_laporan_pekan(halaqah, ustadz, santri_data):
    bulan_map = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    now = datetime.now()
    bulan = bulan_map[now.month]
    pekan = (now.day - 1) // 7 + 1

    ustadz = ustadz.replace("Ustadz ", "").strip()
    lines = [
        "*📖 Rekap Hafalan Pekanan*",
        f"*👥 Halaqah:* {halaqah}",
        f"*🧑‍🏫 Ustadz:* {ustadz}",
        f"*🗓️ Pekan:* {pekan} | *📅 Bulan:* {bulan}",
        "", "━━━━━━━━━━━━━━━━━━━━"
    ]

    for i, s in enumerate(santri_data, 1):
        nama = s["nama"]
        halaman = s.get("halaman", 0)
        juz = s.get("juz", 0)
        total = int(s.get("total_juz", 0))
        status = s.get("status")

        if status == "hafalan_baru":
            status_str = "✅Tercapai" if halaman >= 3 else "❌Tidak Tercapai"
        elif status == "tahsin":
            status_str = "📚Tahsin"
        elif status == "murojaah":
            status_str = "♻️Muroja'ah"
        elif status == "ujian":
            status_str = "📑Persiapan Ujian"
        elif status == "simaan":
            status_str = "📢Persiapan Sima'an"
        elif status == "sakit":
            status_str = "🤒Sakit"
        elif status == "izin":
            status_str = "📌Izin"
        else:
            status_str = "❓Tidak Diketahui"

        lines.append(
            f"{i}️⃣ *{nama}*\n"
            f"   📘 Hafalan Baru: {halaman} Halaman" + (f" (Juz {juz})" if status not in ["sakit", "izin"] else "") + "\n"
            f"   📌 Status: {status_str}\n"
            f"   📖 Total Hafalan: {total} Juz"
        )
        lines.append("━━━━━━━━━━━━━━━━━━━━")

    lines.append("_✨ Barakallahu fiikum. Semangat terus dalam menjaga Al-Qur'an!_")
    return "\n".join(lines)
