# README: Promoter Prediction Platform

## Описание проекта
Этот проект направлен на создание аналитической платформы для предсказания промоторных участков в последовательностях ДНК. Основная цель — собрать, обработать и проанализировать данные, а также обучить модель для идентификации промоторов. Пайплайн автоматизирует загрузку и обработку данных, а обучение модели и создание визуализаций выполняются отдельными скриптами. Проект реализован в рамках курса по Инжинирингу и управлению данными, где рассматриваются практические аспекты работы с данными и автоматизации процессов, но мною аспекты разработки аналитических решений для биоинформатики.
---

## Структура проекта
```plaintext
.
├── LICENSE
├── README.md
├── dashboard
│   └── data_analysis_metrics.csv
├── data
│   ├── processed
│   │   ├── clean_report.txt
│   │   ├── cleaned_data.csv
│   │   ├── combined_data.csv
│   │   ├── load_report.txt
│   │   └── mydatabase.db
│   └── raw_data
│       └── kaggle_data
│           ├── nayanack
│           │   └── promoter-gene-prediction
│           │       └── promoters_2.data
│           ├── samira1992
│           │   └── promoter-or-not-bioinformatics-dataset
│           │       ├── bendability.tsv
│           │       ├── non_promoter.csv
│           │       └── promoter.csv
│           └── stefanost
│               └── gene-promoter-sequences
│                   └── promoters.data
├── environment.yml
├── models
│   ├── best_model_weights.pth
│   ├── final_evaluation_report.txt
│   ├── training_loss.png
│   └── training_report.txt
├── pipeline
│   ├── main.nf
│   └── nextflow.config
├── scripts
│   ├── analysis.py
│   ├── clean.py
│   ├── combine.py
│   ├── dashboard.py
│   ├── db_script.py
│   └── train_scr.py
└── visualiztions
    ├── class_distribution.png
    ├── gc_content_distribution.png
    ├── kmer_heatmap.png
    ├── kmer_histogram.png
    ├── sequence_length_distribution.png
    └── t.png
```

---

## Требования
Для запуска проекта необходимо установить зависимости, указанные в `environment.yml`. Убедитесь, что у вас установлен `conda`.

### Установка зависимостей
```bash
conda env create -f environment.yml
conda activate promoter-env
```

---

## Запуск пайплайна
Пайплайн написан на Nextflow и автоматизирует сбор, обработку и анализ данных. Для запуска выполните следующие шаги:

1. **Инициализация Nextflow:**
   Убедитесь, что Nextflow установлен:
   ```bash
   curl -s https://get.nextflow.io | bash
   ```
2. **Запуск пайплайна:**
   ```bash
   nextflow run pipeline/main.nf
   ```
   
   ### Основные шаги пайплайна:
   - **Сбор данных:** Загружаются три датасета с Kaggle.
   - **Обработка данных:** Объединение, очистка и преобразование данных в единый формат.
   - **Анализ данных:** Генерация визуализаций для предварительного анализа.
   - **Загрузка в базу данных:** Обработанные данные сохраняются в SQLite для последующего использования.

Все файлы сохраняются в директории `data/processed`.

---

## Обучение модели
Для обучения модели выполните команду:
```bash
python scripts/train_scr.py --input ./data/processed/cleaned_data.csv --output_dir ./models
```

Выходные файлы будут сохранены в директории `models`:
- `model_architecture.json` — структура модели.
- `model_weights.pth` — веса модели.
- `training_report.txt` — отчёт об обучении.
- Графики обучения (например, `training_loss.png`).

---

## Создание дэшборда
Для генерации дэшборда выполните:
```bash
python scripts/dashboard.py --input ./data/processed/cleaned_data.csv --output ./dashboard
```
Дэшборд создаёт CSV-файл с ключевыми метриками и графиками, которые можно использовать для визуализации результатов анализа.

---

## Скрипты
- `combine.py`: Объединяет данные из разных источников.
- `clean.py`: Очищает и нормализует данные.
- `analysis.py`: Генерирует визуализации для анализа данных.
- `train_scr.py`: Обучение модели.
- `db_script.py`: Загружает данные в SQLite базу.
- `dashboard.py`: Создаёт отчёт о данных и визуализации для дэшборда.

---

## Дополнительно
- Все данные для обучения и анализа загружаются автоматически через пайплайн.
- Для использования скриптов требуется активация Conda-окружения: `conda activate promoter-env`.

При необходимости уточняйте или дорабатывайте под свои задачи.

