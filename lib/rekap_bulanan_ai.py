# lib/rekap_bulanan_ai.py

from utils.gsheet import client, spreadsheet_id

def ambil_data_rekap_bulanan_santri(nama_santri: str, bulan: str):
    try:
        sheet = client.open_by_key(spreadsheet_id).worksheet("Santri")
        data = sheet.get_all_values()
        header = data[0]
        bulan_col = header.index("Bulan")  # Kolom E
        pekan_col = header.index("Pekan")  # Kolom D
        total_col = header.index("Total Hafalan")  # Kolom N
        nama_col = header.index("Nama")  # Kolom A

        hasil = []
        for row in data[1:]:
            if len(row) <= total_col:
                continue  # skip baris tidak lengkap
            if row[nama_col].strip().lower() == nama_santri.strip().lower() and row[bulan_col].strip().lower() == bulan.strip().lower():
                pekan = row[pekan_col]
                total = row[total_col]
                hasil.append(f"📆 *{pekan}* — {total}")

        if not hasil:
            return f"⚠️ Tidak ditemukan rekap untuk *{nama_santri}* di bulan *{bulan.title()}*."

        teks = f"📊 *Rekap Bulanan Santri: {nama_santri.title()} - {bulan.title()}*\n\n"
        teks += "\n".join(hasil)
        return teks

    except Exception as e:
        print("❌ Gagal mengambil data rekap:", e)
        return "⚠️ Terjadi kesalahan saat mengambil data rekap."
