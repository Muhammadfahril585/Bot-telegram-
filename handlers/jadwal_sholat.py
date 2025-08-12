import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from weasyprint import HTML
import tempfile
from collections import defaultdict

KOTA_ID = {
    "aceh": 1, "alahan panjang": 2, "amboina": 3, "ambon": 4, "amuntai": 5, "anyer": 6,
    "arosbaya": 7, "baitul musthofa": 265, "baliage": 9, "balikpapan": 10, "banda aceh": 11, "bandar lampung": 12,
    "bandung": 13, "banggai": 14, "bangka": 15, "bangkalan": 16, "bangkinan": 17, "bangko": 18,
    "banjar": 19, "banjarmasin": 20, "banjarnegara": 21, "banten": 22, "bantul": 23, "banyumas": 24,
    "banyuwangi": 25, "barabai": 26, "batang": 27, "baturaja": 28, "batusangkar": 29, "baubau": 30,
    "bekasi": 31, "bengkalis": 32, "bengkulu": 33, "bima": 34, "binjai": 35, "bireun": 36,
    "blangkajeren": 37, "blega": 38, "blitar": 39, "blora": 40, "bogor": 41, "bojonegoro": 42,
    "bondowoso": 43, "bontang": 44, "bonthain": 45, "boyolali": 46, "brebes": 47, "bukittinggi": 48,
    "bulukumba": 49, "bungah": 50, "buntok": 51, "calang": 52, "cepu": 53, "ciamis": 54,
    "cianjur": 55, "cibinong": 56, "cijulang": 57, "cikajang": 58, "cilacap": 59, "cilegon": 60,
    "cimahi": 61, "cirebon": 62, "curup": 63, "demak": 64, "denpasar": 65, "dilli": 66,
    "dobo": 67, "dompu": 68, "donggala": 69, "dumai": 70, "durjan": 71, "endeh": 72,
    "enrekang": 73, "fakfak": 74, "garut": 75, "gebang arosbaya": 76, "gebang bangkalan": 77, "glagah": 78,
    "glagah lamongan": 79, "gombong": 80, "gorontalo": 81, "grajakan": 82, "gresik condrodipo": 83, "gresik": 84,
    "gunung sitoli": 85, "idi": 86, "indramayu": 87, "jakarta": 88, "jambi": 89, "jampea": 90,
    "jatinegara": 91, "jayapura": 92, "jember": 93, "jeneponto": 94, "jepara": 95, "jombang": 96,
    "kabanjahe": 97, "kadungdung": 98, "kalabahi": 99, "kalianda": 100, "kandangan": 101, "kangean": 102,
    "karang nunggal": 103, "karanganyar": 104, "karawang": 105, "kayuagung": 106, "kebayoran": 107, "kebumen": 108,
    "kediri": 109, "kefamenanu": 110, "kendal": 111, "kendari": 112, "ketapang kalimantan": 113, "ketapang madura": 114,
    "klaten": 115, "kolaka": 116, "kotabaru": 117, "kotabumi": 118, "kotamobago": 119, "kraksan": 120,
    "krui": 121, "kuala kapuas": 122, "kuala simpang": 123, "kuala tungkal": 124, "kudus": 125, "kuningan": 126,
    "kupang": 127, "kutacane": 128, "kutai": 129, "labuha": 130, "labuhan": 131, "lahat": 132,
    "lamongan": 133, "langsa": 134, "larantuka": 135, "lhokseimawe": 136, "lhoktukon": 137, "lubuk linggau": 138,
    "lubuk sikaping": 139, "lumajang": 140, "luwuk": 141, "madiun": 142, "magetan": 143, "majalengka": 144,
    "majene": 145, "makale": 146, "malang": 147, "malingping": 148, "mamuju": 149, "manado": 150,
    "maninjau": 151, "manokwari": 152, "manyar": 153, "marabahan": 154, "maros": 155, "martapura": 156,
    "mataram": 157, "maumere": 158, "medan": 159, "menado": 160, "merak": 161, "merauke": 162,
    "metro": 163, "meulaboh": 164, "meureudeu": 165, "mojokerto": 166, "morotai": 167, "muara bulian": 168,
    "muara bungo": 169, "muara enim": 170, "muara labuh": 171, "muara tewe": 172, "mukomuko": 173, "nabire": 174,
    "negara bali": 175, "negara kalsel": 176, "nganjuk": 177, "ngawi": 178, "nunukan": 179, "pacitan": 180,
    "padang": 181, "padang panjang": 182, "padang sidampuan": 183, "padang sidempuan": 184, "pagantenan": 185, "painan": 186,
    "pakan baru": 187, "palangkaraya": 188, "palembang": 189, "palopo": 190, "palu": 191, "pamanukan": 192,
    "pamekasan": 193, "pameungpeuk": 194, "pandegelang": 195, "pangkajene": 196, "pangkal pinang": 197, "pangkalan bun": 198,
    "parepare": 199, "pariaman": 200, "pasir pangarayan": 201, "pasuruan": 202, "pati": 203, "payakumbuh": 204,
    "pekalongan": 205, "pekanbaru": 206, "pelabuhan ratu": 207, "pemalang": 208, "pematang siantar": 209, "pengalengan": 210,
    "pinrang": 211, "polewali": 212, "ponorogo": 213, "pontianak": 214, "poso": 215, "ppmi assalaam": 216,
    "probolinggo": 217, "purbalingga": 218, "purwakarta": 219, "purwodadi": 220, "purwokerto": 221, "purworejo": 222,
    "putusibah": 223, "raba": 224, "raha": 225, "rangkasbitung": 226, "rantau": 227, "rantau prapat": 228, "rembang": 229, "rengat": 230, "ruteng": 231, "sabang": 232, "salatiga": 233, "samarinda": 234,
    "sambas": 235, "sampang": 236, "sampit": 237, "sanggau": 238, "sawah lunto": 239, "sekayu": 240,
    "selat panjang": 241, "selong": 242, "semarang": 243, "sepuluh": 244, "serang": 245, "sibolga": 246,
    "sidenreng rappang": 247, "sidikalang": 248, "sidoarjo": 249, "sigli": 250, "sijunjung": 251, "sinabang": 252,
    "sindang barang": 253, "singaraja": 254, "singkawang": 255, "singkil": 256, "sinjai": 257, "sintang": 258,
    "situbondo": 259, "sleman": 260, "solo": 261, "solok": 262, "sorong": 263, "sragen": 264,
    "subang": 266, "sukabumi": 267, "sukoharjo": 268, "suliki": 269, "sumbawa besar": 270, "sumedang": 271,
    "sumenep": 272, "sunbgu minasa": 273, "sungai liat": 274, "sungai penuh": 275, "surabaya": 276, "surakarta": 277,
    "tabanan": 278, "tahuna": 279, "takalar": 280, "takengeun": 281, "takengon": 282, "talu": 283,
    "tambelangan": 284, "tanah grogot": 285, "tangerang": 286, "tanjung balai": 287, "tanjung kalsel": 288, "tanjung karang": 289,
    "tanjung kodok": 290, "tanjung pandan": 291, "tanjung pinang": 292, "tanjung priok": 293, "tanjung redep": 294, "tanjung selor": 295,
    "tapak tuan": 296, "tarutung": 297, "tasikmalaya": 298, "tebing tinggi": 299, "tegal": 300, "teluk betung": 301,
    "temanggung": 302, "tembilahan": 303, "ternate": 304, "tobelo": 305, "tolitoli": 306, "torjun": 307,
    "trenggalek": 308, "tuban": 309, "tulungagung": 310, "ujung kulon": 311, "ujung_pandang": 312, "ujung pangkah": 314,
    "ujung pandang": 315, "makassar": 316, "waikabubak": 317, "waingapu": 318, "wamena": 319, "waru": 320,
    "watanpone": 321, "watansoppeng": 322, "wates": 323, "wonogiri": 324, "wonosari": 325, "wonosobo": 326,
    "yogyakarta": 327, "tarakan": 328, "bunyu": 329, "bulungan": 330, "barru": 331, "soroako": 332,
    "selayar": 333, "gowa": 334, "wajo": 335, "dpw aceh": 336, "masjid ar-rahmah takalar": 337, "masjid imam muslim takalar": 338,
    "mamuju (masjid nurul johar makkasau)": 339, "bombana": 340, "luwu": 341, "luwu utara": 342, "luwu timur": 343, "bone": 344,
    "wahdah islamiyah konawe": 345, "kabupaten buol sulawesi tengah": 346, "kecamatan melonguane": 347
}

BASE_URL = "https://krfdsawi.stiba.ac.id/"

# Fungsi untuk mengelompokkan wilayah berdasarkan huruf pertama
def kelompokkan_wilayah():
    kelompok = defaultdict(list)
    for kota in sorted(KOTA_ID.keys()):
        huruf_pertama = kota[0].upper()
        kelompok[huruf_pertama].append(kota)
    return dict(kelompok)

# Fungsi untuk membuat keyboard huruf abjad
def buat_keyboard_huruf():
    kelompok = kelompokkan_wilayah()
    keyboard = []
    row = []
    
    for i, huruf in enumerate(sorted(kelompok.keys())):
        row.append(InlineKeyboardButton(f"{huruf}", callback_data=f"huruf:{huruf}"))
        # Buat baris baru setiap 5 tombol
        if (i + 1) % 5 == 0:
            keyboard.append(row)
            row = []
    
    # Tambahkan sisa tombol jika ada
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

# Fungsi untuk membuat keyboard daftar wilayah berdasarkan huruf
def buat_keyboard_wilayah(huruf):
    kelompok = kelompokkan_wilayah()
    wilayah_list = kelompok.get(huruf, [])
    
    keyboard = []
    for kota in wilayah_list:
        keyboard.append([InlineKeyboardButton(kota.title(), callback_data=f"wilayah:{kota}")])
    
    # Tombol kembali ke menu huruf
    keyboard.append([InlineKeyboardButton("⬅️ Kembali ke Menu Huruf", callback_data="kembali_huruf")])
    
    return InlineKeyboardMarkup(keyboard)

# ==== Fungsi Kirim PDF ====
async def kirim_jadwal_pdf(update, context, kota: str):
    url = BASE_URL + "domain/krfdsawi.stiba.ac.id/halaman_jadwal/jadwal_imsakiyah_proses.php"
    payload = {"wilayah": KOTA_ID[kota]}
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.post(url, data=payload, headers=headers, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # Perbaiki semua link CSS & gambar jadi absolute URL
    for link in soup.find_all("link", href=True):
        link["href"] = urljoin(BASE_URL, link["href"])
    for img in soup.find_all("img", src=True):
        img["src"] = urljoin(BASE_URL, img["src"])

    # Ambil tabel jadwal
    content_div = soup.find("div", id="toPrint1")
    if not content_div:
        await update.effective_message.reply_text("⚠️ Gagal menemukan konten jadwal.")
        return

    # Kop surat
    kop_html = f"""
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 5px;">
      <tr>
        <td style="width: 80px; text-align: center; vertical-align: middle;">
          <img src="{BASE_URL}domain/krfdsawi.stiba.ac.id/logo.png" style="width: 70px; height: auto;">
        </td>
        <td style="vertical-align: middle; text-align: left;">
          <p style="font-size: 20px; font-weight: bold; margin: 0;">DEWAN SYARIAH</p>
          <p style="font-size: 14px; margin: 0;">Wahdah Islamiyah</p>
          <p style="font-size: 11px; margin: 0;">Jl. Inspeksi PAM Manggala Raya Makassar 90234</p>
          <p style="font-size: 11px; margin: 0;">Website: krfdsawi.stiba.ac.id | Email: krfdsawi@stiba.ac.id</p>
        </td>
      </tr>
    </table>
    <hr>
    """

    # CSS supaya ukuran F4 dan tabel lebar penuh
    custom_css = """
    <style>
        @page {
            size: 210mm 330mm; /* Ukuran F4 */
            margin: 10mm;
        }
        body {
            font-family: "Times New Roman", serif;
            font-size: 12pt;
        }
        table {
            width: 100% !important;
            border-collapse: collapse !important;
        }
        table th, table td {
            border: 1px solid #000 !important;
            padding: 4px !important;
            font-size: 12px;
        }
        table.table-bordered {
            margin: 0 auto !important;
        }
    </style>
    """

    # HTML final
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        {custom_css}
    </head>
    <body>
        {kop_html}
        {str(content_div)}
    </body>
    </html>
    """

    # Simpan ke PDF
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    HTML(string=full_html, base_url=BASE_URL).write_pdf(tmp_pdf.name)

    await update.effective_message.reply_document(
        document=open(tmp_pdf.name, "rb"),
        filename=f"jadwal_{kota}.pdf",
        caption=f"📄 Jadwal Shalat Bulanan - {kota.capitalize()}"
    )

# Fungsi untuk menampilkan jadwal sholat
async def tampilkan_jadwal_sholat(update, context, kota: str):
    url = BASE_URL + "domain/krfdsawi.stiba.ac.id/halaman_jadwal/jadwal_imsakiyah_proses.php"
    payload = {"wilayah": KOTA_ID[kota]}
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.post(url, data=payload, headers=headers, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    judul = soup.find("font", style=lambda v: v and "font-size:16px" in v)
    judul_text = judul.get_text(strip=True) if judul else f"Jadwal Shalat Bulanan - {kota.capitalize()}"

    table = soup.find("table", class_="table-bordered")
    if not table:
        await update.effective_message.reply_text("⚠️ Tabel jadwal tidak ditemukan.")
        return

    hari_list = []
    for tr in table.find("tbody").find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) == 7:
            tanggal, magrib, isya, subuh, duha, zuhur, asar = cols
            teks_hari = (
                f"{tanggal}\n"
                f"🌅 Subuh : {subuh}\n"
                f"🌞 Duha  : {duha}\n"
                f"🏙 Zuhur : {zuhur}\n"
                f"🌇 Asar  : {asar}\n"
                f"🌆 Maghrib : {magrib}\n"
                f"🌃 Isya : {isya}\n"
                "────────────────\n"
            )
            hari_list.append(teks_hari)

    keyboard = [
        [InlineKeyboardButton("📄 Download PDF", callback_data=f"jadwalpdf:{kota}")],
        [InlineKeyboardButton("🔄 Pilih Wilayah Lain", callback_data="kembali_huruf")]
    ]

    if len(hari_list) > 15:
        await update.effective_message.reply_text(f"📅 *{judul_text}*\n\n{''.join(hari_list[:15])}", parse_mode="Markdown")
        await update.effective_message.reply_text("".join(hari_list[15:]), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.effective_message.reply_text(f"📅 *{judul_text}*\n\n{''.join(hari_list)}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ==== Handler /jadwal (tanpa parameter) ====
async def jadwal_sholat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = buat_keyboard_huruf()
    
    await update.message.reply_text(
        "🕌 *JADWAL SHOLAT BULANAN* 🕌\n\n"
        "Silakan pilih huruf pertama dari nama wilayah yang Anda cari:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ==== Callback Handler untuk tombol-tombol ====
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("huruf:"):
        # User memilih huruf
        huruf = query.data.split(":")[1]
        keyboard = buat_keyboard_wilayah(huruf)
        
        await query.edit_message_text(
            f"🏙 *Wilayah yang dimulai dengan huruf '{huruf}'*\n\n"
            "Pilih wilayah yang Anda inginkan:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    elif query.data.startswith("wilayah:"):
        # User memilih wilayah
        kota = query.data.split(":")[1]
        await query.edit_message_text("🔄 Mengambil jadwal sholat, mohon tunggu...")
        await tampilkan_jadwal_sholat(update, context, kota)
    
    elif query.data == "kembali_huruf":
        # User kembali ke menu huruf
        keyboard = buat_keyboard_huruf()
        await query.edit_message_text(
            "🕌 *JADWAL SHOLAT BULANAN* 🕌\n\n"
            "Silakan pilih huruf pertama dari nama wilayah yang Anda cari:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    elif query.data.startswith("jadwalpdf:"):
        # User download PDF
        kota = query.data.split(":")[1]
        await query.edit_message_text("📄 Membuat PDF, mohon tunggu...")
        await kirim_jadwal_pdf(update, context, kota)

# Handler untuk kompatibilitas mundur (jika user masih menggunakan /jadwal {wilayah})
async def jadwal_sholat_legacy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        # Jika ada parameter, gunakan fungsi lama
        kota = " ".join(context.args).lower()
        
        if kota not in KOTA_ID:
            await update.message.reply_text(
                f"⚠️ Kota '{kota}' tidak tersedia.\n"
                "Gunakan /jadwal untuk memilih wilayah melalui menu."
            )
            return
        
        await tampilkan_jadwal_sholat(update, context, kota)
    else:
        # Jika tidak ada parameter, panggil handler baru
        await jadwal_sholat_handler(update, context)

# ==== Registrasi Handler ====
# Tambahkan ini ke aplikasi Telegram Bot Anda:
