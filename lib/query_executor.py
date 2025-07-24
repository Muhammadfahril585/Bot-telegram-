def eksekusi_query(json_instruksi):
    sheet = client.open("Database").worksheet(json_instruksi["sheet"])
    data = sheet.get_all_records()
    
    # Terapkan filter
    hasil = []
    for row in data:
        cocok = all(str(row.get(k, "")).lower() == v.lower() for k, v in json_instruksi.get("filter", {}).items())
        if cocok:
            baris = " | ".join(f"{col}: {row.get(col, '')}" for col in json_instruksi["columns"])
            hasil.append(baris)

    return hasil
