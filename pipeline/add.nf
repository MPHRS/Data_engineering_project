#!/usr/bin/env nextflow
params.dataset_name_1 = "stefanost/gene-promoter-sequences" // Название датасета
params.dataset_name_2 = "samira1992/promoter-or-not-bioinformatics-dataset" // Название датасета
params.dataset_name_3 = "nayanack/promoter-gene-prediction" // Название датасета

params.output_dir_kaggle = "./data/raw_data/kaggle_data"         // Папка для сохранения
params.script_path = "./scripts/combine.py"
params.output_dir_processed = "./data/processed" 
params.kaggle_username = "miphares"                      // Имя пользователя Kaggle
params.kaggle_key = "52285bd03cf110ece44d5a924774d619"   // Ключ API Kaggle

process kaggledownloadData_1 {
    tag "Download ${params.dataset_name_1}"
    publishDir("${params.output_dir_kaggle}", mode: "copy")

    input:
    val(dataset_name), val(output_dir_kaggle), val(kaggle_username), val(kaggle_key)

    output:
    path("${output_dir_kaggle}/${dataset_name}/*")  // Извлекаем все файлы из папки

    script:
    """
    export KAGGLE_USERNAME=${kaggle_username}
    export KAGGLE_KEY=${kaggle_key}
    mkdir -p "${output_dir_kaggle}/${dataset_name}"
    kaggle datasets download -d "${dataset_name}" -p "${output_dir_kaggle}/${dataset_name}" --unzip
    """
}
process combine_datasets {
    tag "Combine datasets"
    publishDir("${params.output_dir_processed}", mode: "copy")

    input:
    tuple path(dataset_1), path(dataset_2), path(dataset_3)

    output:
    path("combined_data.csv")  // Выходной файл с результатом

    script:
    """
    # Пример объединения (пока пустой, замените на реальную логику)
    touch combined_data.csv
    """
}

process kaggledownloadData_2 {
    tag "Download ${params.dataset_name_2}"
    publishDir("${params.output_dir_kaggle}", mode: "copy")

    input:
    val(dataset_name), val(output_dir_kaggle), val(kaggle_username), val(kaggle_key)

    output:
    path("${output_dir_kaggle}/${dataset_name}/*")  // Извлекаем все файлы из папки

    script:
    """
    export KAGGLE_USERNAME=${kaggle_username}
    export KAGGLE_KEY=${kaggle_key}
    mkdir -p "${output_dir_kaggle}/${dataset_name}"
    kaggle datasets download -d "${dataset_name}" -p "${output_dir_kaggle}/${dataset_name}" --unzip
    """
}

process kaggledownloadData_3 {
    tag "Download ${params.dataset_name_3}"
    publishDir("${params.output_dir_kaggle}", mode: "copy")

    input:
    val(dataset_name), val(output_dir_kaggle), val(kaggle_username), val(kaggle_key)

    output:
    path("${output_dir_kaggle}/${dataset_name}/*")  // Извлекаем все файлы из папки

    script:
    """
    export KAGGLE_USERNAME=${kaggle_username}
    export KAGGLE_KEY=${kaggle_key}
    mkdir -p "${output_dir_kaggle}/${dataset_name}"
    kaggle datasets download -d "${dataset_name}" -p "${output_dir_kaggle}/${dataset_name}" --unzip
    """
}
workflow {
    // Каналы для загрузки данных
    data_1 = kaggledownloadData_1(
        dataset_name: params.dataset_name_1,
        output_dir: params.output_dir_kaggle,
        kaggle_username: params.kaggle_username,
        kaggle_key: params.kaggle_key
    )

    data_2 = kaggledownloadData_2(
        dataset_name: params.dataset_name_2,
        output_dir: params.output_dir_kaggle,
        kaggle_username: params.kaggle_username,
        kaggle_key: params.kaggle_key
    )

    data_3 = kaggledownloadData_3(
        dataset_name: params.dataset_name_3,
        output_dir: params.output_dir_kaggle,
        kaggle_username: params.kaggle_username,
        kaggle_key: params.kaggle_key
    )

    // Объединяем датасеты
    combine_datasets(data_1, data_2, data_3)
}
