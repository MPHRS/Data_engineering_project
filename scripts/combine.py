import argparse
import os
import pandas as pd


def process_promoters_data(file_path):
    """Обработка файлов .data с промотерами."""
    data = []
    with open(file_path, "r") as file:
        for line in file:
            # Удаляем все пробелы из строки
            line = line.replace(" ", "").strip()
            if not line:  # Пропускаем пустые строки
                continue
            parts = line.split(",")
            if len(parts) < 3:  # Пропускаем строки с недостаточным количеством частей
                print(f"Skipping malformed line: {line}")
                continue
            _, label, sequence = parts
            data.append({"Sequence": sequence, "Promoter": 1})  # Промоутеры
    return data



def process_non_promoters(file_path):
    """Обработка файлов с Non-promoters."""
    data = []
    with open(file_path, "r") as file:
        for line in file:
            if line.strip():
                data.append({"Sequence": line.strip(), "Promoter": 0})
    return data


def process_promoters_csv(file_path):
    """Обработка файлов .csv с промотерами и non-промотерами."""
    try:
        # Пытаемся прочитать файл с автоматическим разделителем
        df = pd.read_csv(file_path)
    except pd.errors.ParserError:
        # Если ошибка парсинга, пробуем разделитель табуляции
        df = pd.read_csv(file_path, delimiter="\t")

    # Поиск правильной колонки
    sequence_column = None
    for column in df.columns:
        if "Promoter sequences" in column or "non Promoter sequences" in column:
            sequence_column = column
            break

    if not sequence_column:
        raise ValueError(
            f"Не найдена подходящая колонка ('Promoter sequences' или 'non Promoter sequences') в файле {file_path}. "
            f"Доступные колонки: {list(df.columns)}"
        )

    # Определяем метку (1 для промотеров, 0 для non-промотеров)
    label = 1 if "Promoter" in sequence_column and "non" not in sequence_column else 0

    # Формируем список словарей с последовательностями и метками
    data = [{"Sequence": seq.strip(), "Promoter": label} for seq in df[sequence_column]]
    return data



def main():
    parser = argparse.ArgumentParser(description="Combine dataset files into a single CSV file.")
    parser.add_argument("--input1", required=True, help="Path to the .data file with promoters")
    parser.add_argument("--input2", required=True, help="Path to the .csv file with promoters")
    parser.add_argument("--input3", required=True, help="Path to the Non-promoters file")
    parser.add_argument("--output", required=True, help="Path to the output CSV file")

    args = parser.parse_args()

    # Обрабатываем все входные файлы
    data = []
    data.extend(process_promoters_data(args.input1))
    data.extend(process_promoters_csv(args.input2))
    data.extend(process_non_promoters(args.input3))

    # Создаем DataFrame и сохраняем его
    df = pd.DataFrame(data)
    df.to_csv(args.output, index=False)
    print(f"Combined data saved to {args.output}")


if __name__ == "__main__":
    main()
