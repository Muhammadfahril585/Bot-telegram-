import re

def ekstrak_entitas(pertanyaan: str) -> dict:
    pertanyaan = pertanyaan.lower()

    # Ambil nama santri (jika ada)
    nama_santri = None
    match_nama = re.search(r"(?:siapa|hafalan|santri|berada|dimana)?\s*([a-zA-Z ]+?)\s*(?:berada|di halaqah|hafalan|berapa)?", pertanyaan)
    if match_nama:
        nama_santri = match_nama.group(1).strip().title()

    # Ambil nama halaqah (jika ada)
    match_halaqah = re.search(r"halaqah\s+([a-zA-Z_ ]+)", pertanyaan)
    nama_halaqah = match_halaqah.group(1).strip().title() if match_halaqah else None

    # Ambil pekan
    match_pekan = re.search(r"pekan(?: ke|-)?\s*(\d+)", pertanyaan)
    pekan = int(match_pekan.group(1)) if match_pekan else None

    # Ambil bulan
    daftar_bulan = ["januari", "februari", "maret", "april", "mei", "juni", "juli",
                    "agustus", "september", "oktober", "november", "desember"]
    bulan = None
    for b in daftar_bulan:
        if b in pertanyaan:
            bulan = b.title()
            break

    return {
        "nama_santri": nama_santri,
        "halaqah": nama_halaqah,
        "pekan": pekan,
        "bulan": bulan
    }




