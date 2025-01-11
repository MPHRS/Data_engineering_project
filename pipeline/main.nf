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
    tuple path(dataset_1), path(dataset_2), path(dataset_3)
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
    python ${python_script} --input1 ${dataset_1} --input2 ${dataset_2} --input3 ${dataset_3} --output combined_data.csv
    """
}
params.script_path_clean = "./scripts/clean.py"
process clean_combined_dataset {
    tag "Clean combined dataset"
    publishDir("${params.output_dir_processed}", mode: "copy") // Сохраняем результат в той же папке, что и объединенные данные

    input:
    path combined_data
    path python_cleaning_script

    output:
    path "cleaned_data.csv"  // Выходной файл с очищенными данными

    script:
    """
    touch cleaned_data.csv
    python ${python_cleaning_script} --input ${combined_data} --output cleaned_data.csv
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
    new File("${params.output_dir_kaggle}/nayanack/promoter-gene-prediction/promoters.data").absolutePath,
    new File("${params.output_dir_kaggle}/samira1992/promoter-or-not-bioinformatics-dataset/non_promoter.csv").absolutePath,
    new File("${params.output_dir_kaggle}/samira1992/promoter-or-not-bioinformatics-dataset/promoter.csv").absolutePath,
    new File("${params.output_dir_kaggle}/stefanost/gene-promoter-sequences/promoters.data").absolutePath
]
// target_files.each { println "File: $it" }
script_ch =  channel.fromPath(params.script_path)
// script_ch.view()

    // filesTuple = tuple(  kaggledownloadData_3.out.data_3,   kaggledownloadData_2.out.data_2,   kaggledownloadData_1.out.data_1) 
    // Объединяем датасеты
combine_datasets(target_files,  kaggledownloadData_3.out.data_3,  kaggledownloadData_2.out.data_2,  kaggledownloadData_1.out.data_1, script_ch)
// Очищаем объединенный датасет
python_cleaning_script_path =  channel.fromPath(params.script_path_clean)

clean_combined_dataset(combine_datasets.out, python_cleaning_script_path)
}


