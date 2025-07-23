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
    # Hanya SELECT yang diizinkan
    if not query.lower().strip().startswith("select"):
        return "⚠️ Maaf, hanya query SELECT yang diperbolehkan."

    try:
        sheet = get_sheet("Halaqah Umar")  # ✅ Ganti sesuai kebutuhan
        all_data = sheet.get_all_values()
        headers = all_data[0]
        rows = all_data[1:]

        # Coba filter hasil berdasarkan kolom yang diminta
        # Contoh parsing sederhana: SELECT nama, ustadz WHERE ustadz = 'Ust. Hasan'
        if "*" in query.lower():
            # Tampilkan semua
            hasil = [", ".join(row) for row in rows]
        else:
            hasil = []
            for row in rows:
                gabungan = " ".join(row).lower()
                if all(kata.lower() in gabungan for kata in query.lower().replace("select", "").split()):
                    hasil.append(", ".join(row))

        if not hasil:
            return "🔍 Tidak ditemukan hasil yang cocok."

        return "\n".join([f"{i+1}. {h}" for i, h in enumerate(hasil[:10])])  # Maks 10 hasil

    except Exception as e:
        print("❌ GSheet error:", e)
        return "⚠️ Terjadi kesalahan saat membaca data Google Sheets."
