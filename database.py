import psycopg2

def get_db():
    return psycopg2.connect(
        host="dpg-d15ncqmuk2gs73fiulpg-a.oregon-postgres.render.com",
        database="halaqah",
        user="halaqah_user",
        password="Iep6nWQ2GMJ3wVL3ntqkYte352qX7tu1"
    )
