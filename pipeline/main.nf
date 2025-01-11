#!/usr/bin/env nextflow
params.dataset_name_1 = "stefanost/gene-promoter-sequences" // Название датасета
params.dataset_name_2 = "samira1992/promoter-or-not-bioinformatics-dataset" // Название датасета
params.dataset_name_3 = "nayanack/promoter-gene-prediction" // Название датасета

params.output_dir_kaggle = "./data/raw_data/kaggle_data"         // Папка для сохранения

params.kaggle_username = "miphares"                      // Имя пользователя Kaggle
params.kaggle_key = "52285bd03cf110ece44d5a924774d619"   // Ключ API Kaggle



process kaggledownloadData_1 {
    tag "Download ${params.dataset_name}"
    publishDir("${params.output_dir_kaggle}", mode: "copy")  // Указываем корректный путь

    input:
    tuple val(dataset_name), val(output_dir_kaggle), val(kaggle_username), val(kaggle_key)
    output:
    path("${dataset_name}"), emit: data_1

    script:
    """
    export KAGGLE_USERNAME=${kaggle_username}
    export KAGGLE_KEY=${kaggle_key}
    mkdir -p "${dataset_name}"
    kaggle datasets download -d "${dataset_name}" -p "${dataset_name}" --unzip
    """
}

process kaggledownloadData_2 {
    tag "Download ${params.dataset_name}"
    publishDir("${params.output_dir_kaggle}", mode: "copy")  // Указываем корректный путь

    input:
    tuple val(dataset_name), val(output_dir_kaggle), val(kaggle_username), val(kaggle_key)
    output:
    path("${dataset_name}"), emit: data_2

    script:
    """
    export KAGGLE_USERNAME=${kaggle_username}
    export KAGGLE_KEY=${kaggle_key}
    mkdir -p "${dataset_name}"
    kaggle datasets download -d "${dataset_name}" -p "${dataset_name}" --unzip
    """
}

process kaggledownloadData_3 {
    tag "Download ${params.dataset_name}"
    publishDir("${params.output_dir_kaggle}", mode: "copy")  // Указываем корректный путь

    input:
    tuple val(dataset_name), val(output_dir_kaggle), val(kaggle_username), val(kaggle_key)
    output:
    path("${dataset_name}"), emit: data_3

    script:
    """
    export KAGGLE_USERNAME=${kaggle_username}
    export KAGGLE_KEY=${kaggle_key}
    mkdir -p "${dataset_name}"
    kaggle datasets download -d "${dataset_name}" -p "${dataset_name}" --unzip
    # Переименовываем файл promoters.data в promoters_2.data
    if [ -f "${dataset_name}/promoters.data" ]; then
        mv "${dataset_name}/promoters.data" "${dataset_name}/promoters_2.data"
    fi
    """
}
// step2
params.script_path = "./scripts/combine.py"
params.output_dir_processed = "./data/processed"         // Папка для сохранения
// Создаём канал из относительного пути и преобразуем его в абсолютный

process combine_datasets {
    tag "Combine datasets"
    publishDir("${params.output_dir_processed}", mode: "copy") // Сохраняем результат в указанной папке

    input:
    tuple path(dataset_1), path(dataset_2), path(dataset_3), path(dataset_4)
    val nothing_1          // Путь до третьего датасета
    val nothing_2          // Путь до третьего датасета
    val nothing_3   
    path python_script     // Путь до третьего датасета

        // Путь до скрип
    output:
    path("combined_data.csv")  // Выходной файл с результатом

    script:
    """
    touch combined_data.csv
    python ${python_script} --input1 ${dataset_1} --input2 ${dataset_2} --input3 ${dataset_3} --input4 ${dataset_4} --output combined_data.csv
    """
}

params.script_path_clean = "./scripts/clean.py"
process clean_combined_dataset {
    tag "Clean combined dataset"
    publishDir("${params.output_dir_processed}", mode: "copy")

    input:
    path combined_data
    path python_cleaning_script

    output:
    path "cleaned_data.csv"
    path "clean_report.txt"

    script:
    """
    python ${python_cleaning_script} --input ${combined_data} --output cleaned_data.csv --report clean_report.txt
    """
}
params.visualizations_dir = "./visualiztions" 
params.analysis_script_path = "./scripts/analysis.py"
params.train_script_path = "./scripts/train_scr.py"
params.db_script_path = "./scripts/db_script.py"
process analyze_data {
    tag "Analyze data"
    publishDir("${params.visualizations_dir}", mode: "copy") // Сохраняем визуализации в указанной папке

    input:
    path cleaned_data       // Входной файл с очищенными данными
    path python_analysis_script // Скрипт для анализа

    output:
    path "*.png"            // Все созданные графики

    script:
    """
    touch t.png
    python ${python_analysis_script} --input ${cleaned_data}
    """
}
process train_model {
    tag "Train Model"
    publishDir("./model_output", mode: "copy") // Сохраняем результаты обучения в указанной папке

    input:
    path cleaned_data
    path train_script_path  // Путь к скрипту обучения

    output:
    path "model_architecture.json"    // JSON с архитектурой модели
    path "model_weights.pth"          // Веса модели
    path "training_report.txt"        // Отчёт о процессе обучения
    path "*.png"                      // График обучения (например, loss/accuracy по эпохам)

    script:
    """
    python ${train_script_path} --input ${cleaned_data} --output_dir ./model_output
    """
}
params.db_url = "sqlite:///mydatabase.db"  // Пример для SQLite
params.table_name = "promoter_data"        // Имя таблицы, в которую будут загружаться данные

process load_data_to_db {
    tag "Load data to database"
    publishDir("${params.output_dir_processed}", mode: "copy")

    input:
    path cleaned_data    // Очищенные данные
    path python_db_script  // Скрипт для загрузки в базу данных

    output:
    path "mydatabase.db"  // Файл базы данных SQLite

    script:
    """
    python ${python_db_script} --input ${cleaned_data} --db_file_path mydatabase.db --table_name ${params.table_name}
    """
}

// python3 ${script_ch}

workflow {
    kaggledownloadData_1(
        dataset_name: params.dataset_name_1,
        output_dir: params.output_dir_kaggle,
        kaggle_username: params.kaggle_username,
        kaggle_key: params.kaggle_key
    )
    kaggledownloadData_2(
        dataset_name: params.dataset_name_2,
        output_dir: params.output_dir_kaggle,
        kaggle_username: params.kaggle_username,
        kaggle_key: params.kaggle_key
    )
    kaggledownloadData_3(
        dataset_name: params.dataset_name_3,
        output_dir: params.output_dir_kaggle,
        kaggle_username: params.kaggle_username,
        kaggle_key: params.kaggle_key
    )


def target_files = [
    new File("${params.output_dir_kaggle}/nayanack/promoter-gene-prediction/promoters_2.data").absolutePath,
    new File("${params.output_dir_kaggle}/samira1992/promoter-or-not-bioinformatics-dataset/non_promoter.csv").absolutePath,
    new File("${params.output_dir_kaggle}/samira1992/promoter-or-not-bioinformatics-dataset/promoter.csv").absolutePath,
    new File("${params.output_dir_kaggle}/stefanost/gene-promoter-sequences/promoters.data").absolutePath
]
// target_files.each { println "File: $it" }
script_ch =  channel.fromPath(params.script_path)


    // Объединяем датасеты
combine_datasets(target_files,  kaggledownloadData_3.out.data_3,  kaggledownloadData_2.out.data_2,  kaggledownloadData_1.out.data_1, script_ch)
// Очищаем объединенный датасет
python_cleaning_script_path =  channel.fromPath(params.script_path_clean)

clean_combined_dataset(combine_datasets.out, python_cleaning_script_path)
analysis_script_path_ch =  channel.fromPath(params.analysis_script_path)

analyze_data(clean_combined_dataset.out[0], analysis_script_path_ch)

// train_model(clean_combined_dataset.out[0], train_script_path_ch)
// Загрузка в базу данных
python_db_script = channel.fromPath(params.db_script_path)

load_data_to_db(clean_combined_dataset.out[0], python_db_script)
}


