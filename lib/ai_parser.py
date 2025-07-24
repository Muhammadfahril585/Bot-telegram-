import os
import requests
import json
from lib.json_instruction_prompt import get_json_prompt

# 🔐 Ambil API key dari environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# 🔁 Daftar model prioritas yang akan dicoba
MODEL_PRIORITAS = [
    "tngtech/deepseek-r1t2-chimera:free",
    "microsoft/mai-ds-r1:free",
    "qwen/qwen3-235b-a22b-07-25",
    "qwen/qwen3-235b-a22b-07-25:free",
    "google/gemma-3n-e2b-it:free",
    "mistralai/mistral-nemo:free",
    "meta-llama/llama-4-maverick:free"
]

def ubah_pertanyaan_ke_json(pertanyaan: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/Alitqon_bot",  # opsional tapi bagus untuk branding
        "X-Title": "JSONQueryBot"
    }

    # 🔁 Coba semua model satu per satu
    for model in MODEL_PRIORITAS:
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": get_json_prompt()},
                {"role": "user", "content": pertanyaan}
            ]
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                     headers=headers, json=body, timeout=25)
            data = response.json()

            if "choices" in data:
                content = data["choices"][0]["message"]["content"]
                print(f"✅ JSON returned from model `{model}`: {content}")
                return json.loads(content)

            else:
                print(f"⚠️ Tidak ada response dari model {model}: {data}")

        except Exception as e:
            print(f"❌ Gagal dengan model {model}:", e)

    return {"error": "Semua model gagal menghasilkan JSON yang valid"}
