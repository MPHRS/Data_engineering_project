import argparse

# Функция для обработки первого и четвертого файлов (promoter sequences)
def process_promoter_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    with open(output_file, 'a') as f_out:
        for line in lines:
            line = line.replace(" ", "").strip()  # Убираем пробелы
            parts = line.split(',')
            if parts[0] == '+':
                f_out.write(f"{parts[2]},1\n")  # Промотер (метка 1)
            elif parts[0] == '-':
                f_out.write(f"{parts[2]},0\n")  # Non-промотер (метка 0)

# Функция для обработки второго и третьего файлов (non-promoter sequences)
def process_non_promoter_file(input_file, output_file, label):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    with open(output_file, 'a') as f_out:
        for line in lines[1:]:  # Пропускаем первую строку
            line = line.replace(" ", "").strip()
            f_out.write(f"{line},{label}\n")  # Добавляем метку

# Основная функция
def main():
    # Создаем парсер для аргументов командной строки
    parser = argparse.ArgumentParser(description="Обработка метагеномных данных.")
    
    parser.add_argument('--input1', required=True, help="Путь к первому входному файлу (promoter sequences)")
    parser.add_argument('--input2', required=True, help="Путь ко второму входному файлу (non-promoter sequences)")
    parser.add_argument('--input3', required=True, help="Путь к третьему входному файлу (promoter sequences)")
    parser.add_argument('--input4', required=True, help="Путь к четвертому входному файлу (non-promoter sequences)")
    parser.add_argument('--output', required=True, help="Путь к итоговому файлу")

    args = parser.parse_args()
    with open(args.output, 'w') as f_out:
        f_out.write("Sequence,Promoter\n")  # Пе
    # Обработка файлов по очереди
    process_promoter_file(args.input1, args.output)  # Обрабатываем первый файл (promoter)
    process_non_promoter_file(args.input2, args.output, 0)  # Обрабатываем второй файл (non-promoter), метка 0
    process_non_promoter_file(args.input3, args.output, 1)  # Обрабатываем третий файл (promoter), метка 1
    process_promoter_file(args.input4, args.output)  # Обрабатываем четвертый файл (non-promoter)

if __name__ == "__main__":
    main()
