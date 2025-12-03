# handlers/scribd.py
import re
import requests
import json
import tempfile
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

def load_cookies(file_path="cookie.json"):
    with open(file_path, 'r') as file:
        cookies_raw = json.load(file)
        if isinstance(cookies_raw, dict):
            return cookies_raw
        elif isinstance(cookies_raw, list):
            cookies = {}
            for cookie in cookies_raw:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
            return cookies
        else:
            raise ValueError("Cookies format tidak didukung.")

def extract_information(response_json):
    document = response_json.get('document', {})
    return {
        "title": document.get('title', 'Not Available'),
        "access_key": document.get('access_key', 'Not Available'),
        "author_name": document.get('author', {}).get('name', 'Not Available'),
        "receipt_url": response_json.get('receipt_url', 'Not Available')
    }

async def handle_scribd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Tolong sertakan URL Scribd setelah perintah /scribd")
        return

    url = context.args[0]
    match = re.search(r'scribd\.com/(document|doc|presentation)/(\d+)', url)
    if not match:
        await update.message.reply_text("❌ URL Scribd tidak valid")
        return

    document_id = match.group(2)
    first_url = f'https://www.scribd.com/doc-page/download-receipt-modal-props/{document_id}'

    try:
        cookies = load_cookies("cookie.json")

        # First request
        resp = requests.get(first_url, cookies=cookies)
        if resp.status_code != 200:
            await update.message.reply_text(f"⚠️ First request gagal: {resp.status_code}")
            return

        info = extract_information(resp.json())
        second_url = f"https://www.scribd.com/document_downloads/{document_id}/?secret_password={info['access_key']}&extension=pdf"

        # Second request
        resp2 = requests.get(second_url, cookies=cookies, allow_redirects=False)
        if resp2.status_code not in [301, 302]:
            await update.message.reply_text(f"⚠️ Second request gagal: {resp2.status_code}")
            return

        redirect_url = resp2.headers.get('Location')
        if not redirect_url:
            await update.message.reply_text("⚠️ Tidak ada redirect URL di second request")
            return

        # Third request
        resp3 = requests.get(redirect_url, cookies=cookies, allow_redirects=False)
        if resp3.status_code in [301, 302]:
            final_url = resp3.headers.get('Location')
        elif resp3.status_code == 200:
            # Sudah final, langsung pakai redirect_url
            final_url = redirect_url
        else:
            await update.message.reply_text(f"⚠️ Third request gagal: {resp3.status_code}")
            return

        # Kirim link + tombol
        text = (
            f"<b>Here is the Download Link ✅</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Title: {info['title']}\n"
            f"Author: {info['author_name']}\n"
            f"Main Url: <a href='{info['receipt_url']}'>Click Here</a>\n"
            f"Download Link: <a href='{final_url}'>Download Now</a>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Scribd Downloader integrated in your bot"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Download Now", url=final_url)]
        ])
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")

        # Langsung unduh PDF dan kirim ke chat
        pdf_resp = requests.get(final_url, cookies=cookies, stream=True)
        if pdf_resp.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                for chunk in pdf_resp.iter_content(chunk_size=8192):
                    tmpfile.write(chunk)
                tmpfile_path = tmpfile.name

            await update.message.reply_document(open(tmpfile_path, "rb"), filename=f"{info['title']}.pdf")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")
