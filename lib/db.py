from database import get_db

def get_santri_terbanyak():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT nama, hafalan
        FROM santri
        ORDER BY hafalan DESC
        LIMIT 1
    """)
    result = cur.fetchone()
    cur.close()
    return result

def get_santri_dari_halaqah(nama_halaqah):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.nama
        FROM santri s
        JOIN halaqah h ON s.halaqah_id = h.id
        WHERE h.nama = ?
        ORDER BY s.nama ASC
    """, (nama_halaqah,))
    hasil = cur.fetchall()
    cur.close()
    return [row[0] for row in hasil]

def get_total_hafalan_santri(nama):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT hafalan
        FROM santri
        WHERE nama = ?
    """, (nama,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

def get_rekap_bulanan(bulan):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT nama_santri, SUM(hafalan_baru)
        FROM laporan_pekanan
        WHERE bulan = ?
        GROUP BY nama_santri
    """, (bulan,))
    hasil = cur.fetchall()
    cur.close()
    return hasil

def get_santri_by_ustadz(nama_ustadz):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.nama
        FROM santri s
        JOIN halaqah h ON s.halaqah_id = h.id
        WHERE h.ustadz = ?
        ORDER BY s.nama ASC
    """, (nama_ustadz,))
    hasil = cur.fetchall()
    cur.close()
    return [row[0] for row in hasil]

def cari_halaqah_terdekat(keyword):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nama FROM halaqah")
    semua = [row[0] for row in cur.fetchall()]
    cur.close()

    keyword = keyword.lower()
    for h in semua:
        if keyword in h.lower() or keyword.replace(" ", "_") in h.lower():
            return h
    return None

