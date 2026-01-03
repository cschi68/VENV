import sqlite3

# 連接資料庫檔案
conn = sqlite3.connect('./db_bge_word/chroma.sqlite3')
cursor = conn.cursor()

# 執行查詢
try:
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("資料庫中的資料表:", tables)
finally:
    conn.close()