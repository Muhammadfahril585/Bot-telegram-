import requests
import os
from lib.system_prompt import get_sql_context
from utils.gsheet import get_sheet  # Import get_sheet dari utils

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def buat_sql_dari_pertanyaan(pertanyaan: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/Alitqon_bot",
        "X-Title": "SQLQueryBot"
    }

    body = {
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "messages": [
            {"role": "system", "content": get_sql_context()},
            {"role": "user", "content": pertanyaan}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=body, timeout=20)
        data = response.json()

        if "choices" in data:
            print("🧠 AI returned:", data["choices"][0]["message"]["content"])
            return data["choices"][0]["message"]["content"]
        else:
            print("❌ SQL error:", data)
            return None
    except Exception as e:
        print("❌ SQL Exception:", e)
        return None


def jalankan_query(query: str) -> str:
    query_lower = query.lower().strip()

    # 1. Jika bukan query SELECT (mungkin AI kasih jawaban langsung), kirim apa adanya
    if not query_lower.startswith("select"):
        if any(k in query_lower for k in ["santri", "halaqah", "ustadz", "jumlah", "total", "daftar"]):
            return query  # anggap ini jawaban langsung
        return "⚠️ Maaf, hanya query SELECT yang diperbolehkan."

    # 2. Deteksi sheet yang akan digunakan dari isi query
    if "daftar halaqah" in query_lower:
        sheet_name = "Daftar Halaqah"
    elif "data_santri" in query_lower:
        sheet_name = "DATA_SANTRI"
    elif "santri" in query_lower:
        sheet_name = "Santri"
    elif "halaqah" in query_lower:
        # Deteksi nama halaqah misalnya "Halaqah Umar bin Khattab"
        potensi = query_lower.split("halaqah")[-1].strip().title()
        sheet_name = potensi if potensi else "Santri"
    else:
        sheet_name = "Santri"  # default

    try:
        sheet = get_sheet(sheet_name)
        all_data = sheet.get_all_values()
        headers = all_data[0]
        rows = all_data[1:]

        # Jika SELECT *, tampilkan semua
        hasil = []
        if "*" in query_lower:
            hasil = [", ".join(row) for row in rows]
        else:
            for row in rows:
                gabungan = " ".join(row).lower()
                if all(kata in gabungan for kata in query_lower.replace("select", "").split()):
                    hasil.append(", ".join(row))

        if not hasil:
            return f"🔍 Tidak ditemukan hasil yang cocok di sheet *{sheet_name}*."

        return f"📄 Hasil dari *{sheet_name}*:\n" + "\n".join([f"{i+1}. {h}" for i, h in enumerate(hasil[:10])])

    except Exception as e:
        print("❌ GSheet error:", e)
        return f"⚠️ Terjadi kesalahan saat membaca data dari sheet *{sheet_name}*."
