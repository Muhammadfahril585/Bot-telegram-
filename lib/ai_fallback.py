import requests
from lib.ai_context import get_system_context

OPENROUTER_API_KEY = "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"
                                                                                                                      # 🔁 Daftar model yang akan dicoba
MODEL_PRIORITAS = [
    "tngtech/deepseek-r1t2-chimera:free",
    "google/gemma-3n-e2b-it:free",
    "mistralai/mistral-nemo:free",
    "meta-llama/llama-4-maverick:free"
]

def tanyakan_ke_model(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/Alitqon_bot",
        "X-Title": "TelegramBot"
    }

    for i, model in enumerate(MODEL_PRIORITAS):
        body = {
            "model": model,
            "messages": [                                                                                                             {"role": "system", "content": get_system_context()},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            print(f"🔍 Mencoba model ke-{i+1}: {model}")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=20
            )
            data = response.json()

            if "error" in data:
                print(f"⚠️ Gagal dengan {model}: {data['error'].get('message', 'Unknown error')}")
                continue

            if "choices" not in data:
                print(f"📦 Respons tidak valid dari {model}: {data}")
                continue

            print(f"✅ Berhasil dengan model: {model}")
            if i > 0:
                return f"🤖 *Saya sedang beralih ke model cadangan karena model utama gagal.*\n\n" + data["choices"][>

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"❌ Error saat akses {model}:", e)
            continue

    return "⚠️ Maaf, semua model AI gagal merespon saat ini. Silakan coba beberapa saat lagi."
          
