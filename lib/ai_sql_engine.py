import requests
import os
from lib.system_prompt import get_sql_context
from lib.google_sheets import cari_data_di_sheets  # Buat fungsi ini di lib/google_sheets.py

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
    if not query.lower().strip().startswith("select"):
        return "⚠️ Maaf, hanya query SELECT yang diperbolehkan."

    try:
        # Gantilah logika ini dengan pencarian di Google Sheets
        hasil = cari_data_di_sheets(query)

        if not hasil:
            return "Tidak ditemukan hasil untuk query tersebut."

        if isinstance(hasil, list):
            return "\n".join([f"{i+1}. {row}" for i, row in enumerate(hasil)])
        return hasil

    except Exception as e:
        print("❌ Sheet error:", e)
        return "⚠️ Terjadi kesalahan saat membaca dari Google Sheets."
