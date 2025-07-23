# lib/ai_sql_engine.py

import requests
from lib.system_prompt import get_sql_context

OPENROUTER_API_KEY = "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"

def buat_sql_dari_pertanyaan(pertanyaan: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/Alitqon_bot",
        "X-Title": "SQLQueryBot"
    }

    body = {
        "model": "tngtech/deepseek-r1t2-chimera:free",  # bisa ganti ke yang kamu aktifkan
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
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query)
        hasil = cursor.fetchall()
        kolom = [desc[0].lower() for desc in cursor.description]  # lowercase kolom
        cursor.close()
        conn.close()

        if not hasil:
            return "Tidak ditemukan hasil untuk query tersebut."

        # 👉 Tangani format daftar halaqah khusus
        if {"id", "nama", "ustadz"}.issubset(set(kolom)):
            hasil_format = "📋 *Daftar Halaqah PPTQ Al-Itqon:*\n"
            emoji_nomor = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "1️⃣1️⃣", "1️⃣2️⃣"]
            for i, row in enumerate(hasil):
                try:
                    nama = str(row[kolom.index("nama")])
                    ustadz = str(row[kolom.index("ustadz")])
                except (IndexError, ValueError):
                    continue
                emoji = emoji_nomor[i] if i < len(emoji_nomor) else f"{i+1}."
                hasil_format += f"{emoji} *{nama}* — Ustadz {ustadz}\n"
            return hasil_format.strip()

        # Format default
        baris = [", ".join(str(item) for item in row) for row in hasil]
        return "\n".join([f"{i+1}. {row}" for i, row in enumerate(baris)])

    except Exception as e:
        print("❌ DB SQL error:", e)
        return "⚠️ Terjadi kesalahan saat menjalankan query."
