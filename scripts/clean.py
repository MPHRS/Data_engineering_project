import pandas as pd
import argparse
import re

def clean_data(input_file, output_file, report_file):
    # Загружаем данные
    print(f"Чтение данных из файла: {input_file}")
    data = pd.read_csv(input_file)

    # Проверяем наличие необходимых столбцов
    if 'Sequence' not in data.columns or 'Promoter' not in data.columns:
        raise ValueError("Входной файл должен содержать столбцы 'Sequence' и 'Promoter'.")

    # Удаляем пробелы из последовательностей
    data['Sequence'] = data['Sequence'].str.replace(r'\s+', '', regex=True)

    # Приводим последовательности к верхнему регистру
    data['Sequence'] = data['Sequence'].str.upper()

    # Проверяем последовательности на допустимые символы
    valid_nucleotides = re.compile(r'^[ATCG]+$')
    data['is_valid'] = data['Sequence'].apply(lambda seq: bool(valid_nucleotides.match(seq)))
    invalid_count = len(data) - data['is_valid'].sum()
    data = data[data['is_valid']].drop(columns=['is_valid'])

    # Сохраняем количество строк до удаления дубликатов
    initial_count = len(data)

    # Удаляем дубликаты
    data = data.drop_duplicates(subset=['Sequence'])

    # Сохраняем количество строк после удаления дубликатов
    final_count = len(data)

    # Сохраняем очищенные данные
    data.to_csv(output_file, index=False)
    print(f"Очищенные данные сохранены в файл: {output_file}")

    # Создаем отчет об очистке
    with open(report_file, 'w') as report:
        report.write(f"Отчет об очистке данных:\n")
        report.write(f"Исходное количество записей: {initial_count + invalid_count}\n")
        report.write(f"Удалено записей с недопустимыми символами: {invalid_count}\n")
        report.write(f"Количество записей после удаления недопустимых символов: {initial_count}\n")
        report.write(f"Количество уникальных записей: {final_count}\n")
        report.write(f"Удалено дубликатов: {initial_count - final_count}\n")
        print(f"Отчет об очистке сохранен в файл: {report_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Очистка данных для предсказания промотеров.")
    parser.add_argument('--input', required=True, help="Путь к входному CSV файлу.")
    parser.add_argument('--output', required=True, help="Путь к выходному очищенному CSV файлу.")
    parser.add_argument('--report', required=True, help="Путь к файлу отчета об очистке.")

    args = parser.parse_args()

    clean_data(input_file=args.input, output_file=args.output, report_file=args.report)
