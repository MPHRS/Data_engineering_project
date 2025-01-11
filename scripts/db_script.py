# Скрипт: db_script.py
import sqlite3
import pandas as pd
import argparse

def main(input_csv, db_file_path, table_name):
    # Чтение CSV файла
    df = pd.read_csv(input_csv)

    # Устанавливаем соединение с базой данных SQLite
    conn = sqlite3.connect(db_file_path)

    # Загружаем данные в таблицу
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"Данные успешно загружены в таблицу '{table_name}' базы данных '{db_file_path}'")

    # Закрываем соединение
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Загрузка CSV в SQLite")
    parser.add_argument("--input", required=True, help="Путь к входному CSV файлу")
    parser.add_argument("--db_file_path", required=True, help="Путь к SQLite базе данных")
    parser.add_argument("--table_name", required=True, help="Имя таблицы")

    args = parser.parse_args()
    main(args.input, args.db_file_path, args.table_name)