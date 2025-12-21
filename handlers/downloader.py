import os
import re
import requests
import subprocess
import asyncio
from bs4 import BeautifulSoup

# --- UTILS: EKSTRAKSI ID & CLEANING ---
def get_youtube_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})"
    ]
    for p in patterns:
        match = re.search(p, url)
        if match: return match.group(1)
    return None

# --- CORE HANDLER ---
async def download_video_handler(update, context):
    url = update.message.text
    chat_id = update.effective_chat.id
    status_msg = await update.message.reply_text("🔍 Mengecek link...")

    try:
        # 1. TIKTOK LOGIC (Translasi dari scraper.js: tikwm)
        if "tiktok.com" in url:
            await status_msg.edit_text("⏳ Mendownload dari TikTok...")
            res = requests.post("https://www.tikwm.com/api/", data={'url': url, 'hd': 1}).json()
            if res.get('data'):
                video_url = res['data']['play']
                caption = res['data'].get('title', 'TikTok Video')
                return await send_url_video(context, chat_id, video_url, caption, status_msg)

        # 2. FACEBOOK LOGIC (Translasi dari scraper.js: getmyfb)
        elif "facebook.com" in url or "fb.watch" in url:
            await status_msg.edit_text("⏳ Mendownload dari Facebook...")
            headers = {'hx-current-url': 'https://getmyfb.com/', 'hx-request': 'true'}
            res = requests.post('https://getmyfb.com/process', data={'id': url, 'locale': 'en'}, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            links = soup.find_all('a', href=True)
            video_url = next((l['href'] for l in links if "download" in l.get('class', []) or "btn" in l.get('class', [])), None)
            if video_url:
                return await send_url_video(context, chat_id, video_url, "Facebook Video", status_msg)

        # 3. INSTAGRAM LOGIC (Translasi dari scraper.js: yt1s)
        elif "instagram.com" in url:
            await status_msg.edit_text("⏳ Mendownload dari Instagram...")
            res = requests.post('https://yt1s.io/api/ajaxSearch', data={'q': url, 'w': '', 'p': 'home', 'lang': 'en'}).json()
            # yt1s mengembalikan HTML di field 'data', kita parse
            soup = BeautifulSoup(res.get('data', ''), 'html.parser')
            video_url = soup.find('a', {'class': 'btn-premium'})['href']
            if video_url:
                return await send_url_video(context, chat_id, video_url, "Instagram Video", status_msg)

        # 4. YOUTUBE LOGIC (Bypass Bypass IP Render)
        elif "youtube.com" in url or "youtu.be" in url:
            await status_msg.edit_text("⏳ Memproses YouTube (Bypass Mode)...")
            output_file = f"yt_{chat_id}.mp4"
            
            # Gunakan yt-dlp dengan client iOS untuk menghindari 'Sign in to confirm'
            # Kita langsung download dan pipe ke ffmpeg untuk kompresi agar hemat RAM
            cmd = [
                'yt-dlp',
                '-g', # Ambil URL mentah saja
                '-f', 'mp4[height<=720]', # Batasi resolusi agar tidak crash di Render
                '--extractor-args', 'youtube:player_client=ios',
                url
            ]
            
            raw_url = subprocess.check_output(cmd).decode('utf-8').strip()
            
            # Proses kompresi ringan agar video "Playable" di Telegram
            ffmpeg_cmd = [
                'ffmpeg', '-i', raw_url, 
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '32', 
                '-c:a', 'aac', '-fs', '49M', # Batasan 49MB (Limit Telegram)
                '-y', output_file
            ]
            subprocess.run(ffmpeg_cmd)
            
            with open(output_file, 'rb') as f:
                await context.bot.send_video(chat_id=chat_id, video=f, caption="YouTube Downloaded ✅")
            
            os.remove(output_file)
            return await status_msg.delete()

        else:
            await status_msg.edit_text("❌ Maaf, link platform ini belum didukung.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Terjadi kesalahan: {str(e)[:100]}...")

# --- HELPER FUNCTIONS ---
async def send_url_video(context, chat_id, video_url, caption, status_msg):
    """Mengirim video langsung via URL (Sangat cepat & hemat RAM server)"""
    try:
        await context.bot.send_video(chat_id=chat_id, video=video_url, caption=caption)
        await status_msg.delete()
    except Exception:
        # Jika gagal kirim via URL, coba download dulu ke server baru kirim
        await status_msg.edit_text("📥 Sedang memproses file...")
        file_path = f"temp_{chat_id}.mp4"
        r = requests.get(video_url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
        
        with open(file_path, 'rb') as f:
            await context.bot.send_video(chat_id=chat_id, video=f, caption=caption)
        os.remove(file_path)
        await status_msg.delete()
