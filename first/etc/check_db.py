import sqlite3
import pandas as pd

# 데이터베이스 파일 경로
db_path = 'object_detection.db'

# 데이터베이스 연결
conn = sqlite3.connect(db_path)

# 데이터베이스 내 테이블 목록 가져오기
tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql(tables_query, conn)
print("Tables in the database:")
print(tables)

# 각 테이블의 내용을 출력
for table_name in tables['name']:
    print(f"\nContents of table {table_name}:")
    table_query = f"SELECT * FROM {table_name};"
    table_contents = pd.read_sql(table_query, conn)
    print(table_contents)

# 데이터베이스 연결 종료
conn.close()
