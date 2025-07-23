from utils.gsheet import get_sheet

def get_santri_terbanyak():
    sheet = get_sheet("Santri")
    data = sheet.get_all_records()
    santri_urut = sorted(data, key=lambda x: x.get("Hafalan", 0), reverse=True)
    return (santri_urut[0]["Nama"], santri_urut[0]["Hafalan"]) if santri_urut else None


def get_santri_dari_halaqah(nama_halaqah):
    sheet = get_sheet("Santri")
    data = sheet.get_all_records()
    return [row["Nama"] for row in data if row.get("Nama Halaqah", "").lower() == nama_halaqah.lower()]


def get_total_hafalan_santri(nama):
    sheet = get_sheet("Santri")
    data = sheet.get_all_records()
    for row in data:
        if row["Nama"].lower() == nama.lower():
            return row.get("Hafalan", 0)
    return None


def get_rekap_bulanan(bulan):
    sheet = get_sheet("Santri")
    data = sheet.get_all_records()
    hasil = []
    for row in data:
        total = 0
        for k, v in row.items():
            if isinstance(k, str) and bulan in k and "Pekan" in k:
                try:
                    total += int(v)
                except:
                    continue
        hasil.append((row["Nama"], total))
    return hasil


def get_santri_by_ustadz(nama_ustadz):
    halaqah_sheet = get_sheet("Daftar Halaqah")
    halaqah_data = halaqah_sheet.get_all_records()
    halaqah_ustadz = [row["Nama Halaqah"] for row in halaqah_data if row.get("Ustadz", "").lower() == nama_ustadz.lower()]

    santri_sheet = get_sheet("Santri")
    santri_data = santri_sheet.get_all_records()
    return [row["Nama"] for row in santri_data if row.get("Nama Halaqah") in halaqah_ustadz]


def cari_halaqah_terdekat(keyword):
    sheet = get_sheet("Daftar Halaqah")
    data = sheet.get_all_records()
    keyword = keyword.lower()

    for row in data:
        nama = row.get("Nama Halaqah", "").lower()
        if keyword in nama or keyword.replace(" ", "_") in nama:
            return row["Nama Halaqah"]
    return None
