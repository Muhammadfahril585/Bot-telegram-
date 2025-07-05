# Gunakan base image Python
FROM python:3.11-slim

# Install ffmpeg dan dependensi sistem lainnya
RUN apt-get update && apt-get install -y ffmpeg

# Set direktori kerja
WORKDIR /app

# Copy semua file project ke dalam image
COPY . .

# Install requirements Python
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan bot saat container start
CMD ["python", "app.py"]
