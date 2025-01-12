import pandas as pd
import argparse
import re

def clean_data(input_file, output_file, report_file):
    print(f"Чтение данных из файла: {input_file}")
    data = pd.read_csv(input_file)

    
    if 'Sequence' not in data.columns or 'Promoter' not in data.columns:
        raise ValueError("Входной файл должен содержать столбцы 'Sequence' и 'Promoter'.")

   
    data['Sequence'] = data['Sequence'].str.replace(r'\s+', '', regex=True)


    data['Sequence'] = data['Sequence'].str.upper()


    valid_nucleotides = re.compile(r'^[ATCG]+$')
    data['is_valid'] = data['Sequence'].apply(lambda seq: bool(valid_nucleotides.match(seq)))
    invalid_count = len(data) - data['is_valid'].sum()
    data = data[data['is_valid']].drop(columns=['is_valid'])


    initial_count = len(data)

    data = data.drop_duplicates(subset=['Sequence'])


    final_count = len(data)

    data.to_csv(output_file, index=False)
    print(f"Очищенные данные сохранены в файл: {output_file}")


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
