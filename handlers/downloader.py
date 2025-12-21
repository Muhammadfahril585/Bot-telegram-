import subprocess
import os
import yt_dlp
import asyncio

async def download_video_handler(update, context):
    url = update.message.text
    chat_id = update.effective_chat.id
    
    # Kirim status awal ke user
    status_msg = await update.message.reply_text("🔍 Sedang mencari video...")

    # Lokasi file sementara
    output_filename = f"video_{chat_id}.mp4"

    try:
        # 1. KONFIGURASI YT-DLP (SCRAPER)
        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Ambil mp4 terbaik
            'outtmpl': 'input_video.%(ext)s',
            'quiet': True,
            'max_filesize': 45 * 1024 * 1024, # Limit 45MB agar aman buat Telegram
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await status_msg.edit_text("⏳ Sedang mendownload & memproses...")
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url', None)

        if not video_url:
            return await status_msg.edit_text("❌ Gagal mendapatkan link video.")

        # 2. PROSES DENGAN FFMPEG (SUBPROCESS)
        # Kita kompres agar video playable di semua HP & size kecil
        command = [
            'ffmpeg',
            '-i', video_url,
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '28',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',
            output_filename
        ]

        # Menjalankan FFMPEG secara non-blocking
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        # 3. KIRIM KE TELEGRAM
        await status_msg.edit_text("📤 Mengirim video...")
        with open(output_filename, 'rb') as video:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video,
                caption=f"✅ Berhasil didownload!\n📌 Sumber: {info.get('title', 'Video')}"
            )

    except Exception as e:
        await status_msg.edit_text(f"❌ Terjadi kesalahan: {str(e)}")
    
    finally:
        # Hapus file sampah agar Render tidak penuh
        if os.path.exists(output_filename):
            os.remove(output_filename)
        if os.path.exists('input_video.mp4'):
            os.remove('input_video.mp4')
